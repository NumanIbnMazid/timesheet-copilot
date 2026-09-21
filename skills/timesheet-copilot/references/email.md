# Optional timesheet email

Email delivery is performed by the assistant's existing mail tools, not the
Python helper. Preparing files does not authorize mailbox searches or drafts.
Use this workflow when the user asks for an email or draft.

Use recipients and wording supplied by the user, their explicitly selected
template, or a specific prior email they authorize you to inspect. Do not copy
recipients from unrelated projects, infer a new project's recipients from a
predecessor, or include a hard-coded sender signature. If recipient information
is missing, finish the workbook and ask for that information.

If no special wording is supplied, propose a short factual message with the
project, exact date range, and attachment. Use “timesheet” for a custom range,
and “weekly timesheet” only when appropriate. A template may override the style.

Before creating a draft, inspect matching existing drafts if the host permits it
to avoid duplicates on retries. Attach the exact verified `.xlsx`. Use native
file attachments or programmatic bytes from disk; never reconstruct base64 in
the model's prose or claim a placeholder is an attachment.

Read back the saved draft's recipients, dates, text and attachment metadata.
When available, download/hash the attachment and compare with the prepared file.
If the provider cannot verify contents, state the narrower check. A returned
draft ID alone does not prove attachment presence. If mail tools fail, deliver
the workbook and draft text and clearly say the mailbox draft is incomplete.

Leave it as a draft unless sending is explicitly requested. Existing explicit
authorization carries forward; do not invent a second approval ceremony.
