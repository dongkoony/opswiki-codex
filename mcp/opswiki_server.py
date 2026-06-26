#!/usr/bin/env python3
"""Expose local OpsWiki outputs and notes through a read-only MCP server."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from hashlib import sha1
from pathlib import Path
from typing import Iterable

from mcp.server.fastmcp import FastMCP


REPO_ROOT = Path(__file__).resolve().parents[1]
MAX_READ_BYTES = 256 * 1024
NOTE_ROOT = Path("examples/sample-obsidian-vault")

OUTPUT_ARTIFACTS = {
    "context-brief": {
        "type": "context_brief",
        "path": Path("examples/sample-output/context-brief.md"),
    },
    "agents": {
        "type": "agents",
        "path": Path("examples/sample-output/AGENTS.md"),
    },
    "runbook-example": {
        "type": "runbook",
        "path": Path("examples/sample-output/runbook-example.md"),
    },
    "static-review": {
        "type": "static_review",
        "path": Path("examples/sample-output/static-review.md"),
    },
}


class McpServerError(Exception):
    """Raised when an OpsWiki MCP request cannot be served safely."""


@dataclass(frozen=True)
class OpsWikiArtifact:
    id: str
    type: str
    path: str
    title: str
    size_bytes: int


@dataclass(frozen=True)
class OpsWikiNote:
    id: str
    path: str
    title: str
    tags: list[str]
    wikilinks: list[str]
    size_bytes: int


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def validate_relative_path(relative_path: Path) -> None:
    if relative_path.is_absolute():
        raise McpServerError("Unsafe repository path.")
    if ".." in relative_path.parts:
        raise McpServerError("Unsafe repository path.")
    if any(part.startswith(".") for part in relative_path.parts):
        raise McpServerError("Unsafe repository path.")


def resolve_repo_path(repo_root: Path, relative_path: Path) -> Path:
    validate_relative_path(relative_path)
    root = repo_root.resolve()
    resolved = (root / relative_path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise McpServerError("Unsafe repository path.") from exc
    return resolved


def read_text_file(repo_root: Path, relative_path: Path) -> str:
    path = resolve_repo_path(repo_root, relative_path)
    if not path.is_file():
        raise McpServerError(f"File not found: {relative_path.as_posix()}")
    size_bytes = path.stat().st_size
    if size_bytes > MAX_READ_BYTES:
        raise McpServerError(f"File is too large: {relative_path.as_posix()}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise McpServerError(f"File is not valid UTF-8: {relative_path.as_posix()}") from exc


def extract_title(path: Path, text: str) -> str:
    for line in text.splitlines():
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


def slugify_note_path(relative_path: Path) -> str:
    stem = relative_path.stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return slug or sha1(relative_path.as_posix().encode("utf-8")).hexdigest()[:8]


def discover_markdown_notes(repo_root: Path) -> list[Path]:
    note_root = repo_root / NOTE_ROOT
    if not note_root.is_dir():
        return []
    return sorted(
        (path.relative_to(repo_root) for path in note_root.rglob("*.md") if path.is_file()),
        key=lambda item: item.as_posix().lower(),
    )


def stable_note_ids(relative_paths: list[Path]) -> dict[Path, str]:
    counts: dict[str, int] = {}
    for path in relative_paths:
        slug = slugify_note_path(path)
        counts[slug] = counts.get(slug, 0) + 1

    ids: dict[Path, str] = {}
    for path in relative_paths:
        slug = slugify_note_path(path)
        if counts[slug] == 1:
            ids[path] = slug
            continue
        suffix = sha1(path.as_posix().encode("utf-8")).hexdigest()[:8]
        ids[path] = f"{slug}-{suffix}"
    return ids


def list_output_artifacts(repo_root: Path = REPO_ROOT) -> list[OpsWikiArtifact]:
    artifacts: list[OpsWikiArtifact] = []
    for artifact_id, metadata in OUTPUT_ARTIFACTS.items():
        relative_path = metadata["path"]
        path = repo_root / relative_path
        if not path.is_file():
            continue
        text = read_text_file(repo_root, relative_path)
        artifacts.append(
            OpsWikiArtifact(
                id=artifact_id,
                type=str(metadata["type"]),
                path=relative_path.as_posix(),
                title=extract_title(relative_path, text),
                size_bytes=path.stat().st_size,
            )
        )
    return artifacts


def list_source_notes(repo_root: Path = REPO_ROOT) -> list[OpsWikiNote]:
    relative_paths = discover_markdown_notes(repo_root)
    ids = stable_note_ids(relative_paths)
    notes: list[OpsWikiNote] = []
    for relative_path in relative_paths:
        path = repo_root / relative_path
        text = read_text_file(repo_root, relative_path)
        notes.append(
            OpsWikiNote(
                id=ids[relative_path],
                path=relative_path.as_posix(),
                title=extract_title(relative_path, text),
                tags=extract_tags(text),
                wikilinks=extract_wikilinks(text),
                size_bytes=path.stat().st_size,
            )
        )
    return notes


def artifact_by_id(repo_root: Path, artifact_id: str) -> OpsWikiArtifact:
    for artifact in list_output_artifacts(repo_root):
        if artifact.id == artifact_id:
            return artifact
    raise McpServerError(f"Unknown OpsWiki output id: {artifact_id}")


def note_by_id(repo_root: Path, note_id: str) -> OpsWikiNote:
    for note in list_source_notes(repo_root):
        if note.id == note_id:
            return note
    raise McpServerError(f"Unknown OpsWiki note id: {note_id}")


def read_output_artifact(repo_root: Path, artifact_id: str) -> dict[str, object]:
    artifact = artifact_by_id(repo_root, artifact_id)
    content = read_text_file(repo_root, Path(artifact.path))
    data = asdict(artifact)
    data["content"] = content
    return data


def read_source_note(repo_root: Path, note_id: str) -> dict[str, object]:
    note = note_by_id(repo_root, note_id)
    content = read_text_file(repo_root, Path(note.path))
    data = asdict(note)
    data["content"] = content
    return data


def json_dumps(data: object) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def artifact_payload(artifact: OpsWikiArtifact) -> dict[str, object]:
    return asdict(artifact)


def note_payload(note: OpsWikiNote) -> dict[str, object]:
    return asdict(note)


def create_server(repo_root: Path = REPO_ROOT) -> FastMCP:
    app = FastMCP(
        "opswiki",
        instructions=(
            "Read-only access to local OpsWiki sample notes and generated outputs. "
            "This server does not execute commands or contact external systems."
        ),
    )

    @app.tool()
    def list_opswiki_outputs() -> dict[str, object]:
        """List generated OpsWiki output artifacts available in this repository."""
        return {
            "outputs": [
                artifact_payload(artifact)
                for artifact in list_output_artifacts(repo_root)
            ]
        }

    @app.tool()
    def read_opswiki_output(id: str) -> dict[str, object]:
        """Read one generated OpsWiki output artifact by stable id."""
        return read_output_artifact(repo_root, id)

    @app.tool()
    def list_opswiki_notes() -> dict[str, object]:
        """List local OpsWiki source notes available in this repository."""
        return {
            "notes": [
                note_payload(note)
                for note in list_source_notes(repo_root)
            ]
        }

    @app.tool()
    def read_opswiki_note(id: str) -> dict[str, object]:
        """Read one local OpsWiki source note by stable id."""
        return read_source_note(repo_root, id)

    @app.resource(
        "opswiki://outputs",
        name="OpsWiki generated outputs",
        mime_type="application/json",
    )
    def outputs_resource() -> str:
        return json_dumps(list_opswiki_outputs())

    @app.resource(
        "opswiki://notes",
        name="OpsWiki source notes",
        mime_type="application/json",
    )
    def notes_resource() -> str:
        return json_dumps(list_opswiki_notes())

    @app.resource(
        "opswiki://outputs/{artifact_id}",
        name="OpsWiki generated output",
        mime_type="text/markdown",
    )
    def output_resource(artifact_id: str) -> str:
        return str(read_output_artifact(repo_root, artifact_id)["content"])

    @app.resource(
        "opswiki://notes/{note_id}",
        name="OpsWiki source note",
        mime_type="text/markdown",
    )
    def note_resource(note_id: str) -> str:
        return str(read_source_note(repo_root, note_id)["content"])

    return app


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
