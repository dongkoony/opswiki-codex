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

## Script-Based Context Compilation

The v0.2.0 exporter implements script-based context compilation through:

```text
scripts/opswiki_export_context.py
```

It compiles selected Markdown notes into:

- source indexes
- context briefs
- AGENTS.md drafts

The exporter keeps source paths, wikilinks, tags, assumptions, and verification steps visible in the output. It is deterministic, local-only, and does not execute commands found in notes.

## Script-Based Runbook Generation

The v0.3.0 generator follows the same local-only script pattern through:

```text
scripts/opswiki_generate_runbook.py
```

It maps structured Markdown sections into a deterministic runbook draft:

- purpose and scope
- symptoms
- confirmed facts
- assumptions
- safety checks
- diagnosis steps
- resolution steps
- rollback
- verification
- escalation
- related notes

Fenced shell commands are rendered as documentation only. The generator does not execute commands, connect to external systems, or change plugin behavior.

## Script-Based Static Review

The v0.4.0 static review helper follows the same local-only script pattern through:

```text
scripts/opswiki_static_review.py
```

It scans local Terraform and Kubernetes files and writes a Markdown review report with findings, assumptions, and verification questions.

Terraform scanning is text-oriented and conservative. It checks high-signal patterns such as public ingress CIDRs, wildcard IAM policy text, sensitive-looking outputs, and missing tags on selected AWS resource blocks without evaluating modules, variables, providers, or plan output.

Kubernetes scanning parses local YAML documents with PyYAML and checks common workload and Service review signals such as privileged containers, hostPath volumes, host networking, mutable image tags, missing resources, missing probes, default namespace use, and Service selectors without matching workload labels in scanned files.

Findings are review prompts, not authoritative policy decisions. The helper does not execute commands, connect to cloud accounts, contact Kubernetes API servers, or change plugin behavior.

## Future Optional MCP Integration

An optional MCP server may later expose compiled context and runbook indexes to Codex. MCP should remain optional because the plugin must continue to work as a local skills-and-scripts plugin.

The MCP layer should not directly connect to production systems by default. Any future integration with cloud, cluster, CI/CD, or model registry systems should require explicit configuration and safe authentication boundaries.
