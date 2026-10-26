"""Speicherschicht für das Todo-CLI (JSON-Datei, nur Standardbibliothek)."""

import json
import os
import tempfile


class TodoError(Exception):
    """Einzige Fehlerklasse; str(e) ist die Meldung für den Nutzer."""


def _invalid(path):
    return TodoError(f"Datei {path} ist kein gültiges Todo-JSON")


def load(path: str) -> list[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []
    except (ValueError, UnicodeDecodeError, OSError):
        raise _invalid(path) from None
    if not isinstance(data, dict) or not isinstance(data.get("todos"), list):
        raise _invalid(path)
    for t in data["todos"]:
        if (
            not isinstance(t, dict)
            or not isinstance(t.get("id"), int)
            or isinstance(t.get("id"), bool)
            or not isinstance(t.get("text"), str)
            or not isinstance(t.get("done"), bool)
        ):
            raise _invalid(path)
    return data["todos"]


def save(path: str, todos: list[dict]) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    try:
        fd, tmp = tempfile.mkstemp(dir=directory, prefix=".todo-", suffix=".tmp")
    except OSError as e:
        raise TodoError(f"Datei {path} kann nicht geschrieben werden: {e.strerror}") from None
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"todos": todos}, f, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException as e:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        if isinstance(e, OSError):
            raise TodoError(f"Datei {path} kann nicht geschrieben werden: {e.strerror}") from None
        raise


def add_todo(path: str, text: str) -> dict:
    text = text.strip()
    if not text:
        raise TodoError("Text darf nicht leer sein")
    todos = load(path)
    new_id = max((t["id"] for t in todos), default=0) + 1
    todo = {"id": new_id, "text": text, "done": False}
    todos.append(todo)
    save(path, todos)
    return todo


def list_todos(path: str) -> list[dict]:
    return sorted(load(path), key=lambda t: t["id"])


def mark_done(path: str, todo_id: int) -> dict:
    todos = load(path)
    for t in todos:
        if t["id"] == todo_id:
            if not t["done"]:
                t["done"] = True
                save(path, todos)
            return t
    raise TodoError(f"Unbekannte ID: {todo_id}")
