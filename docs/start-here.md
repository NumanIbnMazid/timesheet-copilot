# Getting started

## Choose the easiest route

**Open the downloaded folder in your assistant.** This is the simplest first
use. Download the ZIP from this private GitHub repository, unzip it, and give
your assistant access to the folder. Say:

> Read AGENTS.md and set up Timesheet Copilot for me. Run the fictional example,
> then help me connect my own PMS projects.

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

## How PMS access works

**Browser route:** Sign in to PMS as usual. An assistant with browser controls
can select the project and dates and click Export. If your assistant cannot
control your browser, download the CSV yourself and give it the file. To check
against PMS independently, also provide the total shown for the same project,
dates and all members/activities.

**API route:** If your team already has an approved API credential, the helper
can download the CSV and compare it with PMS totals automatically. Your
assistant can help configure where the credential is stored without showing it
in chat. You do not need this route to get started. Setup details for the
assistant are in [PMS access](../skills/timesheet-copilot/references/pms.md).

Never paste a password or token into a conversation or into the profile. The
skill does not extract browser tokens. A failed login produces an access error,
not a timesheet with zero hours.

## Weekly use

Say “Prepare last week's timesheets.” Last week means the previous complete
week in your configured timezone. An explicit date range always takes precedence.
The assistant states the exact dates and selected projects before running.

It checks entries and available totals, prepares the Excel files and gives you
links. Review the files before sharing them. If it reports a total mismatch,
correct or re-export the data in PMS; the helper does not alter hours to make
the figures agree.

For email drafts, supply recipients and your preferred wording, or ask the
assistant to look at a specific prior email. A finished draft must include the
correct attachment. Sending requires your explicit instruction.

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
