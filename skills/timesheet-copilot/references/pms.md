# PMS access and export contract

This adapter targets the PMS API and CSV contract documented below. The website
address is configurable; this is not an integration with every product called
PMS. Validate a real run before claiming acceptance on a new deployment.

## Browser export: no API credential setup

Check that the host can control a browser and access its downloads. Open the
user's PMS website in that browser and have the user sign in there, complete MFA,
and connect to a work VPN if needed. Do not assume a login in a different browser
or profile is available to this host. Confirm the visible project and Export
control before proceeding; missing permissions require the PMS administrator.
For a configured project, navigate to:

`<base_url>/all-projects/<project_id>/timesheet/weekly`

Set the exact start/end dates and all members/activities, inspect the visible
project/date range, and click Export. Read the page's total when available.
Use `format` with the downloaded CSV and that total in minutes. If browser
controls or downloads are unavailable, request the user's downloaded export.
Do not invent a specific browser tool name or use hidden browser APIs.

PMS downloads may share the same filename. Identify a CSV by its contents, not
by suffixes such as `(1)` or `(2)`. A download name is not proof of project or
date scope. A limited member/activity filter can produce an internally
consistent but incomplete export; inspect the filters and compare with PMS.

## Direct API: existing approved credential

Browser sign-in does not authenticate this helper. Direct API requests require
a valid bearer access token supplied separately. Ask the user to obtain it from
their PMS administrator or documented team process. Do not invent a token-issuing
screen or endpoint. This skill does not obtain or renew tokens. If API access is
unavailable, use browser export or a downloaded CSV.

### Credential setup

The helper accepts an environment variable named by `pms.token_env` (default
`PMS_TOKEN`) **or** `pms.token_file`, a path to a plain token stored outside the
skill/repository. Configure one, not both. For a token file on POSIX, permissions
must exclude group/other access (normally `600`). On other systems use an
appropriately restricted file ACL. The profile holds the path, never the token.

For the simplest persistent local setup:

1. Choose a private location with the user, outside the skill/repository and
   accessible to the helper. Create an empty plain-text file with owner-only
   permissions, without overwriting an existing credential. On POSIX, create it
   with mode `600`; on Windows, restrict its ACL to the user's account.
2. Have the user open it themselves, paste the complete token alone, and save.
   Do not request or display its contents. Do not include `Bearer`, quotes,
   username/password pairs, or JSON in the token file.
3. Set `pms.token_file` to that file's path and remove `pms.token_env`. For example:

   ```json
   "pms": {
     "base_url": "https://pms.example.com",
     "token_file": "~/private-timesheets/pms-token.txt"
   }
   ```

   This is the `pms` section of the user's profile. Use their actual PMS address
   and file location. Paths are resolved relative to the profile unless absolute
   or starting with `~`.
4. After the user says it is saved, use the helper to fetch one explicitly
   selected project/date range and compare with PMS. Never inspect the token
   yourself to check that it was saved. The helper reads it internally.

For an IT-managed environment, keep `"token_env": "PMS_TOKEN"` instead. The
variable must be supplied to the process that actually runs the helper. Setting
it in an unrelated terminal does not give it to an already running desktop
assistant. A `.env` file is not loaded automatically. Ask IT to configure the
host's secret/environment support, or use the token file method.

The `check` command validates settings only; it makes no network request and
does not validate credentials. An API 401/403 means the user must renew the token
or check its project/export permissions, or switch to browser export. A browser
login alone does not update the configured API token.

Use the user's approved credential/secret-management workflow. Do not ask them
to paste tokens in chat, inspect browser storage, scrape a password manager,
or echo credentials for troubleshooting. If no approved credential is available,
use the browser route. A read-only report operation does not make the underlying
bearer credential itself read-only; limit access using the provider's controls.

The helper issues GET requests only, using `Authorization: Bearer …`. It requires
HTTPS, refuses redirects, uses a 45-second request timeout, limits responses to
25 MiB, and reports errors without HTTP bodies or auth headers. It does not
retry login failures or follow login redirects.

### Export

`GET /api/timesheets/export`

Parameters: `startDate`, `endDate` (inclusive ISO dates), `projectIds` (one numeric
ID), empty `memberIds` and `activityIds`, `exportType=project_timesheet`.

### Independent total

`GET /api/timesheets`

Parameters: `startDate`, `endDate`, `pageNumber=1`, `includeFilters=true`,
`projectId` (one ID). Required response field: `weeklyTotalInMinute`, a
non-negative integer. Missing, null, malformed or inaccessible totals fail the
fetch; none is treated as zero. The field is used as a control, not as a list of
work records, so no detail-page pagination is inferred from it.

For longer date ranges, request a control for each configured week segment and
reconcile each segment separately. Partial weeks use their exact date bounds.
If a deployment ignores those bounds or interprets this field differently, the
run must be investigated rather than silently trusting a range-wide number.

## CSV contract

UTF-8 (optional BOM), comma-separated, exactly these seven columns:

`Date,Project,Activity,Description,Hours,Minutes,Resource`

Quoted commas and multiline text are supported. Each detail entry has the exact
configured project name and a resource. Dates may be ISO, US `MM/DD/YYYY`, or
an English weekday plus month name (e.g. `Sunday, September 13, 2026`). A blank
date inherits the current day within a group. Dates must be chronological and
inside the requested range. Other locales/layouts require an adapter update;
the parser does not guess ambiguous day/month conventions.

Hours and minutes are non-negative whole numbers; minutes range from 0 to 59.
Subtotal rows have `Total` or `Weekly Total` in Description with no Resource or
Activity. Each available subtotal must equal its preceding detail group. Source
strings and row order are preserved in Excel; only Hours/Minutes become numbers.
No new totals are inserted into the source table. The result record reports the
sum of detail minutes, avoiding double-counting subtotal rows.

Missing CSV subtotals produce warnings. Empty files, HTML/login pages, extra
columns, mixed projects, malformed entries, out-of-range dates, mismatched totals,
or unrenderably long cells fail visibly. Without an independent PMS control,
CSV arithmetic cannot establish that every intended entry was exported.
