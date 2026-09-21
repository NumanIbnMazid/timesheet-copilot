"""Validate PMS detail and subtotal rows without rewriting source facts."""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from config import TimesheetError, require

HEADER = ["Date", "Project", "Activity", "Description", "Hours", "Minutes", "Resource"]
DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%A, %B %d, %Y", "%A, %d %B, %Y", "%A, %d %B %Y", "%A, %m/%d/%Y")


@dataclass
class Report:
    rows: list
    entries: list
    total_minutes: int
    subtotal_rows: list
    warnings: list


def parse_date(value, row):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            pass
    raise TimesheetError(f"CSV row {row}: unrecognized date. Use the original PMS export; do not guess its locale.")


def number(value, row, label):
    require(bool(re.fullmatch(r"\d+", value.strip())), f"CSV row {row}: {label} must be a non-negative whole number.")
    return int(value)


def validate(csv_text, project_name, first, last, controls=None):
    try:
        rows = list(csv.reader(io.StringIO(csv_text.lstrip("\ufeff")), strict=True))
    except csv.Error as exc:
        raise TimesheetError("Invalid CSV. Download the official PMS export again.") from exc
    require(rows and [v.strip() for v in rows[0]] == HEADER,
            "Unexpected PMS CSV header. Expected Date, Project, Activity, Description, Hours, Minutes, Resource.")
    output = [HEADER.copy()]
    entries, subtotals, warnings = [], [], []
    current_date = None
    day_sum = week_sum = 0
    day_open = week_open = False
    daily_count = weekly_count = 0
    previous_date = None
    for row_num, raw in enumerate(rows[1:], 2):
        if not any(v.strip() for v in raw):
            output.append([""] * 7)
            continue
        require(len(raw) == 7, f"CSV row {row_num}: expected exactly seven columns; no columns were discarded.")
        values = [v.strip() for v in raw]
        day, project, activity, description, hours, minutes, resource = values
        for cell in raw:
            require(len(cell) <= 32767, f"CSV row {row_num}: text exceeds Excel's cell limit.")
            require(not re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", cell), f"CSV row {row_num}: unsupported control character.")
        is_total = description in ("Total", "Weekly Total") and not resource and not activity
        if is_total:
            amount = number(hours, row_num, "Hours") * 60 + number(minutes, row_num, "Minutes")
            require(int(minutes) < 60, f"CSV row {row_num}: Minutes must be between 0 and 59.")
            require(not project or project == project_name, f"CSV row {row_num}: subtotal belongs to another project.")
            if description == "Total":
                require(day_open, f"CSV row {row_num}: daily total has no preceding entries.")
                if day:
                    require(parse_date(day, row_num) == current_date, f"CSV row {row_num}: daily total date does not match its entries.")
                require(amount == day_sum, f"CSV row {row_num}: daily total does not match detail minutes ({amount} versus {day_sum}).")
                daily_count += 1
                day_sum, day_open, current_date = 0, False, None
            else:
                require(week_open or (not entries and amount == 0 and weekly_count == 0), f"CSV row {row_num}: duplicate or misplaced weekly total.")
                require(amount == week_sum, f"CSV row {row_num}: weekly total does not match detail minutes ({amount} versus {week_sum}).")
                if day_open:
                    warnings.append("Some days have no CSV subtotal; their detail minutes were still included.")
                weekly_count += 1
                week_sum, week_open = 0, False
                day_sum, day_open, current_date = 0, False, None
            subtotals.append(len(output) + 1)
        else:
            require(project == project_name, f"CSV row {row_num}: Project does not match the configured PMS name. Check the export and profile.")
            require(resource, f"CSV row {row_num}: a work entry is missing its Resource.")
            parsed = parse_date(day, row_num) if day else current_date
            require(parsed is not None, f"CSV row {row_num}: a work entry has no date to inherit.")
            require(first <= parsed <= last, f"CSV row {row_num}: work date is outside the requested range.")
            require(previous_date is None or parsed >= previous_date, f"CSV row {row_num}: dates are out of order; inspect the export.")
            if day_open and parsed != current_date:
                warnings.append("Some days have no CSV subtotal; their detail minutes were still included.")
                day_sum = 0
            current_date = previous_date = parsed
            amount = number(hours, row_num, "Hours") * 60 + number(minutes, row_num, "Minutes")
            require(int(minutes) < 60, f"CSV row {row_num}: Minutes must be between 0 and 59.")
            day_sum += amount
            week_sum += amount
            day_open = week_open = True
            entries.append({"date": parsed, "minutes": amount})
        # Preserve every source text cell exactly; only numeric fields are typed.
        output.append(raw[:4] + [int(hours), int(minutes), raw[6]])
    total = sum(e["minutes"] for e in entries)
    require(entries or controls is not None,
            "Export has no work entries. Confirm a zero total in PMS and supply it explicitly; an empty export alone does not prove zero work.")
    if not daily_count:
        warnings.append("No daily CSV subtotals were available.")
    elif day_open:
        warnings.append("Some days have no CSV subtotal; their detail minutes were still included.")
    if not weekly_count or week_open:
        warnings.append("Some or all work entries have no weekly CSV subtotal.")
    if controls is None:
        warnings.append("No independent PMS total was supplied; only CSV consistency was checked.")
    else:
        covered = []
        for control in controls:
            start, end = date.fromisoformat(control["start"]), date.fromisoformat(control["end"])
            require(type(control["minutes"]) is int and control["minutes"] >= 0, "Control totals must be non-negative integer minutes.")
            covered.append((start, end))
            actual = sum(e["minutes"] for e in entries if start <= e["date"] <= end)
            require(actual == control["minutes"], f"PMS total mismatch for {start} to {end}: export {actual} minutes, PMS {control['minutes']} minutes. Re-export; do not edit hours.")
        cursor = first
        for start, end in sorted(covered):
            require(start == cursor and start <= end <= last, "Control total ranges must cover the requested dates exactly, without overlaps or gaps.")
            cursor = end + timedelta(days=1)
        require(cursor == last + timedelta(days=1), "PMS control totals do not cover the full requested range.")
    return Report(output, entries, total, subtotals, list(dict.fromkeys(warnings)))
