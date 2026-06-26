# MCP Integration Design

## Summary

v0.5.0 adds optional local MCP integration for OpsWiki for Codex. The MCP layer exposes existing local knowledge outputs and source notes to Codex through a controlled, read-only interface.

This feature continues the existing OpsWiki pattern:

- v0.2.0: local Markdown context exporter
- v0.3.0: local runbook generator
- v0.4.0: local static review helper
- v0.5.0: optional local MCP access to generated outputs and local knowledge sources

The MCP server does not replace the existing scripts. It gives Codex a structured way to list and read local notes and generated artifacts that already live in the repository.

## Goals

- Add optional MCP configuration for the plugin.
- Add one local MCP server that can be launched by Codex.
- Expose read-only access to generated OpsWiki outputs:
  - context briefs
  - generated `AGENTS.md`
  - generated runbooks
  - static review reports
- Expose read-only access to local Markdown source notes.
- Keep v0.2 exporter, v0.3 runbook generator, and v0.4 static review helper behavior unchanged.
- Keep the first MCP release deterministic, local-only, and testable.
- Keep plugin installation useful without MCP when the user only wants skills and scripts.

## Non-Goals

- No cloud account access.
- No Kubernetes API server access.
- No CI/CD API access.
- No model registry access.
- No live Obsidian API integration.
- No execution of `terraform`, `tofu`, `kubectl`, cloud CLIs, scanners, or shell commands.
- No mutation tools in v0.5.0.
- No MCP tool that writes files, edits notes, regenerates outputs, commits changes, or opens pull requests.
- No app integration through `.app.json`.
- No replacement of existing CLI scripts.

## Best-Practice Basis

MCP should expose a narrow capability surface with explicit boundaries. For OpsWiki, the safest first capability is a read-only local index over known repository paths.

The design follows these guardrails:

- Read-only MCP resources are easier to review, test, and reason about than mutation tools.
- Repository-relative paths are safer and more portable than arbitrary filesystem paths.
- Existing scripts remain the source of generation behavior; MCP only surfaces their outputs.
- Production and provider integrations require separate authentication, safety, and audit design, so they remain outside v0.5.0.

## User Workflow

The user installs or loads the plugin in Codex. When MCP is enabled, Codex can discover local OpsWiki resources through the MCP server.

Expected Codex usage:

```text
Use OpsWiki MCP to list generated outputs.
Read the static review report for this repository.
Read the Kubernetes CrashLoopBackOff source note.
Summarize the generated runbook and cite the source artifact.
```

The user can still run existing scripts directly:

```powershell
uv run python scripts/opswiki_export_context.py --input examples/sample-obsidian-vault --output examples/sample-output --project-name sample-obsidian-vault
uv run python scripts/opswiki_generate_runbook.py --input examples/sample-obsidian-vault --output examples/sample-output/runbook-example.md --title "Kubernetes CrashLoopBackOff" --service "sample-obsidian-vault" --severity "SEV3" --focus "kubernetes"
uv run --with pyyaml python scripts/opswiki_static_review.py --input examples/sample-infra --output examples/sample-output/static-review.md --project-name sample-infra
```

The MCP server reads the generated files after those scripts have produced them. It does not run the scripts in v0.5.0.

## Dependency Strategy

The repository currently avoids a package manifest and uses standard-library Python for existing v0.2 and v0.3 scripts, with PyYAML supplied through `uv --with pyyaml` for v0.4 Kubernetes parsing.

v0.5.0 should keep that lightweight pattern:

- Use Python standard library for indexing and file reads.
- Use the official MCP Python SDK package, `mcp`, for server transport and tool/resource registration.
- Do not add Terraform, Kubernetes, cloud, CI, or Obsidian SDK dependencies.
- Do not introduce a lockfile unless the chosen MCP package requires a stable executable environment.

Implementation should use this server command strategy:

- `uv run --with mcp python mcp/opswiki_server.py`

Do not add `pyproject.toml`, `requirements.txt`, or a lockfile in v0.5.0 unless implementation verification proves that `uv run --with mcp ...` cannot launch reliably.

## File Structure

Create:

- `.mcp.json`
- `mcp/opswiki_server.py`
- `tests/test_opswiki_mcp_server.py`
- `docs/superpowers/plans/2026-06-26-v0.5-mcp-integration-implementation.md`

Modify:

- `.codex-plugin/plugin.json`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

Do not create:

- `.app.json`
- app definitions
- provider credential files
- cloud, cluster, CI, or model registry configuration

## MCP Configuration

`.mcp.json` should define one local server entry for OpsWiki. The server command must be local and repository-scoped.

Expected shape:

```json
{
  "mcpServers": {
    "opswiki": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp",
        "python",
        "mcp/opswiki_server.py"
      ]
    }
  }
}
```

The MCP package name is fixed to `mcp`, the official Python SDK package.

`.codex-plugin/plugin.json` should add `mcpServers` only when `.mcp.json` exists and validation confirms the companion file is present.

The plugin version should update only after the MCP implementation and docs are verified:

```json
"version": "0.5.0"
```

## Server Boundary

The server root is the repository root. The server may read only files under the repository root.

Allowed source directories:

- `examples/sample-obsidian-vault/`
- `examples/sample-output/`
- `docs/`

Allowed generated output files:

- `examples/sample-output/context-brief.md`
- `examples/sample-output/AGENTS.md`
- `examples/sample-output/runbook-example.md`
- `examples/sample-output/static-review.md`

Allowed source note files:

- Markdown files under `examples/sample-obsidian-vault/`

The server must reject:

- absolute paths supplied by clients
- `..` path traversal
- paths outside the repository root after resolution
- hidden `.git/` paths
- plugin metadata files unless specifically exposed by a resource
- binary files
- files larger than the configured maximum read size

Recommended maximum read size:

```text
256 KiB per file
```

This limit keeps MCP responses predictable and avoids accidentally streaming large local artifacts.

## MCP Resources

The server should expose resources with stable URI shapes.

### Generated Outputs Index

URI:

```text
opswiki://outputs
```

Content:

- JSON or Markdown index of generated output artifacts
- artifact id
- artifact type
- relative path
- title when extractable
- size in bytes
- last modified timestamp if available from local filesystem

### Generated Output Artifact

URI shape:

```text
opswiki://outputs/<artifact-id>
```

Artifact ids:

- `context-brief`
- `agents`
- `runbook-example`
- `static-review`

Content:

- Markdown file content
- Metadata header or separate resource metadata with artifact type and path

### Source Notes Index

URI:

```text
opswiki://notes
```

Content:

- JSON or Markdown index of source notes
- note id
- relative path
- title
- tags
- wikilinks

### Source Note

URI shape:

```text
opswiki://notes/<note-id>
```

Note ids should be deterministic slugs derived from relative paths. For example:

```text
examples/sample-obsidian-vault/Kubernetes CrashLoopBackOff.md
```

becomes:

```text
kubernetes-crashloopbackoff
```

If two notes produce the same slug, append a short stable suffix derived from the relative path.

## MCP Tools

v0.5.0 should include read-only tools only. Tools return structured data and never modify files.

### `list_opswiki_outputs`

Input:

```json
{}
```

Output:

```json
{
  "outputs": [
    {
      "id": "static-review",
      "type": "static_review",
      "path": "examples/sample-output/static-review.md",
      "title": "Static Review: sample-infra"
    }
  ]
}
```

Behavior:

- Lists only supported generated artifacts.
- Omits missing artifacts instead of failing the whole request.
- Includes an empty array when no outputs are present.

### `read_opswiki_output`

Input:

```json
{
  "id": "static-review"
}
```

Output:

```json
{
  "id": "static-review",
  "type": "static_review",
  "path": "examples/sample-output/static-review.md",
  "content": "# Static Review: sample-infra\n..."
}
```

Behavior:

- Reads only known output ids.
- Returns a clear error for unknown ids.
- Does not accept arbitrary file paths.

### `list_opswiki_notes`

Input:

```json
{}
```

Output:

```json
{
  "notes": [
    {
      "id": "kubernetes-crashloopbackoff",
      "path": "examples/sample-obsidian-vault/Kubernetes CrashLoopBackOff.md",
      "title": "Kubernetes CrashLoopBackOff",
      "tags": ["#kubernetes", "#triage", "#runbook"],
      "wikilinks": ["Jenkins Docker Permission Denied"]
    }
  ]
}
```

Behavior:

- Discovers Markdown notes under the configured source note directory.
- Reuses the same title, tag, and wikilink extraction semantics as `scripts/opswiki_export_context.py`.
- Does not parse shell commands into executable actions.

### `read_opswiki_note`

Input:

```json
{
  "id": "kubernetes-crashloopbackoff"
}
```

Output:

```json
{
  "id": "kubernetes-crashloopbackoff",
  "path": "examples/sample-obsidian-vault/Kubernetes CrashLoopBackOff.md",
  "title": "Kubernetes CrashLoopBackOff",
  "content": "# Kubernetes CrashLoopBackOff\n..."
}
```

Behavior:

- Reads only known note ids.
- Returns a clear error for unknown ids.
- Preserves source content without rewriting.

## Internal Model

Use small plain Python classes or dataclasses:

- `McpServerError`
- `OpsWikiArtifact`
- `OpsWikiNote`
- `OpsWikiIndex`

Suggested fields:

```text
OpsWikiArtifact
- id
- type
- path
- title
- size_bytes

OpsWikiNote
- id
- path
- title
- tags
- wikilinks
- size_bytes
```

The MCP server should keep indexing logic separate from transport registration so unit tests can verify behavior without launching a full MCP process.

Suggested modules:

- `mcp/opswiki_server.py`: server registration and CLI entry point
- within the same file for v0.5.0: local index helpers and read guards

If the implementation grows beyond one focused file, split only when tests show the server file is doing unrelated work.

## Data Flow

1. MCP server starts from repository root.
2. Server builds an allowlisted artifact registry for generated outputs.
3. Server scans allowed source note directories for Markdown files.
4. Server derives stable ids and metadata.
5. Client lists resources or calls read-only tools.
6. Server validates requested ids against the registry.
7. Server reads UTF-8 text with file size limits.
8. Server returns structured JSON or resource content.

## Error Handling

Errors should be explicit and safe:

- Missing generated output: omit from list; return not found when requested directly.
- Missing source note directory: return an empty note list.
- Invalid id: return a clear unknown id error.
- Non-UTF-8 file: return an unsupported encoding error.
- Oversized file: return a file too large error.
- Path traversal attempt: return invalid id or forbidden path without echoing host-specific absolute paths.
- MCP package import failure: print a clear setup error in server startup.

Error messages must not reveal secrets or arbitrary absolute host paths. Repository-relative paths are acceptable.

## Security and Safety

v0.5.0 safety requirements:

- All operations are read-only.
- All reads are repository-root confined.
- No subprocess execution from MCP tools.
- No shell command extraction is treated as executable.
- No external network calls.
- No credentials or environment secrets are read.
- Hidden directories such as `.git/` are not exposed.
- MCP resource names and tool output should use repository-relative paths.

The MCP server should document that source notes and generated reports may still contain sensitive content if the user wrote it there. The server controls where it reads from; it does not sanitize the content itself.

## Testing Strategy

Use `unittest`, matching the existing repository test style.

Unit tests:

- Lists known generated outputs when sample files exist.
- Omits missing generated outputs without failing list operations.
- Reads a known generated output by id.
- Rejects an unknown output id.
- Lists sample Obsidian notes with title, tags, and wikilinks.
- Reads a known source note by id.
- Rejects an unknown note id.
- Rejects traversal-like ids.
- Rejects oversized files when a test fixture exceeds the configured maximum read size.

Optional transport smoke test:

- Import the MCP server module.
- Verify registered resource and tool names if the chosen MCP framework exposes inspectable registration.

Full verification:

```powershell
uv run --with pyyaml --with mcp python -m unittest discover -s tests -v
uv run --with pyyaml --with mcp python C:\Users\dongh\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py C:\Users\dongh\iCloudDrive\opswiki-codex
git diff --check
git diff -- .app.json
git diff -- .codex-plugin/plugin.json
```

Expected:

- all tests pass
- plugin validation passes
- no whitespace errors
- no `.app.json` diff
- plugin manifest diff includes version `0.5.0` and MCP metadata only after `.mcp.json` exists

## Documentation Updates

README should document:

- v0.5.0 optional MCP purpose
- how to enable the MCP server in Codex
- available read-only resources and tools
- local-only behavior
- no command execution or external connections

Architecture should document:

- MCP as an optional read-only layer over existing scripts and outputs
- repository-root read confinement
- why generation remains in CLI scripts for v0.5.0
- future mutation or provider integration requirements

Roadmap should mark v0.5.0 implemented only after tests and plugin validation pass.

## Backlog Outside v0.5.0

- MCP tools that generate context briefs, runbooks, or static review reports.
- Writable note management through MCP.
- Live Obsidian integration.
- Cloud provider, Kubernetes, CI/CD, or model registry integrations.
- Authenticated provider adapters.
- Remote repository indexing.
- Large artifact pagination or streaming.

## Acceptance Criteria

- `.mcp.json` exists and defines one local OpsWiki MCP server.
- Plugin manifest references MCP only when `.mcp.json` exists.
- MCP server exposes read-only resources for generated outputs and source notes.
- MCP server exposes read-only tools for listing and reading generated outputs and source notes.
- The server rejects arbitrary paths and traversal attempts.
- The server reads local repository files only.
- The server does not execute external commands.
- Existing v0.2, v0.3, and v0.4 tests continue to pass.
- MCP tests cover indexing, reads, missing files, invalid ids, and path safety.
- Plugin validation passes.
