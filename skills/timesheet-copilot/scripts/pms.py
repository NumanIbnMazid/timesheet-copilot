"""Read-only adapter for the Enosis-compatible PMS API described in pms.md."""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from config import TimesheetError, require, week_segments

MAX_BYTES = 25 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    # Authentication must never follow a login redirect or another origin.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def credential(settings):
    if "token_file" in settings:
        path = Path(settings["token_file"])
        try:
            if os.name == "posix":
                require(not (stat.S_IMODE(path.stat().st_mode) & 0o077),
                        "PMS token file must be private (permissions 600).")
            token = path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise TimesheetError("Cannot read the configured PMS token file. Use the browser export route or repair credential access.") from exc
    else:
        token = os.environ.get(settings.get("token_env", "PMS_TOKEN"), "").strip()
    require(token and not any(c.isspace() for c in token),
            "PMS API credential is unavailable or invalid. Sign in and export through the browser, or configure a credential outside chat.")
    return token


class PMS:
    def __init__(self, settings):
        self.base_url = settings["base_url"]
        self._token = credential(settings)
        self._opener = build_opener(NoRedirect())

    def get(self, endpoint, params):
        request = Request(self.base_url + endpoint + "?" + urlencode(params),
                          headers={"Authorization": "Bearer " + self._token, "Accept": "text/csv, application/json"})
        try:
            with self._opener.open(request, timeout=45) as response:
                data = response.read(MAX_BYTES + 1)
        except HTTPError as exc:
            if exc.code in (401, 403):
                raise TimesheetError("PMS denied access. Sign in again or use the browser export route.") from None
            raise TimesheetError(f"PMS request failed (HTTP {exc.code}). No timesheet was verified; retry after resolving PMS access.") from None
        except (URLError, TimeoutError, OSError):
            raise TimesheetError("PMS could not be reached. Check the connection or use a downloaded export.") from None
        require(len(data) <= MAX_BYTES, "PMS export is too large. Request a shorter date range.")
        try:
            return data.decode("utf-8-sig")
        except UnicodeError as exc:
            raise TimesheetError("PMS returned an unsupported encoding. Export a UTF-8 CSV through the browser.") from exc

    def fetch(self, project_id, first, last, week_start):
        csv_text = self.get("/api/timesheets/export", {
            "startDate": first.isoformat(), "endDate": last.isoformat(),
            "projectIds": str(project_id), "memberIds": "", "activityIds": "", "exportType": "project_timesheet",
        })
        controls = []
        # weeklyTotalInMinute is a weekly control, not a documented range grand total.
        for start, end in week_segments(first, last, week_start):
            raw = self.get("/api/timesheets", {
                "startDate": start.isoformat(), "endDate": end.isoformat(),
                "pageNumber": "1", "includeFilters": "true", "projectId": str(project_id),
            })
            try:
                payload = json.loads(raw)
            except ValueError:
                raise TimesheetError("PMS returned an invalid total response. Re-export or inspect the PMS total.") from None
            minutes = payload.get("weeklyTotalInMinute") if isinstance(payload, dict) else None
            require(type(minutes) is int and minutes >= 0,
                    "PMS response is missing a valid weeklyTotalInMinute. Missing totals are not zero.")
            controls.append({"start": start.isoformat(), "end": end.isoformat(), "minutes": minutes})
        return csv_text, controls
