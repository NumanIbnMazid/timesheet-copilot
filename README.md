# Timesheet Copilot

**An AI skill that turns PMS work logs into checked, readable Excel timesheets.**
Tell your assistant which project and dates you need. It gets the PMS export,
checks the hours, and prepares the file. If you ask, it can also draft the email.

## What am I installing?

A **skill** is a set of instructions and small helpers your AI assistant uses to
do a particular job. Timesheet Copilot is one skill. This repository is simply
the folder where its files are stored and shared.

There is no separate app, server or paid API account to set up. You need your
usual AI assistant, access to this private repository, and permission to view the
relevant timesheets in PMS. Your assistant needs to be able to read files and run
Python. Browser access helps it download exports; you can also download them yourself.

**You do not need to learn Git, write code, or run commands each week.**

## Start here

1. Get access to this private repository from its owner.
2. On GitHub, choose **Code → Download ZIP**, then unzip it. Open the folder in
   an assistant with local file access, such as Codex, Claude Code or Cursor.
   Ask it to read `AGENTS.md`. If you already use Git, cloning also works.
3. Paste this message:

   > Set up Timesheet Copilot using the skill in this folder. Help me choose my
   > PMS projects, where to save the files, and which day my week starts.
   > Keep my settings outside the skill folder. Run the fictional example first.

4. Sign in to PMS normally in the browser when needed. Then say:

   > Prepare last week's timesheet for my project.

Your assistant handles the helper setup. Python 3.10 or newer and the packages
listed in the skill's `requirements.txt` are needed. If Python is missing, it
will explain that one-time installation before continuing.

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

The **Enosis-compatible PMS timesheet export and API** are supported. “PMS” does
not mean every project-management system. Teams using the same PMS can supply
their own projects and settings. Browser downloads work without setting up an
API credential. An existing approved API credential enables direct downloads.

Jira and other time-log sources can be added later. They are not implemented in
this version. See [development and verification](docs/development.md) for the
small adapter boundary and current testing limits.

This version is distributed as a standalone skill in a private repository.
It does not require KPI Copilot or a plugin marketplace.
