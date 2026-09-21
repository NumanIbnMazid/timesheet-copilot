# PMS access and export contract

This adapter targets the Enosis PMS API shape documented in the original skill.
The origin is configurable; it is not an integration with every product called
PMS. Endpoint contracts below are inherited from that workflow. Validate a real
run before claiming acceptance on a new deployment.

## Browser export: no API credential setup

Use the host's supported browser controls. Sign-in happens in the browser, by
the user. For a configured project, navigate to:

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

The helper accepts an environment variable named by `pms.token_env` (default
`PMS_TOKEN`) **or** `pms.token_file`, a path to a plain token stored outside the
skill/repository. Configure one, not both. For a token file on POSIX, permissions
must exclude group/other access (normally `600`). On other systems use an
appropriately restricted file ACL. The profile holds the path, never the token.

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
