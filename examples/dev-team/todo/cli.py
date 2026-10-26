"""Kommandozeilen-Schnittstelle fuer das Todo-Tool."""

from __future__ import annotations

import argparse
import sys

from todo.storage import TodoError, add_todo, list_todos, mark_done

DEFAULT_FILE = "todos.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="Kleines Todo-Tool")
    parser.add_argument(
        "--file",
        default=DEFAULT_FILE,
        help=f"Pfad zur JSON-Datei (Standard: {DEFAULT_FILE})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Todo hinzufuegen")
    p_add.add_argument("text", nargs="+", help="Text des Todos")

    sub.add_parser("list", help="Todos anzeigen")

    p_done = sub.add_parser("done", help="Todo als erledigt markieren")
    p_done.add_argument("id", type=int, help="ID des Todos")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "add":
            todo = add_todo(args.file, " ".join(args.text))
            print(f"Hinzugefügt: {todo['id']}")
        elif args.command == "list":
            todos = list_todos(args.file)
            if not todos:
                print("Keine Todos.")
            for t in todos:
                mark = "x" if t["done"] else " "
                print(f"[{mark}] {t['id']} {t['text']}")
        elif args.command == "done":
            todo = mark_done(args.file, args.id)
            print(f"Erledigt: {todo['id']}")
    except TodoError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    return 0
