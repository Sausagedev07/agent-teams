<p align="center">
  <img src="docs/img/banner.svg" alt="agent-teams: eine Orchestrator-Session koordiniert Subagents, die jeweils ein eigenes Modell nutzen (haiku, sonnet oder opus)" width="100%">
</p>

<p align="center"><a href="README.md">English</a> | <b>Deutsch</b></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="Lizenz: MIT"></a>
  <img src="https://img.shields.io/badge/models-haiku%20%C2%B7%20sonnet%20%C2%B7%20opus-8A63D2.svg" alt="Modelle: haiku, sonnet, opus">
</p>

# agent-teams

Ein Claude-Skill, der deine aktuelle Session zum Orchestrator eines Teams aus Subagents macht, wobei jedes Teammitglied sein eigenes Modell nutzt: `haiku`, `sonnet` oder `opus`.

> Dies ist ein Community-Skill. Er stammt nicht von Anthropic und ist kein offizielles Produkt. Der Skill ist auf Englisch geschrieben und funktioniert in jeder Sprache; er antwortet dir in deiner.

## Funktionen

- **Modellwahl pro Mitglied.** Günstiges `haiku` für Massenarbeit, `sonnet` als Standard, `opus` für Architektur und kritisches Review.
- **Parallel, wo es geht.** Unabhängige Mitglieder starten im selben Turn; abhängige starten, sobald ihre Vorgänger fertig sind.
- **Sicheres paralleles Schreiben.** Mitglieder, die gleichzeitig schreiben, bekommen getrennte Dateien oder Git-Worktrees.
- **Unabhängige Prüfung.** Ein Reviewer, der die Arbeit nicht selbst gemacht hat, prüft das Ergebnis. Der Orchestrator kontrolliert Behauptungen, behebt mittlere und schwere Befunde selbst und lässt die Tests erneut laufen.
- **Du behältst die Kontrolle.** Nennst du Rollen und Modelle, werden sie genau so übernommen. Sonst schlägt der Skill ein Team vor und zeigt es zuerst als kurze Tabelle.

## So funktioniert es

<p align="center">
  <img src="docs/img/architecture.svg" alt="Architekturdiagramm: Die Orchestrator-Session plant das Team, startet unabhängige Mitglieder parallel, reicht deren Ergebnisse an abhängige Mitglieder wie einen Reviewer weiter, prüft dann und liefert das Endergebnis" width="90%">
</p>

1. **Planen.** Der Orchestrator klärt das Ziel und entwirft das Team: Rolle, Modell, Agent-Typ, Auftrag und Abhängigkeiten je Mitglied.
2. **Starten.** Unabhängige Mitglieder werden mit dem `Agent`-Tool parallel gestartet, jedes mit einem in sich geschlossenen Briefing. Abhängige folgen später und bekommen die Ergebnisse ihrer Vorgänger.
3. **Einsammeln.** Berichte kommen als Benachrichtigung. Muss ein Mitglied nachbessern, wird es mit `SendMessage` fortgesetzt und behält seinen Kontext.
4. **Prüfen und liefern.** Der Orchestrator prüft stichprobenartig, löst Widersprüche auf, behebt Reviewer-Befunde und liefert das Ergebnis plus ein bis zwei Sätze dazu, wer was beigetragen hat.

Der Orchestrator ist die Session, in der du gerade bist, und läuft auf dem dort gewählten Modell. Ein Skill kann dieses Modell nicht ändern. Willst du einen anderen Orchestrator, stelle zuerst die Session um (in Claude Code mit `/model`).

Subagents können keine eigenen Subagents starten, deshalb muss der Skill in der Hauptsession laufen. Verschachtelte Teams baut der Orchestrator flach auf.

## Installation

**Claude Code**

Kopiere den Ordner `skill/agent-teams` an eine dieser Stellen:

```bash
# persönlich (alle Projekte)
cp -r skill/agent-teams ~/.claude/skills/agent-teams

# oder pro Projekt
mkdir -p .claude/skills
cp -r skill/agent-teams .claude/skills/agent-teams
```

**Claude-App**

[Lade `agent-teams.skill` herunter](https://github.com/Sausagedev07/agent-teams/raw/main/dist/agent-teams.skill) (liegt auch unter [`dist/`](dist/agent-teams.skill)) und lade sie in den Skill-Einstellungen der App hoch.

> **Voraussetzung:** Der Skill braucht eine Umgebung, in der die Hauptsession das `Agent`-Tool mit `model`-Parameter hat (z. B. Claude Code). Ohne das Tool schlägt der Skill nur einen Teamplan vor und erledigt die Arbeit selbst.

## Benutzung

Rufe den Skill mit einer Aufgabe auf oder beschreibe einfach das Team, das du willst:

```text
/agent-teams Vergleiche drei Static-Site-Generatoren für eine Doku-Seite.
```

```text
Bau mir ein Team: drei Rechercheure mit haiku, ein Reviewer mit opus, am Ende ein kurzer Bericht von dir.
```

```text
Build a team for a small Python CLI: one plans (opus), two implement in separate files (sonnet), one writes tests, one reviews.
```

Nennst du keine Modelle, wählt der Skill sie nach der Faustregel unten und sagt dir, welche er genommen hat.

## Modell-Faustregel

| Modell | Einsatz |
|---|---|
| `haiku` | Schnelle, einfache, klar abgegrenzte Arbeit: Dateien sichten, Daten sammeln, Formatierung, Massenaufgaben |
| `sonnet` | Standard für Umsetzung, Recherche mit Auswertung, Tests, Dokumentation |
| `opus` | Schwieriges Denken: Architektur, heikle Fehlersuche, kritisches Review |

Mehr Mitglieder sind nicht automatisch besser. Teile nur auf, wenn die Teile wirklich unabhängig sind oder eine zweite, unvoreingenommene Sicht (Review) etwas bringt. Zwei bis fünf Mitglieder reichen für fast jede Aufgabe. Fertige Besetzungen (Recherche, Entwicklung, Schreiben, Code-Review, Massenarbeit) stehen in [`skill/agent-teams/references/team-examples.md`](skill/agent-teams/references/team-examples.md).

## Benchmarks

Drei Testfälle, durchgeführt am 26.10.2026 mit Sonnet 5.5 als Orchestrator. Jede Konfiguration wurde **einmal** gemessen (n=1), es gibt also keine Varianzabschätzung. Die Baseline ist ein einzelner Subagent mit demselben Prompt ohne den Skill. Ein Subagent hat kein `Agent`-Tool, die Baseline kann also kein Team starten und übernimmt alle Rollen selbst. Die Läufe nutzten die ursprüngliche deutsche Fassung des Skills (v1.0.0); v1.1 ist eine englische Übersetzung mit denselben Anweisungen und wurde nicht neu gemessen.

**Erfüllte Kriterien** (Assertions je Testfall)

| Fall | Mit Skill | Baseline (Einzelagent) |
|---|---|---|
| Recherche-Team (Balkonkraftwerke, Deutschland) | 5/5 | 1/5 |
| Dev-Team (Python-CLI Todo-Tool) | 5/5 | 2/5 |
| Massensortierung (40 Produkte, 4 Kategorien) | 4/4 | 1/4 |
| **Gesamt** | **14/14** | **4/14** |

Interpretiere diese Scores vorsichtig: Die meisten Assertions prüfen Teamverhalten (richtige Modelle, paralleler Start, Reihenfolge), ein Einzelagent fällt dabei konstruktionsbedingt durch. Der Score zeigt, dass der Skill echte Teams zustande bringt, nicht dass ein Einzelagent schlechtere Texte schreibt.

<p align="center">
  <img src="docs/img/chart-scores.svg" alt="Balkendiagramm der erfüllten Kriterien je Testfall: mit Skill 5/5, 5/5 und 4/4 gegenüber der Baseline mit 1/5, 2/5 und 1/4" width="80%">
</p>

**Zeit und Tokens**

Zeiten in Sekunden. Der „kritische Pfad“ ist die Summe über alle Phasen des jeweils langsamsten Mitglieds einer Phase; Orchestrator-Overhead zwischen den Phasen ist nicht enthalten. Die „Team-Summe“ addiert alle Mitglieder.

| Fall | Baseline | Team, kritischer Pfad | Team-Summe |
|---|---|---|---|
| Recherche-Team | 56,5 | 257,4 | 393,0 |
| Dev-Team | 35,8 | 128,0 | 148,4 |
| Massensortierung | 20,6 | 24,8 | 56,1 |

| Fall | Tokens Team | Tokens Baseline | Faktor |
|---|---|---|---|
| Recherche-Team | 344.049 | 74.508 | 4,6x |
| Dev-Team | 339.592 | 70.120 | 4,8x |
| Massensortierung | 336.953 | 68.863 | 4,9x |

Die Token-Zahlen stammen vom Harness und enthalten den festen System-Prompt-Overhead jedes Agents (etwa 55-65k). Die Tokens des Orchestrators selbst wurden nicht gemessen, die echten Teamkosten liegen also höher.

<p align="center">
  <img src="docs/img/chart-time.svg" alt="Balkendiagramm der Zeit in Sekunden je Testfall: Baseline gegenüber Team-Kritischer-Pfad und Team-Summe" width="80%">
</p>

<p align="center">
  <img src="docs/img/chart-tokens.svg" alt="Balkendiagramm der Tokens je Testfall: das Team braucht etwa das 4,6- bis 4,9-Fache der Tokens der Einzelagent-Baseline" width="80%">
</p>

**Ehrliches Fazit.** In diesen Läufen ist ein Team teurer (etwa 4,6-4,9x so viele Tokens) und nicht schneller. Der Nutzen liegt in der unabhängigen Prüfung, die echte Fehler fand:

- Der Opus-Prüfer im Recherche-Fall korrigierte eine Amortisationszeit von 3,4-4,3 auf 4-8 Jahre und stellte fest, dass eine behauptete gesetzliche Frist im Gesetz nicht steht. (Das waren Fehler der Haiku-Rechercheure; ob die Baseline dieselben Fehler machte, wurde nicht geprüft.)
- Der Opus-Reviewer im Dev-Fall fand zwei mittlere Probleme: einen Traceback bei Schreibfehlern und einen Test, der seine eigene Zusage nicht prüfte. Der Orchestrator behob beide; die Suite wuchs von 26 auf 28 grüne Tests.

Ausführlicher Bericht: [`benchmarks/benchmark.md`](benchmarks/benchmark.md). Rohdaten: [`benchmarks/raw-data.json`](benchmarks/raw-data.json). Chart-Skript: [`benchmarks/make_charts.py`](benchmarks/make_charts.py).

## Wann (nicht) nutzen

Nutze ihn, wenn:

- sich die Aufgabe in wirklich unabhängige Teile zerlegen lässt (mehrere Rechercheaspekte, getrennte Module, Massenarbeit);
- du eine zweite Sicht willst, die die Arbeit nicht selbst gemacht hat (Review, Faktencheck, Gegenprüfung);
- verschiedene Teile verschiedene Modelle verdienen, etwa günstige Worker und ein starker Prüfer.

Lass es bleiben, wenn:

- die Aufgabe klein oder streng sequenziell ist, denn dann ist eine Session schneller und billiger;
- du die schnellste Antwort brauchst: In den Benchmarks war das Team langsamer als ein Einzelagent;
- die Token-Kosten wichtiger sind als eine unabhängige Prüfung.

## Aufbau des Repos

```text
skill/agent-teams/
  SKILL.md                      der Skill (Englisch)
  assets/team-template.md       wiederverwendbare Teamvorlage
  references/team-examples.md   fertige Teambesetzungen
dist/agent-teams.skill          gepackter Skill für die Claude-App
evals/                          3 Testfälle im claude-plugin-eval-Format
examples/
  research-team/
  dev-team/
  bulk-sorting/
benchmarks/                     benchmark.md, raw-data.json, make_charts.py
docs/img/                       Banner, Architekturdiagramm, Charts
LICENSE                         MIT
```

## Einschränkungen

- Subagents können keine Subagents starten. Führe den Skill in der Hauptsession aus; läuft er in einem Subagent, kann er nur einen Teamplan vorschlagen.
- Der Skill kann das Orchestrator-Modell nicht ändern. Stelle das Session-Modell selbst um.
- Genutzt werden nur `haiku`, `sonnet` und `opus`. Andere Modellnamen werden der nächsten passenden Stufe zugeordnet.
- Der Benchmark ist klein (3 Fälle, n=1) und misst überwiegend Teamverhalten. Die Zahlen sind ein Hinweis, kein Beweis.
- Die Kosten wachsen mit Teamgröße und Modellwahl. Setze starke Modelle nur ein, wo sie sichtbar etwas bringen.

## Lizenz

[MIT](LICENSE)
