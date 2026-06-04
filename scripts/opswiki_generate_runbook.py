#!/usr/bin/env python3
"""Generate operational runbooks from Markdown or Obsidian-style notes."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


SHELL_LANGUAGES = {"bash", "shell", "sh", "powershell", "ps1"}

SYMPTOM_SECTION_KEYS = {"symptom", "symptoms"}
CONFIRMED_FACT_SECTION_KEYS = {"confirmed facts"}
ASSUMPTION_SECTION_KEYS = {"assumptions"}
DIAGNOSIS_SECTION_KEYS = {
    "checks",
    "diagnosis",
    "diagnosis steps",
    "read-only checks",
}
RESOLUTION_SECTION_KEYS = {
    "resolution",
    "resolution notes",
    "resolution steps",
    "safer fix order",
}
ROLLBACK_SECTION_KEYS = {"rollback"}
VERIFICATION_SECTION_KEYS = {"verification"}
ESCALATION_SECTION_KEYS = {"escalation"}


class GeneratorError(Exception):
    """Raised when runbook input or output cannot be processed."""


class Note:
    def __init__(
        self,
        *,
        path: str,
        title: str,
        tags: list[str],
        wikilinks: list[str],
        headings: list[tuple[int, str]],
        sections: dict[str, str],
        commands: list[str],
    ) -> None:
        self.path = path
        self.title = title
        self.tags = tags
        self.wikilinks = wikilinks
        self.headings = headings
        self.sections = sections
        self.commands = commands


class RunbookDraft:
    def __init__(
        self,
        *,
        title: str,
        service: str,
        severity: str,
        focus: str | None,
        purpose: list[str],
        scope: list[str],
        symptoms: list[str],
        confirmed_facts: list[str],
        assumptions: list[str],
        safety_checks: list[str],
        diagnosis_steps: list[str],
        resolution_steps: list[str],
        rollback_steps: list[str],
        verification_steps: list[str],
        escalation_steps: list[str],
        commands: list[str],
        related_notes: list[str],
    ) -> None:
        self.title = title
        self.service = service
        self.severity = severity
        self.focus = focus
        self.purpose = purpose
        self.scope = scope
        self.symptoms = symptoms
        self.confirmed_facts = confirmed_facts
        self.assumptions = assumptions
        self.safety_checks = safety_checks
        self.diagnosis_steps = diagnosis_steps
        self.resolution_steps = resolution_steps
        self.rollback_steps = rollback_steps
        self.verification_steps = verification_steps
        self.escalation_steps = escalation_steps
        self.commands = commands
        self.related_notes = related_notes


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def extract_title(path: Path, lines: list[str]) -> str:
    for line in lines:
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return path.stem


def extract_tags(text: str) -> list[str]:
    return unique_preserve_order(re.findall(r"(?<![\w/])#[A-Za-z0-9][A-Za-z0-9_-]*", text))


def extract_wikilinks(text: str) -> list[str]:
    links: list[str] = []
    for raw_link in re.findall(r"\[\[([^\]]+)\]\]", text):
        target = raw_link.split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            links.append(target)
    return unique_preserve_order(links)


def extract_headings_and_sections(lines: list[str]) -> tuple[list[tuple[int, str]], dict[str, str]]:
    headings: list[tuple[int, str]] = []
    sections: dict[str, list[str]] = {}
    current_key: str | None = None

    for line in lines:
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            level = len(match.group(1))
            heading = match.group(2).strip()
            headings.append((level, heading))
            current_key = normalize_heading(heading) if level > 1 else None
            if current_key is not None:
                sections.setdefault(current_key, [])
            continue
        if current_key is not None:
            sections[current_key].append(line)

    return headings, {
        key: "\n".join(value).strip()
        for key, value in sections.items()
        if "\n".join(value).strip()
    }


def extract_commands(lines: list[str]) -> list[str]:
    commands: list[str] = []
    capturing = False
    current: list[str] = []

    for line in lines:
        fence = re.match(r"^```\s*([A-Za-z0-9_-]*)\s*$", line)
        if fence:
            if capturing:
                command = "\n".join(current).strip()
                if command:
                    commands.append(command)
                capturing = False
                current = []
                continue
            language = fence.group(1).lower()
            if language in SHELL_LANGUAGES:
                capturing = True
                current = []
            continue
        if capturing:
            current.append(line)

    return commands


def parse_note(path: Path, text: str) -> Note:
    lines = text.splitlines()
    headings, sections = extract_headings_and_sections(lines)
    return Note(
        path=path.as_posix(),
        title=extract_title(path, lines),
        tags=extract_tags(text),
        wikilinks=extract_wikilinks(text),
        headings=headings,
        sections=sections,
        commands=extract_commands(lines),
    )


def section_items(note: Note, section_keys: set[str]) -> list[str]:
    items: list[str] = []
    for key in section_keys:
        body = note.sections.get(key)
        if body:
            items.extend(markdown_items(body))
    return items


def markdown_items(section_body: str) -> list[str]:
    items: list[str] = []
    paragraph_lines: list[str] = []

    for raw_line in section_body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        bullet = re.match(r"^(?:[-*]|\d+\.)\s+(.+)$", line)
        if bullet:
            items.append(bullet.group(1).strip())
            continue
        if not line.startswith("#"):
            paragraph_lines.append(line)

    if not items and paragraph_lines:
        items.append(" ".join(paragraph_lines).strip())
    return items


def collect_section_items(notes: list[Note], section_keys: set[str]) -> list[str]:
    return unique_preserve_order(item for note in notes for item in section_items(note, section_keys))


def collect_commands(notes: list[Note]) -> list[str]:
    return unique_preserve_order(command for note in notes for command in note.commands)


def build_runbook_draft(
    notes: list[Note],
    title: str | None,
    service: str,
    severity: str | None,
    focus: str | None,
) -> RunbookDraft:
    if not notes:
        raise GeneratorError("No notes were provided.")

    resolved_title = title or notes[0].title
    resolved_severity = severity or "not specified"
    related_notes = unique_preserve_order(
        [note.title for note in notes] + [link for note in notes for link in note.wikilinks]
    )

    return RunbookDraft(
        title=resolved_title,
        service=service,
        severity=resolved_severity,
        focus=focus,
        purpose=[f"Use this runbook when `{resolved_title}` appears in OpsWiki notes."],
        scope=[
            f"Service: {service}",
            f"Severity: {resolved_severity}",
            "Source: local Markdown or Obsidian-style operational notes.",
        ],
        symptoms=collect_section_items(notes, SYMPTOM_SECTION_KEYS)
        or ["Confirm the user-visible symptom and affected service before changing state."],
        confirmed_facts=collect_section_items(notes, CONFIRMED_FACT_SECTION_KEYS)
        or ["No confirmed facts were extracted from source notes."],
        assumptions=collect_section_items(notes, ASSUMPTION_SECTION_KEYS)
        or [
            "Confirm environment, namespace, account, region, and affected workload before running commands."
        ],
        safety_checks=[
            "Start with read-only diagnosis before state-changing commands.",
            "Treat placeholder values such as `<namespace>` and `<pod>` as examples.",
            "Commands are documentation only; do not execute them from this generated runbook.",
        ],
        diagnosis_steps=collect_section_items(notes, DIAGNOSIS_SECTION_KEYS)
        or ["Collect logs, events, recent deployments, and ownership context before remediation."],
        resolution_steps=collect_section_items(notes, RESOLUTION_SECTION_KEYS)
        or ["Document the lowest-risk fix after diagnosis identifies the likely cause."],
        rollback_steps=collect_section_items(notes, ROLLBACK_SECTION_KEYS)
        or ["Confirm rollback target, blast radius, and owner approval before changing state."],
        verification_steps=collect_section_items(notes, VERIFICATION_SECTION_KEYS)
        or ["Verify the original symptom no longer reproduces and no new alerts appear."],
        escalation_steps=collect_section_items(notes, ESCALATION_SECTION_KEYS)
        or ["Escalate to service owners when impact, ownership, or rollback safety is unclear."],
        commands=collect_commands(notes),
        related_notes=related_notes,
    )
