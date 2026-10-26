import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

OUTPUTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if OUTPUTS not in sys.path:
    sys.path.insert(0, OUTPUTS)

from todo import cli, storage  # noqa: E402


class TmpMixin(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = os.path.join(self._tmp.name, "t.json")

    def write(self, content):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(content)

    def read(self):
        with open(self.path, encoding="utf-8") as f:
            return f.read()


class StorageTests(TmpMixin):
    def test_missing_file_is_empty(self):
        self.assertEqual(storage.load(self.path), [])
        self.assertEqual(storage.list_todos(self.path), [])

    def test_add_creates_file_with_format(self):
        t = storage.add_todo(self.path, "Milch")
        self.assertEqual(t, {"id": 1, "text": "Milch", "done": False})
        self.assertEqual(json.loads(self.read()),
                         {"todos": [{"id": 1, "text": "Milch", "done": False}]})

    def test_ids_increment(self):
        self.assertEqual(storage.add_todo(self.path, "a")["id"], 1)
        self.assertEqual(storage.add_todo(self.path, "b")["id"], 2)

    def test_id_is_max_plus_one_with_gaps(self):
        self.write(json.dumps({"todos": [
            {"id": 3, "text": "x", "done": False},
            {"id": 7, "text": "y", "done": True}]}))
        self.assertEqual(storage.add_todo(self.path, "z")["id"], 8)

    def test_empty_and_whitespace_text(self):
        for txt in ("", "   ", "\t\n"):
            with self.assertRaises(storage.TodoError):
                storage.add_todo(self.path, txt)
        self.assertFalse(os.path.exists(self.path))

    def test_mark_done(self):
        storage.add_todo(self.path, "a")
        t = storage.mark_done(self.path, 1)
        self.assertTrue(t["done"])
        self.assertTrue(storage.load(self.path)[0]["done"])

    def test_mark_done_twice_ok(self):
        storage.add_todo(self.path, "a")
        storage.mark_done(self.path, 1)
        self.assertTrue(storage.mark_done(self.path, 1)["done"])

    def test_mark_done_unknown_id(self):
        storage.add_todo(self.path, "a")
        with self.assertRaises(storage.TodoError):
            storage.mark_done(self.path, 99)

    def test_unicode_roundtrip(self):
        storage.add_todo(self.path, "Käse über Öl ✓")
        self.assertEqual(storage.load(self.path)[0]["text"], "Käse über Öl ✓")

    def test_broken_json_raises_and_not_overwritten(self):
        self.write("{kaputt")
        for fn in (lambda: storage.load(self.path),
                   lambda: storage.add_todo(self.path, "x"),
                   lambda: storage.mark_done(self.path, 1),
                   lambda: storage.list_todos(self.path)):
            with self.assertRaises(storage.TodoError):
                fn()
        self.assertEqual(self.read(), "{kaputt")

    def test_wrong_structure_raises(self):
        for content in ('[]', '{"foo":1}', '{"todos":{}}', '{"todos":[1]}',
                        '{"todos":[{"id":"1","text":"a","done":false}]}',
                        '{"todos":[{"id":1,"text":"a"}]}'):
            self.write(content)
            with self.assertRaises(storage.TodoError, msg=content):
                storage.load(self.path)

    def test_empty_file_is_error(self):
        self.write("")
        with self.assertRaises(storage.TodoError):
            storage.load(self.path)

    def test_no_tmp_files_left(self):
        storage.add_todo(self.path, "a")
        self.assertEqual(os.listdir(self._tmp.name), ["t.json"])

    def test_list_sorted_by_id(self):
        self.write(json.dumps({"todos": [
            {"id": 2, "text": "b", "done": False},
            {"id": 1, "text": "a", "done": False}]}))
        self.assertEqual([t["id"] for t in storage.list_todos(self.path)], [1, 2])


class CliTests(TmpMixin):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(["--file", self.path, *args])
        return code, out.getvalue(), err.getvalue()

    def test_add_and_list(self):
        self.assertEqual(self.run_cli("add", "Milch", "kaufen"),
                         (0, "Hinzugefügt: 1\n", ""))
        self.assertEqual(self.run_cli("add", "Brot"), (0, "Hinzugefügt: 2\n", ""))
        self.assertEqual(self.run_cli("list"),
                         (0, "[ ] 1 Milch kaufen\n[ ] 2 Brot\n", ""))

    def test_list_empty(self):
        self.assertEqual(self.run_cli("list"), (0, "Keine Todos.\n", ""))
        self.assertFalse(os.path.exists(self.path))

    def test_done(self):
        self.run_cli("add", "a")
        self.run_cli("add", "b")
        self.assertEqual(self.run_cli("done", "2"), (0, "Erledigt: 2\n", ""))
        self.assertEqual(self.run_cli("list"), (0, "[ ] 1 a\n[x] 2 b\n", ""))

    def test_done_twice_no_error(self):
        self.run_cli("add", "a")
        self.run_cli("done", "1")
        self.assertEqual(self.run_cli("done", "1"), (0, "Erledigt: 1\n", ""))

    def test_done_unknown_id(self):
        code, out, err = self.run_cli("done", "5")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("Fehler: "))

    def test_add_empty_text(self):
        for txt in ("", "   "):
            code, out, err = self.run_cli("add", txt)
            self.assertEqual(code, 1)
            self.assertEqual(out, "")
            self.assertTrue(err.startswith("Fehler: "))
        self.assertFalse(os.path.exists(self.path))

    def test_broken_json(self):
        self.write("nicht json")
        for args in (("list",), ("add", "x"), ("done", "1")):
            code, out, err = self.run_cli(*args)
            self.assertEqual(code, 1, args)
            self.assertEqual(out, "")
            self.assertTrue(err.startswith("Fehler: "))
        self.assertEqual(self.read(), "nicht json")

    def test_new_id_is_max_plus_one_after_deleting_first(self):
        self.run_cli("add", "a")
        self.run_cli("add", "b")
        data = json.loads(self.read())
        data["todos"] = [t for t in data["todos"] if t["id"] != 1]
        self.write(json.dumps(data))
        self.run_cli("add", "c")
        self.assertEqual(self.run_cli("list")[1], "[ ] 2 b\n[ ] 3 c\n")

    def test_highest_id_is_reused_after_manual_delete(self):
        # Bewusst dokumentiert: Regel ist max+1. Wird die höchste ID von Hand
        # gelöscht, wird sie wieder vergeben (das CLI hat keinen Löschbefehl).
        self.run_cli("add", "a")
        self.run_cli("add", "b")
        data = json.loads(self.read())
        data["todos"] = [t for t in data["todos"] if t["id"] != 2]
        self.write(json.dumps(data))
        self.run_cli("add", "c")
        self.assertEqual(self.run_cli("list")[1], "[ ] 1 a\n[ ] 2 c\n")

    def test_unwritable_path_reports_error(self):
        bad = os.path.join(self.path + "-gibt-es-nicht", "t.json")
        with contextlib.redirect_stderr(io.StringIO()) as err:
            with contextlib.redirect_stdout(io.StringIO()):
                code = cli.main(["--file", bad, "add", "x"])
        self.assertEqual(code, 1)
        self.assertTrue(err.getvalue().startswith("Fehler: "))

    def test_unicode(self):
        self.run_cli("add", "Äpfel ✓")
        self.assertEqual(self.run_cli("list")[1], "[ ] 1 Äpfel ✓\n")

    def test_invalid_usage_exits_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                cli.main(["--file", self.path, "done", "abc"])
        self.assertEqual(cm.exception.code, 2)
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                cli.main(["--file", self.path])


class SubprocessTests(TmpMixin):
    def run_mod(self, *args):
        return subprocess.run([sys.executable, "-m", "todo", "--file", self.path, *args],
                              cwd=OUTPUTS, capture_output=True, text=True,
                              encoding="utf-8", timeout=30)

    def test_end_to_end(self):
        r = self.run_mod("add", "Hallo", "Welt")
        self.assertEqual((r.returncode, r.stdout), (0, "Hinzugefügt: 1\n"))
        r = self.run_mod("done", "1")
        self.assertEqual((r.returncode, r.stdout), (0, "Erledigt: 1\n"))
        r = self.run_mod("list")
        self.assertEqual((r.returncode, r.stdout), (0, "[x] 1 Hallo Welt\n"))

    def test_error_exit_code(self):
        r = self.run_mod("done", "9")
        self.assertEqual(r.returncode, 1)
        self.assertTrue(r.stderr.startswith("Fehler: "))


if __name__ == "__main__":
    unittest.main()
