# Upgrade Guide

This guide describes the expected upgrade path from OpsWiki for Codex v0.5.0 to v1.0.0.

## Summary

v1.0.0 is a stable local-first release. It consolidates the existing v0.1.0 through v0.5.0 workflows and adds release documentation, upgrade guidance, and validation expectations.

v1.0.0 does not add live production-system integrations.

## What Changes From v0.5.0

- The plugin version moves from `0.5.0` to `1.0.0`.
- Release readiness documentation is added.
- A release checklist documents the commands maintainers should run before publishing.
- This upgrade guide documents compatibility, validation, and post-v1.0 backlog boundaries.
- README and architecture documentation describe the stable local workflow set more explicitly.

## What Stays Compatible

Existing local workflows remain available:

- Markdown and Obsidian-style context export
- AGENTS.md draft generation
- local runbook generation
- local Terraform and Kubernetes static review
- optional read-only local MCP server access
- existing skills and references

Existing commands remain valid:

```powershell
uv run python scripts/opswiki_export_context.py --input examples/sample-obsidian-vault --output examples/sample-output --project-name sample-obsidian-vault
uv run python scripts/opswiki_generate_runbook.py --input examples/sample-obsidian-vault --output examples/sample-output/runbook-example.md --title "Kubernetes CrashLoopBackOff" --service "sample-obsidian-vault" --severity "SEV3" --focus "kubernetes"
uv run --with pyyaml python scripts/opswiki_static_review.py --input examples/sample-infra --output examples/sample-output/static-review.md --project-name sample-infra
uv run --with mcp python mcp/opswiki_server.py
```

## What Is Still Out Of Scope

The v1.0.0 release does not add:

- live Obsidian API integration
- app integration through `.app.json`
- CI/CD static analysis helper
- automatic external incident timeline discovery
- provider-authenticated cloud, cluster, CI, or model registry adapters
- writable MCP tools
- command execution from MCP tools

These items remain post-v1.0 backlog unless a future feature spec explicitly brings them into scope.

## Recommended Upgrade Checks

After pulling v1.0.0, run:

```powershell
uv run --with pyyaml --with mcp python -m unittest discover -s tests -v
uv run --with pyyaml --with mcp python C:\Users\dongh\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py C:\Users\dongh\iCloudDrive\opswiki-codex
git diff --check
```

If you customized sample notes or outputs locally, regenerate the sample outputs and review the diff:

```powershell
uv run python scripts/opswiki_export_context.py --input examples/sample-obsidian-vault --output examples/sample-output --project-name sample-obsidian-vault
uv run python scripts/opswiki_generate_runbook.py --input examples/sample-obsidian-vault --output examples/sample-output/runbook-example.md --title "Kubernetes CrashLoopBackOff" --service "sample-obsidian-vault" --severity "SEV3" --focus "kubernetes"
uv run --with pyyaml python scripts/opswiki_static_review.py --input examples/sample-infra --output examples/sample-output/static-review.md --project-name sample-infra
git diff -- examples/sample-output
```

## Safety Notes

- The plugin remains local-first.
- Existing scripts read local files and write local Markdown outputs.
- The static review helper does not execute `terraform`, `tofu`, `kubectl`, cloud APIs, cluster calls, or scanner binaries.
- The MCP server is read-only and repository-root confined.
- Sample Terraform and Kubernetes files are fixtures with intentional findings, not production templates.

## Rollback

If v1.0.0 needs to be deferred before release publication, revert the release-readiness PR or revert the plugin version from `1.0.0` to `0.5.0`.

If a v1.0.0 tag has already been published, create a follow-up patch release instead of rewriting public release history.
