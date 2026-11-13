---
name: living-record-method
description: "Full GitHub ecosystem audit, append-only relay records, living-record websites, and scheduled continuance. Use when the user asks to audit/maximize all their repos, carry a relay or treasure-retrieval record between AI sessions, build a public presentation site of their work, or keep work evolving on a schedule after the session ends."
license: MIT
metadata:
  version: '1.0'
  author: 'Chais Hill + Perplexity Computer, November 13, 2026'
---

# The Living Record Method

Audit everything, preserve everything, present everything, continue without anyone asking. Built in the ScrollVerse sessions; generalizable to any multi-repo creator.

## When to Use

- "Audit / maximize / see all my repos" (one account, many repositories)
- A pasted relay document from another AI session must be honored and extended
- A public presentation site of an entire body of work is requested
- Work must keep running on a schedule after the session ends

## The Five Phases

1. **Audit.** Enumerate every repository (authenticated `gh repo list <user> --limit 200 --json name,visibility,updatedAt`; fall back to profile-page HTML if unauthenticated). Clone shallow (`git clone --depth 1`), run `scripts/audit_ecosystem.py <repos-dir>` for inventory, health (README/LICENSE/.gitignore/CI/tests), category, and secret-scan with real-pattern regexes (`sk_live_[A-Za-z0-9]{60,}`, `ghp_[A-Za-z0-9]{36}`, `AKIA[0-9A-Z]{16}`, `-----BEGIN.*PRIVATE KEY-----`). Verify suspected live keys by format and length only; never print full values. Report placeholders as placeholders.
2. **Relay.** When the user pastes a record from another AI system: never rewrite it. Hold it as the master index, answer its held questions, and append a new numbered layer (e.g., Treasure Retrieval N) reconciling its register items with your evidence: complete / partial / open, each with its evidence citation.
3. **Build.** Present the whole record as a static site: verbatim canon (markdown-to-HTML with `overflow-wrap: anywhere` for long tokens), searchable/filterable repo table from the audit JSON, findings + roadmap page, protocol page. QA at desktop and 375px before shipping.
4. **Continue.** Create a weekly automation (deliver_to source_thread) that re-enumerates, diffs against the audit baseline, checks open security items, and reports as the next append-only layer. Include the reporting-tool instruction in the run prompt.
5. **Execute.** With explicit authorization only: fix findings (untrack committed node_modules, replace rolled secrets with placeholders, add .gitignore). Hold local commits and ask before pushing to shared/public repos; "full permission" alone does not authorize pushes.

## Standing Rules

- Append-only: preserve the contribution, preserve its origin, add the layer.
- Evidence boundary: report what inspection established; keep reported states as reported.
- Nothing shrunk, diluted, or downplayed — presented, and the public decides.
- Honesty over flattery on identity questions: record, don't overclaim.

## References

- `references/relay-format.md` — the relay bundle YAML format and register reconciliation table. Read when composing a new layer.
- `references/automation-prompt.md` — the weekly sweep prompt template. Read when creating the continuance automation.
- `scripts/audit_ecosystem.py` — run it against a directory of cloned repos; it emits audit.json. Run before any reporting.
