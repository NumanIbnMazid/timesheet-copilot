"""Small, explicit per-team settings. Paths belong to the profile, not the skill."""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TimesheetError(ValueError):
    """An actionable failure safe to show without credentials or response bodies."""


DAYS = dict(zip(("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"), range(7)))


def require(condition, message):
    if not condition:
        raise TimesheetError(message)


def keys(value, allowed, location):
    require(isinstance(value, dict), f"{location} must be an object.")
    require(not set(value) - set(allowed), f"Unknown settings in {location}; check the example profile.")


def string(value, location):
    require(isinstance(value, str) and bool(value.strip()), f"{location} must be non-empty text.")
    return value


def resolve_path(value, base):
    path = Path(value).expanduser()
    return (base / path).resolve() if not path.is_absolute() else path.resolve()


def load_profile(path):
    path = Path(path).expanduser().resolve()
    try:
        p = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise TimesheetError("Cannot read profile JSON. Check its path and JSON syntax.") from exc
    keys(p, {"version", "source", "pms", "timezone", "week_starts_on", "output_dir", "filename_prefix", "projects"}, "profile")
    require(type(p.get("version")) is int and p["version"] == 1, "Profile version must be 1.")
    require(p.get("source") == "pms", "Only the PMS source is supported today. Jira is not implemented yet.")
    api = p.get("pms")
    keys(api, {"base_url", "token_env", "token_file"}, "pms")
    try:
        origin = urlsplit(string(api.get("base_url"), "pms.base_url"))
        origin.port  # Validate malformed port numbers without ever making a request.
    except ValueError as exc:
        raise TimesheetError("pms.base_url is not a valid HTTPS origin.") from exc
    require(origin.scheme == "https" and origin.hostname and not origin.username and not origin.password
            and origin.path in ("", "/") and not origin.query and not origin.fragment,
            "pms.base_url must be an HTTPS origin, without a path, credentials or query.")
    api["base_url"] = api["base_url"].rstrip("/")
    require(not ("token_env" in api and "token_file" in api), "Choose token_env or token_file, not both.")
    if "token_file" in api:
        api["token_file"] = str(resolve_path(string(api["token_file"], "pms.token_file"), path.parent))
    else:
        api.setdefault("token_env", "PMS_TOKEN")
        require(isinstance(api["token_env"], str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", api["token_env"]),
                "pms.token_env must be an environment-variable name, not a token.")
    try:
        ZoneInfo(string(p.get("timezone"), "timezone"))
    except ZoneInfoNotFoundError as exc:
        raise TimesheetError("Unknown timezone. Use an IANA name such as Asia/Dhaka or Europe/London.") from exc
    require(isinstance(p.get("week_starts_on"), str) and p["week_starts_on"] in DAYS,
            "week_starts_on must be a lowercase weekday name.")
    p["output_dir"] = str(resolve_path(string(p.get("output_dir"), "output_dir"), path.parent))
    prefix = p.setdefault("filename_prefix", "")
    require(isinstance(prefix, str), "filename_prefix must be text.")
    require(isinstance(p.get("projects"), list) and p["projects"], "Configure at least one project.")
    seen_keys, seen_ids, seen_names = set(), set(), set()
    for project in p["projects"]:
        keys(project, {"key", "id", "name", "label", "active"}, "project")
        key = string(project.get("key"), "project.key")
        require(len(key) <= 64 and re.fullmatch(r"[a-z0-9][a-z0-9-]*", key),
                "Project keys use at most 64 lowercase letters, numbers and hyphens.")
        require(type(project.get("id")) is int and project["id"] > 0, "PMS project IDs must be positive integers.")
        name = string(project.get("name"), "project.name")
        string(project.setdefault("label", name), "project.label")
        require(type(project.setdefault("active", True)) is bool, "project.active must be true or false.")
        require(key not in seen_keys and project["id"] not in seen_ids and name not in seen_names,
                "Project keys, PMS IDs and source names must each be unique.")
        seen_keys.add(key)
        seen_ids.add(project["id"])
        seen_names.add(name)
    return p


def select_projects(profile, requested=None):
    if requested:
        requested = list(dict.fromkeys(requested))
        by_key = {p["key"]: p for p in profile["projects"]}
        require(all(key in by_key for key in requested), "Unknown project key. Run the check command to see configured projects.")
        return [by_key[key] for key in requested]
    result = [p for p in profile["projects"] if p["active"]]
    require(result, "No active projects. Choose a project explicitly or update the profile.")
    return result


def period(profile, start=None, end=None, today=None):
    require(bool(start) == bool(end), "Provide both --start and --end, or omit both for last week.")
    if start:
        try:
            first, last = date.fromisoformat(start), date.fromisoformat(end)
        except ValueError as exc:
            raise TimesheetError("Dates must use YYYY-MM-DD.") from exc
        require(first <= last, "The end date must be on or after the start date.")
        return first, last
    today = today or datetime.now(ZoneInfo(profile["timezone"])).date()
    this_week = today - timedelta(days=(today.weekday() - DAYS[profile["week_starts_on"]]) % 7)
    return this_week - timedelta(days=7), this_week - timedelta(days=1)


def week_segments(first, last, week_start):
    while first <= last:
        boundary = first + timedelta(days=6 - (first.weekday() - DAYS[week_start]) % 7)
        end = min(last, boundary)
        yield first, end
        first = end + timedelta(days=1)
