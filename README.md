# Timesheet Copilot

**An AI skill that turns PMS work logs into checked, readable Excel timesheets.**
Tell your assistant which project and dates you need. It gets the PMS export,
checks the hours, and prepares the file. If you ask, it can also draft the email.

## What am I installing?

A **skill** is a set of instructions and small helpers your AI assistant uses to
do a particular job. Timesheet Copilot is one skill. This repository is simply
the folder where its files are stored and shared.

There is no separate app or server to set up. Your assistant runs the skill's
helpers, using PMS access you provide through one of the routes below.

**You do not need to learn Git, write code, or run commands each week.**

## Prerequisites: what you need first

- **Access to this private repository** so you can download the skill.
- **An assistant that can read files and run Python.** Python 3.10+ and the
  packages in the skill's `requirements.txt` must be available in that assistant's
  working environment. Ask the assistant to check and set this up for you.
- **Permission to view and export the selected projects in PMS.** Have your PMS
  website address and account ready. Connect to your work VPN if PMS requires it.
- **One working way to get the data:**

| Route | What you need to do |
|---|---|
| Browser export — easiest to start | Open PMS in a browser session your assistant can control, sign in yourself, and complete any verification step. Keep that session open. |
| Direct API download — optional | Obtain a valid PMS API access token through your PMS administrator or your team's approved process, then store it privately as described in the guide. |
| Downloaded CSV | Sign in yourself, export the selected project and dates from PMS, and give the CSV to the assistant. The assistant needs no live PMS login to format that file. |

**Signing in to PMS does not automatically sign in the Python helper.** Browser
export uses the browser session; direct API download uses a separately configured
token. Without either, provide a downloaded CSV. The skill cannot fetch private
timesheets using only a project name or website address.

Follow the [step-by-step PMS access setup](docs/start-here.md#connect-to-pms) for
your chosen route. A mail connection is needed only if you ask for mailbox drafts.

## Start here

1. Get access to this private repository from its owner.
2. On GitHub, choose **Code → Download ZIP**, then unzip it. Open the folder in
   an assistant with local file access, such as Codex, Claude Code or Cursor.
   Ask it to read `AGENTS.md`. If you already use Git, cloning also works.
3. Paste this message:

   > Set up Timesheet Copilot using the skill in this folder. Help me choose my
   > PMS projects, where to save the files, and which day my week starts.
   > Check the prerequisites and help me connect to PMS using browser export.
   > Keep my settings outside the skill folder. Run the fictional example first.

4. Complete the PMS access steps above. Ask the assistant to confirm it can see
   your selected project and export its timesheet, then say:

   > Prepare last week's timesheet for my project.

Your assistant handles the helper setup. If Python, PMS access, or an export
permission is missing, it explains the specific next step before attempting a
real run. The fictional example works without a PMS account.

For using it from other folders or in a skill-upload interface, see the
[short setup guide](docs/start-here.md). The assistant can install the skill for you.

## What you get

- One Excel workbook per selected project, with readable columns, wrapped text,
  visible totals and a frozen heading row.
- The original work descriptions and hours, preserved from PMS.
- A short result stating the dates, number of entries, total hours, and what was
  checked. A raw export and verification record stay beside each workbook.
- A new output folder for each run, so an earlier file is not overwritten.

PMS access is read-only. The helper never creates or changes timesheet entries.
It rejects mismatched totals, wrong-project exports, and entries outside the
requested dates. If a PMS total is unavailable, it clearly labels the result as
checked against the CSV only. Empty exports need a confirmed zero total.

## Examples of things to ask

> Prepare last week's timesheets for all my configured active projects.

> Prepare Atlas from September 1 through September 15, 2026.

> I downloaded this PMS CSV. Format it for Atlas and check it against the PMS
> total of 4 hours 35 minutes for September 13–19, 2026.

> Draft an email with this timesheet attached, using the recipients and wording
> I provide. Leave it as a draft.

Email is optional and uses your assistant's mail connection. No addresses,
signature, client template, or permission to send are built into the skill.

## Supported today

The **PMS timesheet export and API described in the
[PMS format reference](skills/timesheet-copilot/references/pms.md)** are supported.
“PMS” does not mean every project-management system. Teams whose PMS uses that
format can supply their own projects and settings. Browser export requires a
signed-in session; direct API download requires a valid configured token.

Jira and other time-log sources can be added later. They are not implemented in
this version. See [development and verification](docs/development.md) for the
small adapter boundary and current testing limits.

This version is distributed as a standalone skill in a private repository.
It does not require KPI Copilot or a plugin marketplace.
