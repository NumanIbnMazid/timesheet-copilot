# Commands for the assistant

Run from the skill folder, or replace script paths with absolute paths. `python`
means the Python 3.10+ interpreter where requirements were installed. Do not
make the user repeat these steps each week.

## Install dependencies and try fictional data

Create an isolated environment in a writable working folder, then install:

```sh
python -m pip install -r /path/to/timesheet-copilot/requirements.txt
```

Copy `examples/profile.example.json` to a temporary demo folder as `profile.json`.
The example's relative output folder will then live beside that copy. Run:

```sh
python scripts/timesheet.py format --profile /path/to/demo/profile.json \
  --project atlas --csv examples/pms-export.csv \
  --start 2026-09-13 --end 2026-09-19 --expected-total-minutes 275
```

Expected: three entries, 4h 35m, matching control total and one readable workbook.
The control is fictional demo data, not a live PMS check. Do not fetch from the
example URL. No live account is required for the demo.

## Set up and check

```sh
python scripts/timesheet.py init --profile /path/to/private/profile.json
python scripts/timesheet.py check --profile /path/to/private/profile.json
```

`init` never overwrites an existing file. Edit the copy with the user's PMS origin,
exact project names/IDs, output location and week settings before using it.
`label` affects the filename only; `name` must match the PMS Project column.
PMS IDs and keys must be unique. Dates use `YYYY-MM-DD`.

## Get directly from PMS

```sh
python scripts/timesheet.py fetch --profile /path/to/private/profile.json
python scripts/timesheet.py fetch --profile /path/to/private/profile.json \
  --project atlas --project another-project --start 2026-09-01 --end 2026-09-15
```

Omitted dates mean the previous complete week, not a rolling seven days. Omitted
projects mean configured active projects. Explicit project selection can include
an inactive project for historical reporting. Fetch is read-only and uses the
credential source configured under `pms`. It never reads a `.env` file implicitly.

## Use a downloaded export

```sh
python scripts/timesheet.py format --profile /path/to/private/profile.json \
  --project atlas --csv /path/to/download.csv --start 2026-09-13 --end 2026-09-19 \
  --expected-total-minutes 275
```

Get the control total from PMS for the same project/date range and all
members/activities. Do not derive `--expected-total-minutes` from the CSV itself
and call it independent verification. Omit it if unavailable; output then says
PMS was not independently checked. A zero-entry export requires an explicit
confirmed zero control. Format handles one project/file at a time.

## Results and errors

The command prints JSON with `results` and `errors`. Each success includes the
workbook path, total, dates, verification level and warnings. A nonzero exit code
means at least one failure. A multi-project fetch keeps valid outputs and names
failed projects. Do not discard successful results or suppress the failures.

Each run folder has the workbook, `source.csv`, and `verification.json`. The
record includes controls and a SHA-256 of the saved UTF-8 source text, not the
original HTTP transport bytes. Reruns use new folders. Failed formatting does
not leave a completed-looking workbook behind.
