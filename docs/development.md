# Development and verification

The product is one portable skill with a small Python helper. It deliberately
has no service, database, MCP server, scheduler or mail integration. Real settings
and outputs live outside the repository. `examples/` contains only fictional data.

## Layout

- `config.py`: settings, project selection and local calendar periods.
- `pms.py`: read-only PMS HTTP adapter and independent total controls.
- `report.py`: PMS CSV parser and arithmetic/scope validation.
- `workbook.py`: source-preserving Excel presentation and saved-file read-back.
- `timesheet.py`: four commands (`init`, `check`, `fetch`, `format`) and output handling.

The formatter extends the original skill's Python/openpyxl approach, with one
maintained implementation. There is no instruction to bypass it with a second
scratch formatter. Dates stay in the source's text layout; numeric time columns
remain integers. The workbook is a static report, not a second timesheet editor.

## Add another source later

Add a source adapter and parser that returns the existing `Report` structure:
seven presentation columns, detail entries containing a Python `date` and integer
`minutes`, total minutes, subtotal row indexes and warnings. Preserve evidence of
source identity and period filtering. Keep fetch/auth, source-specific parsing
and shared workbook formatting separate. Relax `source` validation only when the
new adapter is implemented and tested.

For Jira, fetch actual worklogs (not estimates), resolve the requested timezone,
handle worklog pagination/permissions and date filtering, and identify projects
by stable IDs. Define how seconds are represented before converting to the
current whole-minute format. Do not round silently or route arbitrary CSVs into
the PMS parser. A plugin can package the same skill later without moving the
user's settings or adding a new engine.

## Local checks

From the repository root, in an isolated Python 3.10+ environment:

```sh
python -m pip install -r skills/timesheet-copilot/requirements.txt
python -m unittest discover -s tests -v
```

The tests use fictional exports and mocked PMS responses. They exercise calendar
boundaries, project isolation, time reconciliation, missing/invalid controls,
HTTP/auth failures, literal spreadsheet text, long-cell handling, saved-file
read-back, CLI output, and reruns that preserve previous results. No production
credentials or real work logs are required.

## Acceptance boundaries

Local tests establish helper behavior against the documented contract. They do
not prove a current live PMS deployment, browser download, mail attachment, or
every assistant's skill installation. The shipped adapter is based on the API
contract in the supplied original skill. Before a team's first production run,
compare a real project and date range with the visible PMS report. Check long
descriptions in their usual spreadsheet viewer. Native rendering can vary by
installed fonts and viewer.

GitHub Actions runs the same tests when available. A local pass is not a CI pass.
Keep any CI billing/access failure distinct from test failures and live acceptance.
