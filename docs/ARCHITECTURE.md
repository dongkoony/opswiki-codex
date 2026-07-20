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

## Optional MCP Integration

The v0.5.0 optional MCP layer is implemented through:

```text
mcp/opswiki_server.py
```

It exposes a read-only local index over:

- sample source notes
- context brief output
- generated AGENTS.md output
- runbook example output
- static review report output

Generation remains in the CLI scripts for v0.5.0. The MCP server only lists and reads existing local files, using repository-root path confinement, hidden-path rejection, UTF-8 validation, and file-size limits before returning content.

The MCP layer does not execute commands, connect to cloud accounts, contact Kubernetes API servers, call CI APIs, or change plugin behavior. Any future integration with cloud, cluster, CI/CD, or model registry systems should require explicit configuration and safe authentication boundaries.

## Stable Release Posture

The v1.0.0 release is a stable local-first workflow release. It consolidates the implemented v0.1.0 through v0.5.0 capabilities without expanding into live production-system integrations.

Release readiness is documented through:

- `docs/RELEASE_CHECKLIST.md`
- `docs/UPGRADE.md`
- `docs/ROADMAP.md`

The stable release contract is:

- local scripts remain the generation surface
- MCP remains optional and read-only
- examples remain generic fixtures
- generated commands remain documentation only
- app integration remains out of scope until a future feature spec introduces it
