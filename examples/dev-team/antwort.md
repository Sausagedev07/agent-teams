Das Todo-CLI (add/list/done, JSON-Datei, nur Standardbibliothek) ist fertig. Team und Modelle:

| Rolle | Modell | Aufgabe |
|---|---|---|
| Planer | opus | Dateien, Signaturen, JSON-Format, Fehlerverhalten |
| Umsetzer A | sonnet | storage.py (parallel zu B) |
| Umsetzer B | sonnet | cli.py, __main__.py (parallel zu A) |
| Tester | sonnet | 26 Tests |
| Reviewer | opus | unabhängige Prüfung |

Opus für Planung und Review, weil dort Denkfehler am teuersten sind; sonnet für die Umsetzung. Der Reviewer fand zwei mittlere Probleme (Schreibfehler endeten im Traceback; ein Test prüfte seine Zusage nicht). Beides ist behoben, jetzt laufen 28 Tests grün. Aufruf: `python -m todo [--file PFAD] add|list|done`. Regel für IDs: neue ID = höchste + 1.
