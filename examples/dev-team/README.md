# Example: Dev team (Python CLI todo tool)

A five-member team that builds a small command-line todo tool (add, list, done; JSON file storage, standard library only). A planner writes the design, two implementers work on separate files in parallel, a tester writes the test suite, and a reviewer checks the result.

**Original prompt (German):**

> ich will ein kleines python-cli todo tool (add/list/done, json datei). mach ein team draus: einer plant, zwei setzen um (getrennte dateien), einer testet, am schluss ein review. nimm modelle wie du es sinnvoll findest und sag mir welche du nimmst

## Team

| Role | Model | Phase |
|---|---|---|
| planer | opus | 1 |
| umsetzer-a (storage.py) | sonnet | 2 |
| umsetzer-b (cli.py) | sonnet | 2 |
| tester | sonnet | 3 |
| reviewer | opus | 4 |

## Notable findings

- The reviewer found two medium issues: write errors ended in a traceback, and a test named "id never reused" did not test that promise.
- The orchestrator fixed both; the test suite grew from 26 to 28 passing tests.

## Files

- `antwort.md`: The final answer to the user, with the team table, the model choices, the reviewer findings and the run command.
- `team-log.md`: The orchestrator's log of the planner, the two parallel implementers, the tester and the reviewer.
- `todo/__init__.py`: Empty package marker.
- `todo/__main__.py`: Entry point so the tool runs as `python -m todo`.
- `todo/cli.py`: The argparse command-line interface for `add`, `list` and `done`.
- `todo/storage.py`: The JSON storage layer with `TodoError` and the add, list and done operations.
- `tests/test_todo.py`: The unittest suite for the storage and the command-line behaviour.
