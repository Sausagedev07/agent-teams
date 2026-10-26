# Example: Bulk sorting (40 product descriptions into 4 categories)

Four haiku workers each sort ten of the 40 product descriptions into the categories Küche, Garten, Sport and Büro, working in parallel on separate line ranges. The orchestrator merges their output, and a sonnet checker then verifies completeness and the assignments.

> **Note on the test data:** all descriptions in `produkte.txt` are the same placeholder ("kurze Beschreibung"), and the 40 lines repeat 16 product names (e.g. Wasserkocher, Toaster). The task is therefore easy; assignment rests on product names alone.


**Original prompt (German):**

> Ich muss 40 kurze Produktbeschreibungen in 4 Kategorien einsortieren (Küche, Garten, Sport, Büro) und danach noch einmal kritisch auf Fehler prüfen lassen. Setz dafür ein Agent-Team ein. Input: produkte.txt

## Team

| Role | Model | Phase |
|---|---|---|
| sortierer-1 (1-10) | haiku | 1 |
| sortierer-2 (11-20) | haiku | 1 |
| sortierer-3 (21-30) | haiku | 1 |
| sortierer-4 (31-40) | haiku | 1 |
| pruefer | sonnet | 2 |

## Notable findings

- All 40 items were assigned exactly once (11 / 9 / 11 / 9 across Küche, Garten, Sport and Büro).
- The sonnet checker found no errors and confirmed the three borderline items.

## Files

- `antwort.md`: The short answer to the user, naming the models used and the category counts.
- `einsortiert.md`: The merged list of all 40 products with their assigned category.
- `team-log.md`: The orchestrator's log of the parallel sorters, the merge step and the checker.
- `teile/teil-1.md`: The sorter 1 result for items 1-10.
- `teile/teil-2.md`: The sorter 2 result for items 11-20.
- `teile/teil-3.md`: The sorter 3 result for items 21-30.
- `teile/teil-4.md`: The sorter 4 result for items 31-40.
