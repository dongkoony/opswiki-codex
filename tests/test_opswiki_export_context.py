import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "opswiki_export_context.py"


def load_exporter():
    spec = importlib.util.spec_from_file_location("opswiki_export_context", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MarkdownParsingTests(unittest.TestCase):
    def test_parse_note_extracts_title_tags_wikilinks_sections_and_commands(self):
        exporter = load_exporter()
        note = exporter.parse_note(
            Path("Kubernetes CrashLoopBackOff.md"),
            """# Kubernetes CrashLoopBackOff

Tags: #kubernetes #triage #runbook

Related: [[Jenkins Docker Permission Denied]]

## Confirmed Facts

- Restart count increases.

## Read-Only Checks

```bash
kubectl get pods -n <namespace>
```
""",
        )

        self.assertEqual(note.title, "Kubernetes CrashLoopBackOff")
        self.assertEqual(note.tags, ["#kubernetes", "#triage", "#runbook"])
        self.assertEqual(note.wikilinks, ["Jenkins Docker Permission Denied"])
        self.assertIn("confirmed facts", note.sections)
        self.assertIn("- Restart count increases.", note.sections["confirmed facts"])
        self.assertEqual(note.commands, ["kubectl get pods -n <namespace>"])

    def test_title_falls_back_to_filename_without_h1(self):
        exporter = load_exporter()
        note = exporter.parse_note(Path("No Heading.md"), "Tags: #aws\n")

        self.assertEqual(note.title, "No Heading")


class ExportCliTests(unittest.TestCase):
    def test_sample_vault_export_writes_context_brief_and_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "export"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(ROOT / "examples" / "sample-obsidian-vault"),
                    "--output",
                    str(output),
                    "--project-name",
                    "sample-opswiki",
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            context = (output / "context-brief.md").read_text(encoding="utf-8")
            agents = (output / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("# Context Brief: sample-opswiki", context)
            self.assertIn("Kubernetes CrashLoopBackOff", context)
            self.assertIn("kubectl get pods -n <namespace>", agents)

    def test_missing_input_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(Path(tmp) / "missing"),
                    "--output",
                    str(Path(tmp) / "out"),
                ],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not exist", result.stderr)

    def test_empty_input_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    tmp,
                    "--output",
                    str(Path(tmp) / "out"),
                ],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("No Markdown files", result.stderr)

    def test_output_path_as_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_file = Path(tmp) / "output-file"
            output_file.write_text("not a directory", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(ROOT / "examples" / "sample-obsidian-vault"),
                    "--output",
                    str(output_file),
                ],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exists as a file", result.stderr)


if __name__ == "__main__":
    unittest.main()
