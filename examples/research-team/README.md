# Example: Research team (balcony solar plants in Germany)

A three-researcher team with an opus checker (models chosen by the user). Three haiku agents research cost, legal registration and yield in parallel; an opus agent then checks their findings and corrects them before the orchestrator writes the final report.

**Original prompt (German):**

> Bau mir ein Team: drei Agents recherchieren parallel je einen Aspekt von "Vor- und Nachteile von Solarbalkonkraftwerken in Deutschland" (Kosten, Recht/Anmeldung, Ertrag). Die Rechercheure sollen haiku sein, ein vierter Agent mit opus prüft die Ergebnisse gegen. Am Ende will ich einen kurzen Bericht von dir.

## Team

| Role | Model | Phase |
|---|---|---|
| recherche-kosten | haiku | 1 |
| recherche-recht | haiku | 1 |
| recherche-ertrag | haiku | 1 |
| gegenpruefer | opus | 2 |

## Notable findings

- The opus checker corrected the payback period from 3.4-4.3 years to 4-8 years.
- The checker found that a claimed 4-month meter-swap deadline is not in the law (§ 10a EEG).
- The checker corrected "one device per household": the law allows several devices within the limits.

## Files

- `bericht.md`: The final German report covering costs, legal registration, yield, electricity prices and open questions.
- `team-log.md`: The orchestrator's log of which agents were started, in which phase, and with which model.
