#!/usr/bin/env python3
"""Assistant-facing entrypoint; users ask for timesheets in normal language."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from config import TimesheetError, load_profile, period, require, select_projects
from pms import PMS
from report import validate
from workbook import write_workbook

SKILL = Path(__file__).resolve().parents[1]


def safe_name(value):
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", value).strip(" .")
    return value[:100].rstrip(" .") or "Timesheet"


def prepare(profile, project, first, last, csv_text, controls=None, source="downloaded PMS export"):
    report = validate(csv_text, project["name"], first, last, controls)
    output = Path(profile["output_dir"])
    output.mkdir(parents=True, exist_ok=True)
    filename = safe_name(" ".join(x for x in (profile["filename_prefix"], project["label"]) if x))
    filename += f"_timesheet_{first:%Y%m%d}_{last:%Y%m%d}.xlsx"
    # Every run gets a fresh directory, preserving earlier reviewed workbooks.
    destination = output / f"{project['key']}_{first:%Y%m%d}_{last:%Y%m%d}_{uuid4().hex[:10]}"
    with tempfile.TemporaryDirectory(prefix=".timesheet-", dir=output) as temp:
        temp = Path(temp)
        write_workbook(report, temp / filename, first)
        (temp / "source.csv").write_text(csv_text, encoding="utf-8", newline="")
        summary = {
            "project": project["name"], "project_key": project["key"], "pms_project_id": project["id"],
            "start": str(first), "end": str(last), "entries": len(report.entries),
            "total_minutes": report.total_minutes, "hours": f"{report.total_minutes // 60}h {report.total_minutes % 60:02d}m",
            "verification": "PMS total matched" if controls is not None else "CSV consistency checked; PMS total not checked",
            "warnings": report.warnings, "controls": controls,
            "source": source, "source_sha256": hashlib.sha256(csv_text.encode("utf-8")).hexdigest(),
            "generated_at": datetime.now(timezone.utc).isoformat(), "workbook": str(destination / filename),
        }
        (temp / "verification.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        temp.rename(destination)
    return summary


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Copy fictional starter settings without overwriting a profile")
    init.add_argument("--profile", required=True)
    check = commands.add_parser("check", help="Validate profile and show configured project scope; no network")
    check.add_argument("--profile", required=True)
    for command in ("fetch", "format"):
        run = commands.add_parser(command, help="Fetch PMS data" if command == "fetch" else "Format an already downloaded PMS CSV")
        run.add_argument("--profile", required=True)
        run.add_argument("--project", action="append", required=command == "format", help="Configured project key; repeat for fetch")
        run.add_argument("--start")
        run.add_argument("--end")
        if command == "format":
            run.add_argument("--csv", required=True)
            run.add_argument("--expected-total-minutes", type=int)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            path = Path(args.profile).expanduser().resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as f:
                f.write((SKILL / "examples/profile.example.json").read_text(encoding="utf-8"))
            print(json.dumps({"profile": str(path), "next": "Replace fictional PMS URL and project with your own; confirm timezone, week start and output folder."}, indent=2))
            return 0
        profile = load_profile(args.profile)
        if args.command == "check":
            first, last = period(profile)
            print(json.dumps({"source": profile["source"], "projects": profile["projects"], "last_week": [str(first), str(last)],
                              "output_dir": profile["output_dir"], "access": "Not checked; use browser export or fetch."}, indent=2))
            return 0
        projects = select_projects(profile, args.project)
        first, last = period(profile, args.start, args.end)
        results, errors = [], []
        if args.command == "format":
            require(len(projects) == 1, "Format accepts one project and one CSV at a time.")
            total = args.expected_total_minutes
            require(total is None or total >= 0, "Expected total minutes cannot be negative.")
            controls = None if total is None else [{"start": str(first), "end": str(last), "minutes": total}]
            with Path(args.csv).expanduser().open(encoding="utf-8-sig", newline="") as source_file:
                csv_text = source_file.read()
            results.append(prepare(profile, projects[0], first, last, csv_text, controls))
        else:
            require("example.com" not in profile["pms"]["base_url"], "Replace the fictional PMS URL before fetching.")
            api = PMS(profile["pms"])
            for project in projects:
                try:
                    csv_text, controls = api.fetch(project["id"], first, last, profile["week_starts_on"])
                    results.append(prepare(profile, project, first, last, csv_text, controls, "PMS API"))
                except TimesheetError as exc:
                    errors.append({"project": project["key"], "error": str(exc)})
        print(json.dumps({"results": results, "errors": errors}, indent=2))
        return 1 if errors else 0
    except (TimesheetError, OSError, UnicodeError) as exc:
        # Avoid dumping tracebacks, source rows, token contents or HTTP bodies.
        message = str(exc) if isinstance(exc, TimesheetError) else "A local file could not be read or written. Check paths, permissions, encoding, and whether the profile already exists."
        print(json.dumps({"error": message}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
