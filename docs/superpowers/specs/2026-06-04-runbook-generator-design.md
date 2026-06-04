# Runbook Generator Design

## Goal

Build the v0.3.0 runbook generator for OpsWiki for Codex. The generator turns structured Markdown notes, incident summaries, or v0.2 context exports into practical operational runbooks.

## Scope

This release adds a local repository helper script. It does not add a Codex app integration, MCP server, cloud connector, cluster connector, CI connector, or model registry connector.

In scope:

- Read Markdown files from an input directory.
- Accept either raw operational notes or v0.2 exporter output.
- Extract operational sections that already exist in OpsWiki notes.
- Generate one runbook Markdown file.
- Keep confirmed facts, assumptions, diagnosis, resolution, rollback, verification, escalation, and related notes clearly separated.
- Add tests using the existing sample vault and sample context output.
- Refresh `examples/sample-output/runbook-example.md`.
- Update README, architecture, roadmap, and plugin version metadata for v0.3.0.

Out of scope:

- Running shell commands from notes.
- Connecting to Kubernetes, AWS, Jenkins, GitHub Actions, Terraform, model registries, or monitoring tools.
- Automatic incident timeline reconstruction from external systems.
- YAML frontmatter schema enforcement.
- Multiple runbook generation modes beyond a single deterministic Markdown output.
- MCP server support.
- Codex app integrations.
- Packaged Python distribution or console entry point.

## Recommended Approach

Create a separate standard-library Python CLI:

```text
scripts/opswiki_generate_runbook.py
```

Keep it separate from `scripts/opswiki_export_context.py` so v0.2 context export and v0.3 runbook generation remain easy to understand and test independently.

The script accepts an input directory and an output file:

```powershell
uv run python scripts/opswiki_generate_runbook.py --input examples/sample-obsidian-vault --output examples/sample-output/runbook-example.md --title "Kubernetes CrashLoopBackOff"
```

Optional flags:

- `--title`: runbook title; defaults to the first discovered note title.
- `--service`: service or system name; defaults to `OpsWiki notes`.
- `--severity`: optional severity label such as `SEV3`.
- `--focus`: optional text used to prioritize matching notes by title, tag, or wikilink.

The command fails with a clear message when:

- the input path does not exist
- the input path is not a directory
- no Markdown files are found
- the output path exists as a directory
- an input file cannot be read as UTF-8

## Data Model

The generator can share parsing ideas with the v0.2 exporter but should remain self-contained for v0.3 unless refactoring is clearly needed.

Each parsed note should include:

- `path`: relative path from the input root
- `title`: first level-one heading, otherwise filename without extension
- `tags`: Markdown hashtags such as `#kubernetes` and `#runbook`
- `wikilinks`: values inside `[[...]]`
- `sections`: heading text mapped to section body
- `commands`: fenced shell command blocks for documentation only

The generator should combine the parsed notes into a `RunbookDraft` structure with:

- title
- service
- severity
- source paths
- purpose bullets
- scope bullets
- symptoms
- confirmed facts
- assumptions
- safety checks
- diagnosis steps
- resolution steps
- rollback steps
- verification steps
- escalation guidance
- related notes

## Section Mapping

Use case-insensitive heading names. The initial mapping should be deterministic and conservative.

Map to symptoms from:

- symptoms
- symptom

Map to confirmed facts from:

- confirmed facts

Map to assumptions from:

- assumptions

Map to diagnosis steps from:

- diagnosis
- diagnosis steps
- checks
- read-only checks

Map to resolution steps from:

- resolution
- resolution notes
- resolution steps
- safer fix order

Map to rollback from:

- rollback

Map to verification from:

- verification

Map to escalation from:

- escalation

When a section is missing, generate a safe default sentence that asks the operator to confirm the missing information before using the runbook in an incident.

## Output Shape

The generated runbook should use this structure:

```markdown
# Runbook: Kubernetes CrashLoopBackOff

## Purpose
- Use this runbook when Kubernetes CrashLoopBackOff appears in OpsWiki notes.

## Scope
- Service or system: OpsWiki notes
- Severity: not specified
- Sources: `Kubernetes CrashLoopBackOff.md`

## Symptoms
- Pod status is `CrashLoopBackOff`.

## Confirmed Facts
- From `Kubernetes CrashLoopBackOff.md`: Previous container logs show the startup failure.

## Assumptions
- Confirm namespace, cluster context, workload name, and latest rollout before taking action.

## Safety Checks
- Confirm environment and cluster context before state-changing commands.
- Prefer read-only diagnosis before restart, rollback, delete, scale, or deploy actions.
- Do not paste secrets, tokens, private keys, account IDs, or customer data into the runbook.

## Diagnosis Steps
```bash
kubectl get pods -n <namespace>
```

## Resolution Steps
- From `Kubernetes CrashLoopBackOff.md`: Fix configuration first when logs show missing settings.

## Rollback
- Roll back to the previous known-good deployment or artifact when user impact is confirmed.

## Verification
- From `Kubernetes CrashLoopBackOff.md`: Previous error no longer appears in logs.

## Escalation
- Escalate when impact, ownership, rollback safety, or data risk cannot be confirmed.

## Related Notes
- [[Jenkins Docker Permission Denied]]
```

Commands must be rendered as documentation only. The generator must not execute them.

## File Structure

Create:

```text
scripts/opswiki_generate_runbook.py
tests/test_opswiki_generate_runbook.py
```

Modify:

```text
examples/sample-output/runbook-example.md
README.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
.codex-plugin/plugin.json
```

Do not add:

```text
.mcp.json
.app.json
```

Do not add `mcpServers` or `apps` to `.codex-plugin/plugin.json`.

## Testing

Add tests that verify:

- Markdown notes are discovered recursively.
- Titles fall back to filenames when no H1 exists.
- Tags and wikilinks are extracted.
- Runbook sections are mapped from source headings.
- Shell commands are preserved as documentation blocks.
- Missing input directory fails with a non-zero exit.
- Empty input directory fails with a non-zero exit.
- Output path as a directory fails with a non-zero exit.
- Running against `examples/sample-obsidian-vault` writes `runbook-example.md`.
- The generated runbook includes safety checks and does not claim commands were executed.

Use Python's standard `unittest` to match v0.2.

## Safety and Privacy

- Do not invent account IDs, regions, namespaces, resource names, owners, commands, or incident timelines.
- Do not execute commands found inside notes.
- Do not connect to external systems.
- Keep commands as documentation blocks only.
- Preserve source paths in generated output.
- Keep the output deterministic so runbooks can be reviewed in diffs.
- Include safety checks before diagnosis or resolution content.

## Documentation Updates

README should include:

- v0.3.0 runbook generator purpose
- example CLI command
- expected output file
- limitations

Architecture should describe:

- v0.2 context export and v0.3 runbook generation as separate local scripts
- no MCP or app integration in v0.3.0

Roadmap should mark v0.3.0 as implemented only after the generator is built and verified.

## Commit Strategy

Use GitHub Flow on:

```text
feature/v0.3-runbook-generator
```

Suggested commits:

```text
docs: add runbook generator design
feat: add runbook generator
docs: document runbook generator workflow
```

Do not include generated attribution, AI attribution, or co-author metadata.
