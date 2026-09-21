---
name: timesheet-copilot
description: Prepare checked Excel timesheets from PMS for selected projects and dates, including weekly or multi-week runs and downloaded PMS CSVs. Also use to set up project settings or draft a timesheet email when requested. PMS only for now; does not enter or change work logs.
---

# Timesheet Copilot

Prepare one readable `.xlsx` per project, preserving the PMS work descriptions,
dates, people and hours. Keep the workflow conversational. Run the supplied
helper rather than rewriting a formatter in scratch code.

## First use

Check prerequisites before claiming the workflow is ready: Python 3.10+ with the
skill's dependencies, file read/write access, the PMS address and project export
permissions, and one usable data route. Browser export requires the user to sign
in in a browser session this host can control, including MFA/VPN when required.
Direct API access requires a separately configured valid token. A supplied CSV
can be formatted offline. A login in another browser, a profile check, or the
fictional demo does not establish live PMS access. Read
[pms.md](references/pms.md) and guide the user through the selected route. If a
prerequisite is missing, name the specific action needed and continue independent
setup or the demo; do not attempt a live fetch without its required access.

Find the profile named by the user or current project instructions. If none is
configured, inspect the provided PMS project pages/export for names and IDs.
Ask only for missing scope, timezone/week start and destination. Do not assume a
particular client, team, sender, email recipients or set of active projects.

Create a private `profile.json` outside the skill using `scripts/timesheet.py init`,
then replace the fictional values. `examples/profile.example.json` documents the
small set of settings. Ask where to put it when that cannot be inferred. Use
`check` to show the resolved output folder, dates and project list. A successful
profile check does not prove access to PMS.

Use Python 3.10+ with the skill's `requirements.txt`. Prefer an isolated existing
environment or create a virtual environment outside the installed skill. Read
[commands.md](references/commands.md) for exact commands and the fictional demo.
The demo may run before a real profile is ready.

## Prepare timesheets

1. Resolve the period once. Explicit dates win; otherwise use the previous
   complete week from the profile's timezone and `week_starts_on`. State exact
   dates and scope without requesting redundant confirmation. Explicitly selected
   projects win; otherwise use configured `active: true` projects. The active list
   is a user-maintained allowlist, not a claim about current PMS status.
2. Read [pms.md](references/pms.md). Use an existing approved API credential with
   `fetch`, or use the signed-in browser's Export control and `format`. Do not
   extract tokens from browser storage, infer API credentials, or print secrets.
   If a file is already supplied, read its Project column rather than guessing
   identity from its download name. Confirm the requested export covers all
   members and activities. Do not include additional projects automatically.
3. Run the helper. It checks dates, project identity, whole-minute values,
   detail/subtotal arithmetic and independent PMS controls when supplied. A mismatch
   requires a source repair or fresh export, never edited hours. Partial batch
   failures must be named; deliver valid projects without calling the whole run complete.
4. Inspect the generated workbook. It wraps all cells, sizes columns and rows,
   styles total rows, freezes the heading and reads saved values back. Visually
   inspect a preview when the host has one, especially long descriptions. Do not
   claim a visual or native Excel check if only structural read-back ran. If the
   helper rejects an overlong row, agree an alternate layout; do not truncate it.
5. Link the workbook and report its project, exact dates and total. Distinguish
   “PMS total matched” from “CSV consistency checked; PMS total not checked”.
   Mention warnings and access failures. Keep raw exports and verification files
   in the run folder; never delete the user's original downloads.

The helper creates a separate output folder each run. Do not overwrite reviewed
files, silently skip empty projects, invent time entries, or treat missing data
as zero. Do not change descriptions to make them sound more impressive.

## Optional email

Prepare email only when requested. A timesheet request by itself requires the
workbook, not mailbox access. Read [email.md](references/email.md) when drafting.
Use the user's recipients and wording or explicitly authorized reference email.
Complete and verify the draft attachment. Send only when explicitly instructed.

## Boundaries

Only the PMS API/export contract in [pms.md](references/pms.md) is implemented.
For another source, explain that an adapter is needed; do not treat unrelated
Jira CSVs as PMS exports.
No KPI scoring, scheduling, PMS writes, or mail-provider integration is bundled.
