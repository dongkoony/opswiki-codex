# Architecture

OpsWiki for Codex starts as an instruction-only plugin. The core architecture is intentionally small so the project can grow from useful workflows instead of premature infrastructure.

## Markdown and Obsidian Notes

Markdown and Obsidian-style notes are the source knowledge format. Notes can include tags, headings, code blocks, operational facts, and `[[wikilink]]` relationships.

OpsWiki treats notes as source material, not as automatically trusted truth. Codex should extract confirmed facts only when the source supports them and mark other useful inferences as assumptions.

## Codex Skills

Skills are task-specific workflows that tell Codex how to use operational knowledge:

- `opswiki-context` converts notes into Codex context and AGENTS.md guidance.
- `devops-runbook` creates and reviews runbooks.
- `terraform-review` reviews infrastructure-as-code changes.
- `kubernetes-triage` supports Kubernetes troubleshooting.
- `cicd-review` reviews Jenkins and GitHub Actions pipelines.
- `mlops-deployment` reviews model-serving deployment readiness.

Each skill owns its own references so workflows stay focused and reviewable.

## AGENTS.md Output

AGENTS.md is the project-level instruction output. It should contain short operational rules, verification commands, review focus areas, and links back to source notes.

Generated AGENTS.md content should be specific enough to guide Codex in a repository but short enough to remain maintainable.

## Future Context Compilation

Future versions can add scripts that compile selected notes into:

- source indexes
- context briefs
- AGENTS.md drafts
- runbook seeds
- review checklists

These scripts should keep source paths, wikilinks, tags, assumptions, and verification steps visible in the output.

## Future Optional MCP Integration

An optional MCP server may later expose compiled context and runbook indexes to Codex. MCP should remain optional because the v0.1.0 plugin must work as a local instruction-only plugin.

The MCP layer should not directly connect to production systems by default. Any future integration with cloud, cluster, CI/CD, or model registry systems should require explicit configuration and safe authentication boundaries.
