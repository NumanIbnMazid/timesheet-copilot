# Getting started

## Prerequisites

Before preparing a real timesheet, you need:

- Access to this private repository and an assistant that can read files, run
  Python and save the finished workbook. Ask it to check for Python 3.10+ and
  install the skill's required packages in its working environment.
- Your PMS website address and permission to view/export the projects you want.
  If PMS is on a private work network, connect to the required VPN first.
- A signed-in browser session available to the assistant, a configured API token,
  or a CSV you have already exported. Choose one route under
  [Connect to PMS](#connect-to-pms).

The skill does not supply a PMS account, sign in for you, or gain access from
the website address alone. The fictional demo needs no PMS connection. To read
the finished `.xlsx`, use Excel or another compatible spreadsheet viewer.

## Choose the easiest route

**Open the downloaded folder in your assistant.** This is the simplest first
use. Download the ZIP from this private GitHub repository, unzip it, and give
your assistant access to the folder. Say:

> Read AGENTS.md and set up Timesheet Copilot for me. Check the prerequisites,
> run the fictional example, then help me connect my PMS account and projects
> using browser export.

Your assistant reads the skill and runs its helpers. Keeping the folder is enough
for this route; you do not also need a plugin installation.

**Already using installed skills?** Ask your assistant to install the entire
`skills/timesheet-copilot` folder, including its scripts, requirements, examples,
and references. For Codex, this copyable prompt uses the built-in installer:

> $skill-installer install the skill at
> https://github.com/NumanIbnMazid/timesheet-copilot/tree/main/skills/timesheet-copilot

You must be signed in to GitHub with access to this private repository. If the
installer cannot authenticate, use the downloaded-folder route. Codex supports
local skills and a skill installer; see the [official skill guide](https://learn.chatgpt.com/docs/build-skills).

**Using a skill-upload interface?** Upload a ZIP containing the
`timesheet-copilot` folder with `SKILL.md` directly inside it. Ask your assistant
to package that folder if needed. The host must support scripts and file output;
an instruction-only chat cannot run the formatter or access your computer.
For Claude Desktop, use a mode with file/script access and, for automatic PMS
exports, browser access. Available installation controls depend on your host.

## One-time setup

The assistant needs these details. It should read them from the PMS page or an
export when possible and ask only for what remains unclear.

| Setting | In ordinary language |
|---|---|
| PMS address | The website where you already enter or review work logs |
| Project name and ID | Which projects to prepare; the ID appears in the project page's address |
| Week and timezone | For example, Sunday–Saturday in Dhaka or Monday–Sunday in London |
| Output folder | Where you want the finished Excel files |
| File label | An optional team prefix and shorter project name for filenames |

These go in one `profile.json` file in a private folder you choose, outside the
downloaded or installed skill. Relative output paths are resolved beside that
profile. You can have separate profiles for different teams. You normally talk
to the assistant; you do not need to edit JSON yourself.

The assistant installs Python dependencies in its working environment, checks
the profile, and remembers the profile path in your project instructions if
you ask it to. Updates to the skill should not replace your settings.

## Connect to PMS

Choose one route. A browser login and an API token are separate ways to sign in;
you do not need both.

### Option 1: sign in through the browser

1. Tell your assistant: “Open my PMS website in the browser you can control.”
   Give it the website address. If it has no browser connection, use Option 3.
2. In that browser, enter your own username/password or use your normal work
   sign-in. Complete any two-step verification. Keep the signed-in tab open.
   Signing in to a different browser or profile may not give the assistant access.
3. Open the selected project's timesheet. Confirm that you can see its entries
   and an Export control. If you cannot, ask your PMS administrator for access
   to view/export that project's timesheets.
4. Tell the assistant: “I am signed in. Prepare the timesheet for this project
   and these dates.” It uses the browser to download the CSV, then formats it.

No API token is required for this route. You enter your password in PMS, not in
chat. If the session expires, sign in again in the same browser session.

### Option 2: set up direct API downloads

Use this if your team supports PMS API access and you want the helper to fetch
exports and totals directly. You do not have to keep a browser signed in.

1. Ask your PMS administrator or follow your team's documented process to obtain
   an **API access token that can read/export timesheets for your projects**.
   A normal account password is not an API token. There is no built-in token
   issuing or renewal feature in this skill. If your team cannot provide API
   access, use Option 1 or 3.
2. Tell the assistant: “Prepare a private local file for my PMS token, and
   configure the profile to use that file. Tell me where to save the token;
   do not display its contents.” The file must be outside the skill/repository,
   readable only by your account, and accessible to the helper's environment.
3. Open that file yourself in a plain-text editor. Paste only the complete token
   and save it. Do not add quotes, `Bearer`, or your username. Tell the assistant
   the file is ready. Do not paste the token into chat or `profile.json`.
4. Ask the assistant to fetch one selected project for a known date range and
   compare the total with PMS. This tests access. A successful fictional demo or
   profile check does not test your credential.

The profile contains only the token file's path. The helper reads the token when
needed. Your IT team can alternatively supply it through an environment variable
available to the helper. See the [assistant's credential setup instructions](../skills/timesheet-copilot/references/pms.md#credential-setup)
for both methods.

If the token expires or is revoked, obtain a replacement through the same process
and update the private file. A browser sign-in does not renew this token. For
access-denied errors, also check the token's permissions for the selected project.

### Option 3: download the CSV yourself

1. Sign in to PMS in your own browser. Open the selected project's timesheet,
   set the exact dates, and include all members and activities.
2. Click Export and save the CSV. Note the total PMS shows for that same scope
   if you want an independent total check.
3. Give the assistant the CSV, project name and dates. For example: “Format this
   PMS export for Atlas, September 13–19, 2026. PMS shows 4 hours 35 minutes.”

The assistant can format this file without a browser connection or API token.
It cannot refresh the data until you provide another export or connect live access.
Without the PMS control total, it reports that only CSV consistency was checked.

### If setup is blocked

| What happens | What to do |
|---|---|
| The assistant sees a login page | Sign in in the browser session the assistant is using. |
| You cannot see the project or Export button | Ask your PMS administrator for the relevant view/export permission. |
| PMS cannot be reached | Check the website address, work network and VPN. |
| The helper reports a missing token | Configure the private token file/environment, or switch to browser/manual export. |
| The API reports access denied | Renew the token if needed and check project permissions; signing in to a browser alone does not fix API access. |
| The assistant cannot run Python or access files | Use an assistant mode with those capabilities and finish the one-time helper setup. |

## Weekly use

Say “Prepare last week's timesheets.” Last week means the previous complete
week in your configured timezone. An explicit date range always takes precedence.
The assistant states the exact dates and selected projects before running.

It checks entries and available totals, prepares the Excel files and gives you
links. Review the files before sharing them. If it reports a total mismatch,
correct or re-export the data in PMS; the helper does not alter hours to make
the figures agree.

For email drafts in your mailbox, first connect your email account using the
assistant's supported mail integration and allow draft/attachment access.
Supply recipients and your preferred wording, or ask the assistant to look at
a specific prior email. Without a mail connection, it can provide the email text
and workbook for you to attach yourself. A finished mailbox draft must include
the correct attachment. Sending requires your explicit instruction.

## Common questions

**Do I need to clone the repository?** No. Downloading the ZIP works. Cloning is
just another way to keep a local copy and get updates.

**Is this a plugin?** This version is a single standalone skill. A plugin could
package it later if distribution needs grow.

**Does everyone use the original author's projects?** No. Project names, IDs,
week boundaries, output paths and labels are your own settings. Shared examples
are fictional, and email details come from you.

**Can I use Jira?** Not yet. This version reads PMS only.

**How do I update?** Download or pull the latest repository, or reinstall the
skill. Keep your separate profile and output folder. Do not overwrite a working
installation with a partially copied `SKILL.md` alone.
