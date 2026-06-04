# OpsWiki for Codex

OpsWiki for Codex is a DevOps and MLOps-focused Codex plugin for turning Markdown or Obsidian-style operational notes into reusable agent context, runbooks, infrastructure review workflows, troubleshooting references, and project-specific AGENTS.md guidance.

This v0.2.0 release provides Codex skills, Markdown references, and a local Markdown/Obsidian context exporter. It does not add MCP servers or app integrations.

## How It Is Different

OpsWiki for Codex is not a general LLM wiki plugin and is not only an Obsidian integration. It focuses on operational engineering work:

- DevOps and SRE runbooks
- infrastructure review workflows
- Kubernetes troubleshooting
- AWS and Terraform review patterns
- CI/CD pipeline review
- MLOps deployment and model-serving guidance
- project-specific AGENTS.md generation from operational notes

## Supported MVP Workflows

- Export Markdown or Obsidian notes into a Codex context brief.
- Draft AGENTS.md guidance for DevOps/MLOps repositories.
- Create and improve incident runbooks.
- Review Terraform and AWS infrastructure changes.
- Triage Kubernetes workload failures.
- Review Jenkins and GitHub Actions pipelines.
- Review MLOps deployment and model-serving readiness.

## Repository Structure

```text
opswiki-codex/
  README.md
  LICENSE
  .codex-plugin/
    plugin.json
  skills/
    opswiki-context/
    devops-runbook/
    terraform-review/
    kubernetes-triage/
    cicd-review/
    mlops-deployment/
  examples/
    sample-obsidian-vault/
    sample-output/
  scripts/
    opswiki_export_context.py
  tests/
    test_opswiki_export_context.py
  docs/
    README.md
    ROADMAP.md
    ARCHITECTURE.md
    CONTRIBUTING.md
```

Each skill contains a `SKILL.md` file and focused Markdown references.

## Markdown Context Exporter

Use the v0.2.0 exporter to compile Markdown or Obsidian-style notes into reviewable Codex context outputs:

```powershell
uv run python scripts/opswiki_export_context.py --input examples/sample-obsidian-vault --output examples/sample-output --project-name sample-obsidian-vault
```

The exporter writes:

- `context-brief.md`
- `AGENTS.md`

The script extracts note titles, tags, `[[wikilink]]` references, operational sections, and fenced shell commands. It preserves source paths and treats generated output as a draft for review.

## How To Use With Codex

1. Install or load this local plugin in Codex.
2. Ask Codex to use the relevant OpsWiki skill for the task.
3. Provide Markdown notes, repository docs, incident notes, Terraform diffs, Kubernetes symptoms, CI/CD files, or MLOps deployment context.
4. Ask for one of the MVP outputs:
   - context brief
   - AGENTS.md guidance
   - runbook
   - infrastructure review
   - triage checklist
   - deployment review

Example prompts:

```text
Use OpsWiki Context to turn these Obsidian notes into AGENTS.md guidance.
Use Terraform Review to review this AWS security group change.
Use Kubernetes Triage to investigate this CrashLoopBackOff.
```

## Current Limitations

- No live Obsidian API integration.
- No MCP server integration yet.
- No app integration yet.
- No Terraform, Kubernetes, or CI/CD static analysis helpers yet.
- The plugin does not connect to cloud accounts, clusters, CI systems, or model registries.
- Codex should treat examples as generic and safe placeholders.

## Roadmap

See `docs/ROADMAP.md`.
