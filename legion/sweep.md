# Weekly Node Sweep — Prompt Template

Schedule weekly in the node's timezone, deliver to the node's source thread. Fill brackets.

---
Weekly [node name] sweep for [user]. Steps:
1) Enumerate [what the node carries — repos / files / systems] and diff against the baseline layer (LAYER-001, [date]). Report only changes: new, changed, removed.
2) Check open security items from the baseline: [items]. Remind if still open; record closure when closed.
3) Note notable changes worth the record.
4) Append the next relay layer (LAYER-002, 003, ...) — append-only, never rewriting earlier layers. Update the register statuses with evidence.
Before ending, send the report to this conversation with automation_notify_source.
---
