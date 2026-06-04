#!/usr/bin/env python3
"""Export Markdown or Obsidian-style notes into OpsWiki context outputs."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable


SHELL_LANGUAGES = {"bash", "shell", "sh", "powershell", "ps1"}
FACT_SECTION_KEYS = {"confirmed facts"}
ASSUMPTION_SECTION_KEYS = {"assumptions"}
VERIFICATION_SECTION_KEYS = {
    "checks",
    "diagnosis steps",
    "read-only checks",
    "verification",
}


class ExportError(Exception):
    """Raised when export input or output cannot be processed."""


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


def discover_markdown_files(input_root: Path) -> list[Path]:
    return sorted(
        (path for path in input_root.rglob("*.md") if path.is_file()),
        key=lambda path: path.relative_to(input_root).as_posix().lower(),
    )


def load_notes(input_root: Path) -> list[Note]:
    if not input_root.exists():
        raise ExportError(f"Input path '{input_root}' does not exist.")
    if not input_root.is_dir():
        raise ExportError(f"Input path '{input_root}' is not a directory.")

    markdown_files = discover_markdown_files(input_root)
    if not markdown_files:
        raise ExportError(f"No Markdown files found in '{input_root}'.")

    notes: list[Note] = []
    for path in markdown_files:
        relative_path = path.relative_to(input_root)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ExportError(f"Input file '{relative_path}' is not valid UTF-8.") from exc
        notes.append(parse_note(relative_path, text))
    return notes


def bullet_lines(section_body: str) -> list[str]:
    values: list[str] = []
    for raw_line in section_body.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            values.append(line)
        elif re.match(r"^\d+\.\s+", line):
            values.append(f"- {line}")
    return values


def section_bullets(note: Note, section_keys: set[str]) -> list[str]:
    values: list[str] = []
    for key in section_keys:
        body = note.sections.get(key)
        if body:
            values.extend(bullet_lines(body))
    return values


def render_source_index(notes: list[Note]) -> list[str]:
    lines = ["## Source Index"]
    for note in notes:
        tags = ", ".join(note.tags) if note.tags else "none"
        links = ", ".join(f"[[{link}]]" for link in note.wikilinks) if note.wikilinks else "none"
        lines.append(f"- `{note.path}` - {note.title}; tags: {tags}; links: {links}")
    return lines


def render_extracted_bullets(
    notes: list[Note],
    *,
    title: str,
    section_keys: set[str],
    empty_message: str,
) -> list[str]:
    lines = [f"## {title}"]
    found = False
    for note in notes:
        for bullet in section_bullets(note, section_keys):
            lines.append(f"- From `{note.path}`: {bullet.removeprefix('- ').strip()}")
            found = True
    if not found:
        lines.append(f"- {empty_message}")
    return lines


def render_verification(notes: list[Note]) -> list[str]:
    lines = ["## Verification"]
    found = False
    for note in notes:
        if not note.commands:
            continue
        lines.append(f"- From `{note.path}`:")
        for command in note.commands:
            lines.extend(["", "  ```bash"])
            lines.extend(f"  {line}" for line in command.splitlines())
            lines.append("  ```")
        found = True
    if not found:
        lines.append("- No shell commands extracted from source notes.")
    return lines


def render_related_notes(notes: list[Note]) -> list[str]:
    lines = ["## Related Notes"]
    found = False
    for note in notes:
        for link in note.wikilinks:
            lines.append(f"- {note.title} links to [[{link}]]")
            found = True
    if not found:
        lines.append("- No wikilinks extracted from source notes.")
    return lines


def render_context_brief(project_name: str, notes: list[Note]) -> str:
    sections = [
        [f"# Context Brief: {project_name}"],
        render_source_index(notes),
        render_extracted_bullets(
            notes,
            title="Confirmed Facts",
            section_keys=FACT_SECTION_KEYS,
            empty_message="No confirmed facts extracted from source notes.",
        ),
        render_extracted_bullets(
            notes,
            title="Assumptions",
            section_keys=ASSUMPTION_SECTION_KEYS,
            empty_message="No assumptions extracted from source notes.",
        ),
        render_verification(notes),
        render_related_notes(notes),
    ]
    return "\n\n".join("\n".join(section) for section in sections) + "\n"


def collect_commands(notes: list[Note]) -> list[str]:
    return unique_preserve_order(command for note in notes for command in note.commands)


def infer_review_focus(notes: list[Note]) -> list[str]:
    tag_text = " ".join(tag.lower() for note in notes for tag in note.tags)
    title_text = " ".join(note.title.lower() for note in notes)
    combined = f"{tag_text} {title_text}"
    focus: list[str] = []
    if "terraform" in combined or "#aws" in combined:
        focus.append("Terraform and AWS: IAM scope, public ingress, state impact, and ownership tags.")
    if "kubernetes" in combined:
        focus.append("Kubernetes: pod state, rollout status, probes, events, and rollback path.")
    if "jenkins" in combined or "ci-cd" in combined or "docker" in combined:
        focus.append("CI/CD: credentials, Docker access, deployment gates, artifacts, and logs.")
    if "mlops" in combined or "model" in combined:
        focus.append("MLOps: artifact version, schema compatibility, rollout metrics, and rollback target.")
    if not focus:
        focus.append("OpsWiki notes: preserve source facts, assumptions, verification steps, and related notes.")
    return focus


def render_agents(project_name: str, input_root: Path, notes: list[Note]) -> str:
    commands = collect_commands(notes)
    note_titles = unique_preserve_order(note.title for note in notes)

    lines = [
        "# AGENTS.md",
        "",
        "## Project Context",
        f"- Generated from OpsWiki notes in `{input_root.as_posix()}` for `{project_name}`.",
        "",
        "## Operational Rules",
        "- Separate confirmed facts from assumptions before proposing infrastructure, deployment, or incident actions.",
        "- Begin incident work with read-only diagnosis before state-changing commands.",
        "- Treat example names, namespaces, accounts, regions, and service identifiers as placeholders unless source notes confirm them.",
        "- Do not include secrets, credentials, private keys, tokens, or personal access keys in commits or generated output.",
        "",
        "## Verification Commands",
    ]
    if commands:
        for command in commands:
            lines.extend(["", "```bash"])
            lines.extend(command.splitlines())
            lines.append("```")
    else:
        lines.append("- No shell commands extracted from source notes.")

    lines.extend(["", "## Review Focus"])
    lines.extend(f"- {item}" for item in infer_review_focus(notes))
    lines.extend(["", "## Related OpsWiki Notes"])
    lines.extend(f"- [[{title}]]" for title in note_titles)
    return "\n".join(lines) + "\n"


def export_context(
    *,
    input_root: Path,
    output_root: Path,
    project_name: str | None = None,
    agents_filename: str = "AGENTS.md",
    context_filename: str = "context-brief.md",
) -> tuple[Path, Path]:
    notes = load_notes(input_root)
    if output_root.exists() and output_root.is_file():
        raise ExportError(f"Output path '{output_root}' exists as a file.")
    output_root.mkdir(parents=True, exist_ok=True)

    resolved_project_name = project_name or input_root.name
    context_path = output_root / context_filename
    agents_path = output_root / agents_filename
    context_path.write_text(render_context_brief(resolved_project_name, notes), encoding="utf-8")
    agents_path.write_text(
        render_agents(resolved_project_name, input_root, notes),
        encoding="utf-8",
    )
    return context_path, agents_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export Markdown or Obsidian-style notes into OpsWiki context outputs."
    )
    parser.add_argument("--input", required=True, help="Input directory containing Markdown notes.")
    parser.add_argument("--output", required=True, help="Output directory for generated files.")
    parser.add_argument("--project-name", help="Project name to use in generated outputs.")
    parser.add_argument(
        "--agents-filename",
        default="AGENTS.md",
        help="Generated AGENTS filename inside the output directory.",
    )
    parser.add_argument(
        "--context-filename",
        default="context-brief.md",
        help="Generated context brief filename inside the output directory.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        context_path, agents_path = export_context(
            input_root=Path(args.input),
            output_root=Path(args.output),
            project_name=args.project_name,
            agents_filename=args.agents_filename,
            context_filename=args.context_filename,
        )
    except ExportError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Wrote {context_path}")
    print(f"Wrote {agents_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
