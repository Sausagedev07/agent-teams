# Ready-made team line-ups

Read this file when the user needs a team but doesn't specify roles. Adapt the line-up and models to the task; these are starting points, not rules.

## Research team
Split the question into sub-questions, search in parallel, cross-check.
- 3–4× `research-<topic>` – **haiku** or **sonnet**, type `general-purpose`: one sub-question each, sources as links
- 1× `checker` – **opus**: checks the key claims against the sources, flags gaps
- The orchestrator writes the report

## Development team
- `architect` – **opus**, type `Plan`: structure, interfaces, file list (writes nothing)
- `builder-a`, `builder-b` – **sonnet**, `general-purpose`: separate modules, separate files
- `tester` – **sonnet**: write and run tests, report failures
- `reviewer` – **opus**: read the diff, name bugs and risks
- Order: architect → builders in parallel → tester → reviewer

## Writing / content team
- `researcher` – **haiku**: collect facts and examples
- `author` – **sonnet**: draft from an outline
- `editor` – **opus**: style, logic, gaps; returns a list of changes rather than a rewrite

## Code review team (read-only)
Several perspectives on the same code, all in parallel:
- `security`, `performance`, `readability` – **sonnet** each, type `Explore`
- The orchestrator merges and prioritizes the findings

## Bulk work
Many small tasks of the same kind (renaming files, classifying texts, cleaning data):
- N× `worker-<n>` – **haiku**, each with its own slice
- 1× `checker` – **sonnet**: spot-checks the results
