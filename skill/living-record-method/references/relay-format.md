# Relay Bundle Format

A relay layer is a markdown document with a YAML header. Each layer cites what came before; none rewrites it.

```yaml
relay_id: treasure-retrieval-N
project: "<Project>"
subject: "<One-line subject of this layer>"
precedes: "<Title of the previous layer, held as master index>"
authored_by: "<Who authored this layer, at whose direction>"
date: "YYYY-MM-DD"
method: "<How evidence was obtained>"
status: "delivered, pending review"
principle: "Append-only. This layer adds evidence; it does not rewrite what came before."
```

Body sections:
1. Answer to any held question from the previous layer
2. Register reconciliation table: | ID | Work item | Status (complete/partial/open) | Evidence recorded in this layer |
3. New findings — events for the evidence ledger
4. Editorial boundary (preserved): reported states stay reported; inspected states marked inspected
5. What remains for future layers

Status vocabulary: **complete** (evidence exists), **partial** (evidence covers some scope), **open** (not done — say so plainly). Never mark a row complete without its evidence citation in the same row.
