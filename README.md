# OpsWiki for Codex

OpsWiki for Codex is a DevOps and MLOps-focused Codex plugin for turning Markdown or Obsidian-style operational notes into reusable agent context, runbooks, infrastructure review workflows, troubleshooting references, and project-specific AGENTS.md guidance.

This v0.5.0 release provides Codex skills, Markdown references, a local Markdown/Obsidian context exporter, a local runbook generator, a local Terraform/Kubernetes static review helper, and optional local MCP access to generated OpsWiki outputs and source notes. It does not add app integrations.

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
- Generate a focused operational runbook from structured notes.
- Run local Terraform and Kubernetes static review checks.
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
  .mcp.json
  .codex-plugin/
    plugin.json
  mcp/
    opswiki_server.py
  skills/
    opswiki-context/
    devops-runbook/
    terraform-review/
    kubernetes-triage/
    cicd-review/
    mlops-deployment/
  examples/
    sample-infra/
    sample-obsidian-vault/
    sample-output/
  scripts/
    opswiki_export_context.py
    opswiki_generate_runbook.py
    opswiki_static_review.py
  tests/
    test_opswiki_export_context.py
    test_opswiki_generate_runbook.py
    test_opswiki_static_review.py
    test_opswiki_mcp_server.py
  docs/
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

## Runbook Generator

Use the v0.3.0 generator to turn Markdown or Obsidian-style operational notes into a focused Markdown runbook:

```powershell
uv run python scripts/opswiki_generate_runbook.py --input examples/sample-obsidian-vault --output examples/sample-output/runbook-example.md --title "Kubernetes CrashLoopBackOff" --service "sample-obsidian-vault" --severity "SEV3" --focus "kubernetes"
```

The generator writes:

- `runbook-example.md`

The script extracts operational sections, related notes, and fenced shell commands. Commands are rendered as documentation only; the generator does not execute commands and does not connect to cloud accounts, clusters, CI systems, or external services.

## Static Review Helper

Use the v0.4.0 helper to scan local Terraform and Kubernetes files and write a Markdown review report:

```powershell
uv run --with pyyaml python scripts/opswiki_static_review.py --input examples/sample-infra --output examples/sample-output/static-review.md --project-name sample-infra
```

The helper writes:

- `static-review.md`

Commands in the generated report are documentation only. The helper reads local files and does not execute `terraform`, `tofu`, `kubectl`, cloud APIs, cluster calls, or scanner binaries.

## Optional MCP Server

Use the v0.5.0 optional local MCP server to expose generated OpsWiki outputs and source notes as read-only MCP resources and tools:

```powershell
uv run --with mcp python mcp/opswiki_server.py
```

The MCP server provides read-only tools:

- `list_opswiki_outputs`
- `read_opswiki_output`
- `list_opswiki_notes`
- `read_opswiki_note`

The server reads local repository files only. It does not execute `terraform`, `tofu`, `kubectl`, cloud APIs, cluster calls, CI APIs, shell commands, or scanner binaries.

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
- No app integration yet.
- No CI/CD static analysis helper yet.
- No automatic external incident timeline or production system discovery.
- The plugin does not connect to cloud accounts, clusters, CI systems, or model registries.
- Codex should treat examples as generic and safe placeholders.

## Roadmap

See `docs/ROADMAP.md`.
