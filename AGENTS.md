# Timesheet Copilot

For setup or a timesheet request, read `skills/timesheet-copilot/SKILL.md` and use
its helper. Keep real profiles, credentials, exports and output outside this repo.

For development, keep this a small standalone skill. PMS is the only implemented
source. Do not add a service, MCP server, plugin marketplace or tracker integration
without a concrete need. The PMS adapter reads data; the report validator checks
it; the workbook writer presents it. Never change reported work or hours to make
a check pass. Examples and tests must be fictional.

Run `python -m unittest discover -s tests -v` after changes to executable behavior.
Read `docs/development.md` for the adapter boundary and evidence limits. Do not
claim live PMS, mail delivery or host installation has been tested from unit tests.
