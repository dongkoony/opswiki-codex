# Markdown and Obsidian Context Exporter Design

## Goal

Build the v0.2.0 Markdown and Obsidian context exporter for OpsWiki for Codex. The exporter compiles selected Markdown notes into Codex-ready operational context: a `context-brief.md` and an `AGENTS.md` draft.

## Scope

This release adds a local repository helper, not a Codex app integration and not an MCP server.

In scope:

- Read Markdown files from an input directory.
- Support plain Markdown notes and Obsidian-style `[[wikilink]]` references.
- Extract note title, tags, wikilinks, headings, fenced commands, and useful operational sections.
- Preserve source paths so Codex can trace generated guidance back to notes.
- Generate `context-brief.md`.
- Generate an `AGENTS.md` draft.
- Add tests using the existing sample vault.
- Update README, architecture, roadmap, and examples for v0.2.0 usage.

Out of scope:

- Live Obsidian integration.
- YAML frontmatter schema enforcement.
- Cloud, cluster, CI/CD, or model registry connections.
- Automatic secret scanning beyond conservative text handling in generated output.
- MCP server support.
- Codex app integrations.
- Packaged Python distribution or console entry point.

## Recommended Approach

Use a minimal Python CLI script with only the standard library:

```text
scripts/opswiki_export_context.py
```

The script accepts an input directory and output directory, then writes:

```text
context-brief.md
AGENTS.md
```

This keeps v0.2.0 useful without pulling in packaging, external dependencies, or runtime integration work that belongs in later roadmap items.

## CLI Shape

```bash
python scripts/opswiki_export_context.py \
  --input examples/sample-obsidian-vault \
  --output tmp/opswiki-export
```

Optional flags:

- `--project-name <name>`: defaults to the input directory name.
- `--agents-filename <name>`: defaults to `AGENTS.md`.
- `--context-filename <name>`: defaults to `context-brief.md`.

The command fails with a clear message when:

- the input path does not exist
- the input path is not a directory
- no Markdown files are found
- the output path exists as a file
- an input file cannot be read as UTF-8

## Data Model

Each parsed note should produce a small in-memory object with:

- `path`: relative path from the input root
- `title`: first level-one heading, otherwise filename without extension
- `tags`: Markdown hashtags such as `#aws` and `#runbook`
- `wikilinks`: values inside `[[...]]`
- `headings`: Markdown headings with level and text
- `sections`: heading text mapped to section body
- `commands`: fenced code blocks marked as bash, shell, sh, or powershell

The parser should be intentionally simple and deterministic. It should not try to fully implement Markdown or Obsidian.

## Output: context-brief.md

The context brief should contain:

```markdown
# Context Brief: <project-name>

## Source Index
- `<path>` - <title>; tags: <tags>; links: <wikilinks>

## Confirmed Facts
- From `<path>`: <fact>

## Assumptions
- From `<path>`: <assumption>

## Verification
- From `<path>`:
  ```bash
  <command>
  ```

## Related Notes
- <title> links to [[Other Note]]
```

Facts, assumptions, and verification content should be extracted from sections whose headings match the existing OpsWiki vocabulary:

- confirmed facts
- assumptions
- verification
- checks
- read-only checks
- resolution notes
- diagnosis steps

When no matching section exists, include the note in the Source Index and Related Notes only.

## Output: AGENTS.md Draft

The AGENTS.md draft should contain:

```markdown
# AGENTS.md

## Project Context
- Generated from OpsWiki notes in `<input>`.

## Operational Rules
- Separate confirmed facts from assumptions before proposing infrastructure, deployment, or incident actions.
- Begin incident work with read-only diagnosis before state-changing commands.
- Treat example names, namespaces, accounts, regions, and service identifiers as placeholders unless source notes confirm them.
- Do not include secrets, credentials, private keys, tokens, or personal access keys in commits or generated output.

## Verification Commands
<commands extracted from notes>

## Review Focus
<short bullets inferred from tags and note titles>

## Related OpsWiki Notes
- [[Note Title]]
```

The generated AGENTS.md is a draft. It should be safe to review and copy into a project, but the script should not overwrite an existing project-level AGENTS.md unless the output directory explicitly points there.

## File Structure

Create:

```text
scripts/opswiki_export_context.py
tests/test_opswiki_export_context.py
examples/sample-output/context-brief.md
docs/superpowers/specs/2026-06-04-markdown-obsidian-context-exporter-design.md
```

Modify:

```text
README.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Do not modify:

```text
.codex-plugin/plugin.json
.mcp.json
.app.json
```

The plugin manifest should not gain `mcpServers` or `apps` fields for v0.2.0.

## Testing

Add tests that verify:

- Markdown notes are discovered recursively.
- Titles fall back to filenames when no H1 exists.
- Tags and wikilinks are extracted.
- Operational sections are extracted by heading name.
- Fenced shell commands are captured.
- Missing input directory fails with a non-zero exit.
- Empty input directory fails with a non-zero exit.
- Running against `examples/sample-obsidian-vault` produces both expected output files.

Use Python's standard `unittest` or `pytest` if already available through the local environment. Prefer standard `unittest` if no test framework exists in the repository.

## Safety and Privacy

- Do not invent account IDs, regions, namespaces, resource names, or owners.
- Do not connect to external services.
- Do not execute commands found inside notes.
- Keep generated command blocks as documentation only.
- Preserve source paths in generated output.
- Keep the implementation deterministic so output can be reviewed in diffs.

## Documentation Updates

README should include:

- v0.2.0 exporter purpose
- example CLI command
- expected outputs
- limitations

Architecture should include:

- script-based context compilation as the v0.2.0 implementation
- continued separation from MCP and app integrations

Roadmap should mark v0.2.0 as the current exporter milestone without claiming v0.3.0 work.

## Commit Strategy

Use GitHub Flow on:

```text
feature/v0.2-context-exporter
```

Suggested commits:

```text
docs: add context exporter design
feat: add markdown context exporter
docs: document context exporter workflow
```

Do not include generated-by text, AI attribution, or co-author metadata.
