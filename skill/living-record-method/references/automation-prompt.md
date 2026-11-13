# Weekly Sweep Automation Prompt Template

Create with: weekly RRULE in the user's timezone, deliver_to source_thread, is_hidden false. The prompt must be self-contained per step and end with the reporting instruction.

Template (fill brackets):
---
Weekly [project] impact sweep for [user] ([github user]). Steps:
1) Use the gh CLI (already authenticated) with `gh repo list [user] --limit 200 --json name,visibility,updatedAt` to enumerate repositories; baseline is [N] total: [breakdown]. Report only changes from baseline (new, renamed, deleted, visibility changes).
2) Check [open security item URL] — [what to look for]; [what to remind the user if still open]; [what to record once closed].
3) Note notable changes across flagship repos ([list]).
4) Report a concise weekly layer: changes, security status, recommended next action. Keep the append-only relay principle: report as a new layer, never rewrite history.
Before ending, send the report to this conversation with automation_notify_source. Plain text in the run thread does not notify the source.
---
