"""Source-launcher setup/readiness and explicit index-replacement boundaries."""

from contextlib import redirect_stderr, redirect_stdout
from hashlib import sha256
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from versionlens.store import connect


PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("versionlens_run_local", PROJECT / "scripts/run_local.py")
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)


class SourceDeploymentTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "checkout"
        self.root.mkdir()
        shutil.copytree(PROJECT / "data/corpus", self.root / "data/corpus")
        shutil.copytree(PROJECT / "data/synthetic", self.root / "data/synthetic")
        shutil.copyfile(PROJECT / "data/sources.json", self.root / "data/sources.json")
        self.index = self.root / "data/versionlens.sqlite3"

    def run_launcher(self, *arguments):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(launcher, "ROOT", self.root), redirect_stdout(output), redirect_stderr(errors):
            code = launcher.main(list(arguments))
        raw = output.getvalue() or errors.getvalue()
        return code, json.loads(raw) if raw else None

    def test_missing_readiness_check_creates_no_index_or_extra_files(self):
        before = sorted(str(path.relative_to(self.root)) for path in self.root.rglob("*"))
        code, result = self.run_launcher("--check")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "not_ready")
        self.assertEqual(result["reason"], "index_missing")
        self.assertFalse(result["model_server_checked"])
        self.assertEqual(before, sorted(str(path.relative_to(self.root)) for path in self.root.rglob("*")))

    def test_first_prepare_verifies_and_builds_the_actual_public_corpus(self):
        with patch("versionlens.local_model.LocalModelClient") as generation, patch("versionlens.embeddings.LocalEmbeddingClient") as embedding:
            code, result = self.run_launcher("--prepare")
        self.assertEqual(code, 0)
        self.assertEqual(result["operation"], "created")
        self.assertEqual((result["index"]["sources"], result["index"]["chunks"]), (32, 644))
        self.assertEqual(result["index"]["versions"], ["0.27.2", "0.28.1"])
        generation.assert_not_called()
        embedding.assert_not_called()

    def test_matching_prepare_keeps_existing_database_bytes(self):
        self.run_launcher("--prepare")
        before = sha256(self.index.read_bytes()).hexdigest()
        code, result = self.run_launcher("--prepare")
        self.assertEqual(code, 0)
        self.assertEqual(result["operation"], "unchanged")
        self.assertEqual(sha256(self.index.read_bytes()).hexdigest(), before)

    def test_ready_check_is_read_only_and_never_contacts_models(self):
        self.run_launcher("--prepare")
        before = self.index.read_bytes()
        with patch("versionlens.local_model.LocalModelClient") as generation, patch("versionlens.embeddings.LocalEmbeddingClient") as embedding:
            code, result = self.run_launcher("--check")
        self.assertEqual(code, 0)
        self.assertEqual(result["operation"], "checked")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(self.index.read_bytes(), before)
        generation.assert_not_called()
        embedding.assert_not_called()

    def test_readiness_rejects_wal_before_sqlite_opens_or_changes_sidecars(self):
        self.run_launcher("--prepare")
        connection = sqlite3.connect(self.index)
        try:
            self.assertEqual(connection.execute("PRAGMA journal_mode=WAL").fetchone()[0], "wal")
            connection.execute("UPDATE metadata SET value=value WHERE key='schema_version'")
            connection.commit()
            sidecars = [Path(str(self.index) + suffix) for suffix in ("-wal", "-shm")]
            self.assertTrue(all(path.exists() for path in sidecars))
            paths = [self.index, *sidecars]
            before = {path.name: path.read_bytes() for path in paths}
            with patch("versionlens.vector_store.load_chunks") as load_chunks:
                code, result = self.run_launcher("--check")
            self.assertEqual(code, 2)
            self.assertIn("WAL-mode", result["error"])
            load_chunks.assert_not_called()
            self.assertEqual({path.name: path.read_bytes() for path in paths}, before)
        finally:
            connection.close()

    def test_fresh_source_subprocess_check_creates_no_bytecode_or_other_files(self):
        shutil.copytree(PROJECT / "src", self.root / "src", ignore=shutil.ignore_patterns("__pycache__"))
        (self.root / "scripts").mkdir()
        target = self.root / "scripts/run_local.py"
        shutil.copyfile(PROJECT / "scripts/run_local.py", target)
        before = {str(path.relative_to(self.root)): sha256(path.read_bytes()).hexdigest()
                  for path in self.root.rglob("*") if path.is_file()}
        result = subprocess.run([sys.executable, str(target), "--check"], cwd=self.root.parent,
                                env={"PATH": os.environ.get("PATH", ""), "PYTHONNOUSERSITE": "1"},
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "index_missing")
        self.assertEqual(list(self.root.rglob("__pycache__")), [])
        self.assertEqual({str(path.relative_to(self.root)): sha256(path.read_bytes()).hexdigest()
                          for path in self.root.rglob("*") if path.is_file()}, before)

    def test_corpus_choice_cannot_silently_replace_existing_index(self):
        self.run_launcher("--prepare")
        before = self.index.read_bytes()
        code, result = self.run_launcher("--prepare", "--include-synthetic")
        self.assertEqual(code, 2)
        self.assertIn("--rebuild", result["error"])
        self.assertEqual(self.index.read_bytes(), before)
        code, result = self.run_launcher("--check", "--include-synthetic")
        self.assertEqual(code, 2)
        self.assertEqual(result["reason"], "index_mismatch")
        self.assertEqual(self.index.read_bytes(), before)

    def test_explicit_rebuild_enables_only_the_labelled_demo_corpus(self):
        self.run_launcher("--prepare")
        code, result = self.run_launcher("--prepare", "--include-synthetic", "--rebuild")
        self.assertEqual(code, 0)
        self.assertEqual(result["operation"], "rebuilt")
        self.assertEqual((result["index"]["sources"], result["index"]["chunks"]), (34, 646))
        code, result = self.run_launcher("--check", "--include-synthetic", "--demo-profile", "support")
        self.assertEqual(code, 0)
        self.assertEqual(result["access_profile"], "support")

    def test_changed_source_bytes_fail_before_an_index_is_created(self):
        manifest = json.loads((self.root / "data/sources.json").read_text())
        (self.root / manifest["sources"][0]["path"]).write_text("Changed source without matching digest.")
        code, result = self.run_launcher("--prepare")
        self.assertEqual(code, 2)
        self.assertIn("Checksum mismatch", result["error"])
        self.assertFalse(self.index.exists())

    def test_default_serve_auto_prepares_missing_index_and_passes_trusted_profile(self):
        with patch("versionlens.server.serve", return_value=0) as serve:
            code, _ = self.run_launcher("--port", "8766", "--demo-profile", "support")
        self.assertEqual(code, 0)
        self.assertTrue(self.index.is_file())
        serve.assert_called_once_with(self.index, self.root / "data/versionlens-vectors.sqlite3", 8766, "support")

    def test_unknown_schema_is_preserved_even_with_rebuild(self):
        self.run_launcher("--prepare")
        with connect(self.index) as connection:
            connection.execute("UPDATE metadata SET value='unknown' WHERE key='schema_version'")
            connection.commit()
        before = self.index.read_bytes()
        code, result = self.run_launcher("--prepare", "--rebuild")
        self.assertEqual(code, 2)
        self.assertIn("schema", result["error"].lower())
        self.assertEqual(self.index.read_bytes(), before)

    def test_symlink_index_is_never_followed(self):
        outside = self.root.parent / "outside.sqlite3"
        outside.write_bytes(b"Preserve this file")
        self.index.symlink_to(outside)
        code, result = self.run_launcher("--prepare", "--rebuild")
        self.assertEqual(code, 2)
        self.assertIn("symlink", result["error"])
        self.assertEqual(outside.read_bytes(), b"Preserve this file")

    def test_symlink_data_directory_is_rejected_before_read_or_write(self):
        outside = self.root.parent / "outside-data"
        (self.root / "data").rename(outside)
        (self.root / "data").symlink_to(outside, target_is_directory=True)
        code, result = self.run_launcher("--prepare", "--rebuild")
        self.assertEqual(code, 2)
        self.assertIn("symlink", result["error"])
        self.assertFalse((outside / "versionlens.sqlite3").exists())

    def test_symlink_vector_sidecar_is_rejected_without_reading_it(self):
        outside = self.root.parent / "unrelated-vector-file"
        outside.write_bytes(b"Preserve unrelated bytes")
        (self.root / "data/versionlens-vectors.sqlite3").symlink_to(outside)
        code, result = self.run_launcher("--check")
        self.assertEqual(code, 2)
        self.assertIn("symlink", result["error"])
        self.assertEqual(outside.read_bytes(), b"Preserve unrelated bytes")
        self.assertFalse(self.index.exists())

    def test_invalid_ports_and_read_only_rebuild_combination_are_rejected(self):
        for arguments in (("--port", "80"), ("--port", "65536"), ("--check", "--rebuild")):
            with self.subTest(arguments=arguments), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                launcher.main(list(arguments))
            self.assertEqual(error.exception.code, 2)
        self.assertFalse(self.index.exists())

    def test_interpreter_and_fts5_failures_do_not_write_project_files(self):
        with patch.object(launcher.sys, "version_info", (3, 10)):
            code, result = self.run_launcher("--prepare")
        self.assertEqual(code, 2)
        self.assertIn("3.11", result["error"])
        with patch.object(launcher.sqlite3, "connect", side_effect=sqlite3.OperationalError("No FTS5")):
            code, result = self.run_launcher("--prepare")
        self.assertEqual(code, 2)
        self.assertFalse(self.index.exists())

    def test_absolute_source_script_prepares_from_an_unrelated_working_directory(self):
        shutil.copytree(PROJECT / "src", self.root / "src", ignore=shutil.ignore_patterns("__pycache__"))
        (self.root / "scripts").mkdir()
        target = self.root / "scripts/run_local.py"
        shutil.copyfile(PROJECT / "scripts/run_local.py", target)
        foreign = self.root.parent / "foreign-working-directory"
        foreign.mkdir()
        result = subprocess.run([sys.executable, str(target), "--prepare"], cwd=foreign,
                                env={"PATH": os.environ.get("PATH", ""), "PYTHONNOUSERSITE": "1"},
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["index"]["chunks"], 644)
        self.assertTrue(self.index.is_file())
        self.assertEqual(list(foreign.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
