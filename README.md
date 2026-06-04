# OpsWiki for Codex

OpsWiki for Codex is a DevOps and MLOps-focused Codex plugin for turning Markdown or Obsidian-style operational notes into reusable agent context, runbooks, infrastructure review workflows, troubleshooting references, and project-specific AGENTS.md guidance.

This v0.1.0 MVP is instruction-only. It provides Codex skills and Markdown references, not MCP servers, app integrations, or complex scripts.

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

- Convert Markdown or Obsidian notes into a Codex context brief.
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
  docs/
    README.md
    ROADMAP.md
    ARCHITECTURE.md
    CONTRIBUTING.md
```

Each skill contains a `SKILL.md` file and focused Markdown references.

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

- No automatic Markdown or Obsidian vault ingestion yet.
- No MCP server integration yet.
- No app integration yet.
- No static analysis scripts yet.
- The plugin does not connect to cloud accounts, clusters, CI systems, or model registries.
- Codex should treat examples as generic and safe placeholders.

## Roadmap

See `docs/ROADMAP.md`.
