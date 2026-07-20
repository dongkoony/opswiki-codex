# Release Checklist

Use this checklist before merging, tagging, or publishing an OpsWiki for Codex release.

## Scope Check

- [ ] Confirm the release target in `.codex-plugin/plugin.json`.
- [ ] Confirm README release language matches the target version.
- [ ] Confirm `docs/ROADMAP.md` describes the target release accurately.
- [ ] Confirm `docs/ARCHITECTURE.md` reflects current capabilities and boundaries.
- [ ] Confirm `docs/UPGRADE.md` explains user-facing changes from the previous release.
- [ ] Confirm no release notes claim live cloud, cluster, CI, model registry, or Obsidian integration unless that integration exists.

## Local Verification

Run from the repository root:

```powershell
uv run --with pyyaml --with mcp python -m unittest discover -s tests -v
uv run --with pyyaml --with mcp python C:\Users\dongh\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py C:\Users\dongh\iCloudDrive\opswiki-codex
git diff --check
git diff -- .app.json
```

Expected results:

- all tests pass
- plugin validation passes
- no whitespace errors
- no `.app.json` diff unless app integration is intentionally in scope

## Sample Output Freshness

Regenerate sample outputs with existing local helpers:

```powershell
uv run python scripts/opswiki_export_context.py --input examples/sample-obsidian-vault --output examples/sample-output --project-name sample-obsidian-vault
uv run python scripts/opswiki_generate_runbook.py --input examples/sample-obsidian-vault --output examples/sample-output/runbook-example.md --title "Kubernetes CrashLoopBackOff" --service "sample-obsidian-vault" --severity "SEV3" --focus "kubernetes"
uv run --with pyyaml python scripts/opswiki_static_review.py --input examples/sample-infra --output examples/sample-output/static-review.md --project-name sample-infra
```

Then inspect:

```powershell
git status --short
git diff -- examples/sample-output
```

Expected results:

- generated outputs are deterministic
- any sample output diff is intentional and reviewable
- generated reports continue to state that commands are documentation only

## MCP Verification

The MCP server is optional, local, and read-only. Verify MCP behavior through tests:

```powershell
uv run --with mcp python -m unittest tests.test_opswiki_mcp_server -v
```

Expected coverage:

- generated output index
- source note index
- read-only output reads
- read-only note reads
- repository-root read guards
- FastMCP tool and resource registration

Manual server launch smoke command:

```powershell
uv run --with mcp python mcp/opswiki_server.py
```

Stop the server after confirming it starts in the expected local MCP mode.

## Safety Review

- [ ] Confirm `.app.json` is absent unless app integration is intentionally part of the release.
- [ ] Confirm MCP tools do not write files.
- [ ] Confirm MCP tools do not execute shell commands.
- [ ] Confirm generated commands in docs and reports are examples only.
- [ ] Confirm sample Terraform and Kubernetes files are treated as fixtures, not deployable infrastructure.
- [ ] Confirm no secrets, credentials, private keys, tokens, or personal access keys are present.
- [ ] Confirm commit messages and PR descriptions do not include generated attribution or co-author metadata.

## GitHub PR Readiness

- [ ] Work is on an allowed feature branch prefix.
- [ ] PR targets `main`.
- [ ] PR description includes summary, why, changes, safety, test plan, and release notes.
- [ ] Labels reflect the work, such as `documentation`, `enhancement`, or `ci`.
- [ ] Milestone is attached only when the matching release milestone exists.
- [ ] GitHub Actions `tests` workflow passes.

## Release Publication

Do not create a tag or GitHub release until the maintainer explicitly approves publication.

When approved, suggested manual publication steps are:

```powershell
git checkout main
git pull --ff-only origin main
git tag v1.0.0
git push origin v1.0.0
```

Create GitHub release notes from the merged PR summary and test plan.
