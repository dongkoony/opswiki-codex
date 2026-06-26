import asyncio
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp" / "opswiki_server.py"


def load_server():
    spec = importlib.util.spec_from_file_location("opswiki_server", SERVER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class OpsWikiIndexTests(unittest.TestCase):
    def test_list_output_artifacts_includes_generated_markdown_outputs(self):
        server = load_server()
        artifacts = server.list_output_artifacts(ROOT)
        by_id = {artifact.id: artifact for artifact in artifacts}

        self.assertEqual(by_id["context-brief"].type, "context_brief")
        self.assertEqual(by_id["agents"].path, "examples/sample-output/AGENTS.md")
        self.assertEqual(by_id["runbook-example"].title, "Runbook: Kubernetes CrashLoopBackOff")
        self.assertEqual(by_id["static-review"].title, "Static Review: sample-infra")

    def test_list_source_notes_extracts_title_tags_and_wikilinks(self):
        server = load_server()
        notes = server.list_source_notes(ROOT)
        by_id = {note.id: note for note in notes}

        note = by_id["kubernetes-crashloopbackoff"]
        self.assertEqual(note.title, "Kubernetes CrashLoopBackOff")
        self.assertIn("#kubernetes", note.tags)
        self.assertIn("Jenkins Docker Permission Denied", note.wikilinks)
        self.assertEqual(
            note.path,
            "examples/sample-obsidian-vault/Kubernetes CrashLoopBackOff.md",
        )

    def test_read_known_output_and_note_by_id(self):
        server = load_server()

        output = server.read_output_artifact(ROOT, "static-review")
        note = server.read_source_note(ROOT, "kubernetes-crashloopbackoff")

        self.assertEqual(output["id"], "static-review")
        self.assertIn("TF_PUBLIC_INGRESS", output["content"])
        self.assertEqual(note["id"], "kubernetes-crashloopbackoff")
        self.assertIn("CrashLoopBackOff", note["content"])


class OpsWikiReadGuardTests(unittest.TestCase):
    def test_read_text_file_rejects_absolute_paths_and_traversal(self):
        server = load_server()

        absolute_path = Path(Path.cwd().anchor) / "outside.md"
        with self.assertRaisesRegex(server.McpServerError, "Unsafe repository path"):
            server.read_text_file(ROOT, absolute_path)

        with self.assertRaisesRegex(server.McpServerError, "Unsafe repository path"):
            server.read_text_file(ROOT, Path("../README.md"))

    def test_read_text_file_rejects_hidden_paths(self):
        server = load_server()

        with self.assertRaisesRegex(server.McpServerError, "Unsafe repository path"):
            server.read_text_file(ROOT, Path(".git/config"))

    def test_read_text_file_rejects_oversized_files(self):
        server = load_server()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            large_file = repo_root / "large.md"
            large_file.write_text("x" * (server.MAX_READ_BYTES + 1), encoding="utf-8")

            with self.assertRaisesRegex(server.McpServerError, "File is too large"):
                server.read_text_file(repo_root, Path("large.md"))

    def test_read_text_file_rejects_non_utf8_files(self):
        server = load_server()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            binary_file = repo_root / "bad.md"
            binary_file.write_bytes(b"\xff\xfe\x00\x00")

            with self.assertRaisesRegex(server.McpServerError, "not valid UTF-8"):
                server.read_text_file(repo_root, Path("bad.md"))


if __name__ == "__main__":
    unittest.main()
