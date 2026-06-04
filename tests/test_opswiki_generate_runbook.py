import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "opswiki_generate_runbook.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("opswiki_generate_runbook", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RunbookParsingTests(unittest.TestCase):
    def test_parse_note_extracts_operational_sections_commands_tags_and_links(self):
        generator = load_generator()
        note = generator.parse_note(
            Path("Kubernetes CrashLoopBackOff.md"),
            """# Kubernetes CrashLoopBackOff

Tags: #kubernetes #triage #runbook

Related: [[Jenkins Docker Permission Denied]]

## Symptoms

- Pod status is `CrashLoopBackOff`.

## Confirmed Facts

- Restart count increases.

## Read-Only Checks

```bash
kubectl get pods -n <namespace>
```

## Resolution Notes

- Fix configuration first when logs show missing settings.
""",
        )

        self.assertEqual(note.title, "Kubernetes CrashLoopBackOff")
        self.assertEqual(note.tags, ["#kubernetes", "#triage", "#runbook"])
        self.assertEqual(note.wikilinks, ["Jenkins Docker Permission Denied"])
        self.assertIn("symptoms", note.sections)
        self.assertIn("confirmed facts", note.sections)
        self.assertIn("read-only checks", note.sections)
        self.assertEqual(note.commands, ["kubectl get pods -n <namespace>"])

    def test_build_runbook_draft_maps_sections_with_safe_defaults(self):
        generator = load_generator()
        note = generator.parse_note(
            Path("No Rollback.md"),
            """# No Rollback

## Confirmed Facts

- A confirmed fact exists.
""",
        )

        draft = generator.build_runbook_draft(
            [note],
            title="No Rollback",
            service="Example service",
            severity=None,
            focus=None,
        )

        self.assertEqual(draft.title, "No Rollback")
        self.assertIn("A confirmed fact exists.", "\n".join(draft.confirmed_facts))
        self.assertTrue(any("Confirm rollback" in item for item in draft.rollback_steps))
        self.assertTrue(draft.safety_checks)
