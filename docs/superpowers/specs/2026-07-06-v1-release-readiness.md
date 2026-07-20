# v1.0.0 Release Readiness Design

## Summary

v1.0.0 should stabilize OpsWiki for Codex as a documented, tested, local-first plugin release. The release should consolidate the v0.1.0 through v0.5.0 workflow set instead of adding another major capability.

The v1.0.0 readiness work should focus on:

- release checklist and validation guidance
- documentation consistency across README, architecture, roadmap, and contributing docs
- repeatable verification commands for local and CI validation
- production-quality examples that remain generic, safe, and local-only
- clear upgrade guidance from v0.5.0 to v1.0.0

v1.0.0 is a stable workflow release for local DevOps/MLOps assistance. It is not a production-system integration release and should not imply live cloud, cluster, CI, model registry, or Obsidian access.

## Current Release State

The current repository has implemented:

- v0.1.0 instruction-only DevOps/MLOps skills and references
- v0.2.0 Markdown and Obsidian context exporter
- v0.3.0 local runbook generator
- v0.4.0 local Terraform and Kubernetes static review helper
- v0.5.0 optional read-only local MCP access to generated outputs and source notes

The repository now has local scripts, unit tests, CI validation, plugin validation, sample notes, generated sample outputs, and MCP metadata.

Remaining README limitations include:

- no live Obsidian API integration
- no app integration
- no CI/CD static analysis helper
- no automatic external incident timeline or production system discovery

These limitations do not block v1.0.0 if they are explicitly documented as out of scope or post-v1.0 backlog.

## Goals

- Define v1.0.0 release readiness criteria.
- Add a release checklist that a maintainer can run before tagging or merging v1.0.0.
- Add a validation matrix covering local tests, plugin validation, CI checks, MCP smoke validation, and documentation checks.
- Clarify upgrade guidance from v0.5.0 to v1.0.0.
- Review documentation for consistent version language and local-only safety boundaries.
- Confirm examples are safe placeholders and are not deployable infrastructure.
- Keep existing v0.2, v0.3, v0.4, and v0.5 behavior unchanged unless a readiness defect is found.

## Non-Goals

- No live Obsidian API integration.
- No `.app.json` app integration.
- No new cloud, Kubernetes, CI/CD, model registry, or provider API integration.
- No new mutation-capable MCP tools.
- No command execution from MCP tools.
- No replacement of existing CLI scripts.
- No claim that sample Terraform or Kubernetes manifests are deployable.
- No release automation that publishes tags or GitHub releases without explicit maintainer approval.

## Best-Practice Basis

v1.0.0 should be treated as a stabilization gate, not a feature expansion gate.

The release should follow these guardrails:

- A stable release needs repeatable verification steps more than new behavior.
- Local-only safety boundaries should be visible in every user-facing workflow.
- Examples should demonstrate findings and outputs without encouraging direct deployment.
- Upgrade guidance should tell users what changed, what did not change, and how to validate their local setup.
- Release documentation should be reviewable in one small PR before any optional implementation cleanup begins.

## Recommended v1.0.0 Scope

### Release Checklist

Create a dedicated release checklist document, likely:

```text
docs/RELEASE_CHECKLIST.md
```

The checklist should cover:

- branch and PR requirements
- local unit test command
- plugin validation command
- whitespace check
- MCP server smoke command
- CI status check
- README version check
- roadmap status check
- sample output freshness check
- forbidden attribution and metadata scan
- confirmation that `.app.json` is absent unless app integration is intentionally added later

### Validation Matrix

Add a compact validation table to README or a dedicated docs page. The table should map each workflow to its validation command:

- context exporter
- runbook generator
- static review helper
- MCP server registration and read-only tools
- plugin manifest validation
- CI workflow

### Upgrade Guidance

Add an upgrade section or document, likely:

```text
docs/UPGRADE.md
```

The guide should explain:

- v1.0.0 is compatible with v0.5.0 usage.
- Existing scripts remain local command-line helpers.
- MCP remains optional.
- The release does not add app integration or live provider access.
- Users should rerun unit tests and plugin validation after local customization.

### Documentation Consistency

Review and update:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/CONTRIBUTING.md`
- `.codex-plugin/plugin.json`

The final v1.0.0 implementation should avoid conflicting statements about current version, MCP status, app integration, and limitations.

### Example Quality

Review:

- `examples/sample-obsidian-vault/`
- `examples/sample-output/`
- `examples/sample-infra/`

Examples should remain:

- generic
- deterministic
- safe placeholders
- free of secrets
- clearly documented as samples
- aligned with generated output expectations

## Release Boundaries

v1.0.0 may update documentation, examples, tests, and metadata. It should avoid new runtime behavior unless the implementation plan identifies a release-blocking defect.

Allowed readiness changes:

- version metadata update to `1.0.0`
- release checklist documentation
- upgrade guidance documentation
- validation command documentation
- sample-output refresh when generated by existing scripts
- tests that lock current behavior
- documentation edits that clarify existing behavior

Disallowed readiness changes:

- new provider integrations
- new shell execution paths
- new writable MCP tools
- app integration
- branch or commit rule changes unrelated to release readiness
- broad refactors without a release-blocking reason

## Quality Gates

The v1.0.0 PR should pass:

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
- no `.app.json` diff unless explicitly approved
- plugin version changes only when the release readiness implementation is complete

Additional recommended checks:

```powershell
uv run python scripts/opswiki_export_context.py --input examples/sample-obsidian-vault --output examples/sample-output --project-name sample-obsidian-vault
uv run python scripts/opswiki_generate_runbook.py --input examples/sample-obsidian-vault --output examples/sample-output/runbook-example.md --title "Kubernetes CrashLoopBackOff" --service "sample-obsidian-vault" --severity "SEV3" --focus "kubernetes"
uv run --with pyyaml python scripts/opswiki_static_review.py --input examples/sample-infra --output examples/sample-output/static-review.md --project-name sample-infra
```

These commands verify that sample outputs can still be regenerated from existing local helpers.

## Implementation Strategy

Use a small, documentation-first implementation plan.

Recommended phases:

1. Release docs and checklist
2. Upgrade guidance and validation matrix
3. Example review and sample output freshness
4. Metadata and roadmap update to v1.0.0
5. Full verification and PR preparation

Each phase should remain independently reviewable. If any production code changes are needed, the implementation plan should switch that phase to test-first development and record RED/GREEN evidence.

## Risks and Guardrails

### Scope Creep

Risk: v1.0.0 could become a catch-all for app integration, CI/CD helper work, or provider integrations.

Guardrail: Treat those items as post-v1.0 backlog unless the user explicitly approves a separate feature spec.

### Overstated Stability

Risk: Documentation could imply that OpsWiki connects to or validates live production systems.

Guardrail: Keep local-only, read-only, and documentation-only boundaries visible in each workflow.

### Example Misuse

Risk: Sample Terraform or Kubernetes manifests could be mistaken for deployable infrastructure.

Guardrail: Keep sample wording clear that fixtures intentionally contain review findings and are not production templates.

### Release Drift

Risk: README, roadmap, plugin manifest, and CI docs could disagree about the current release state.

Guardrail: Add release checklist items that compare version and capability language across core docs.

## Acceptance Criteria

- v1.0.0 readiness scope is documented.
- Release checklist exists and contains concrete commands.
- Upgrade guidance from v0.5.0 to v1.0.0 exists.
- Validation matrix covers scripts, MCP, plugin manifest, CI, and docs.
- Current limitations are either retained as explicit backlog or moved to roadmap follow-up language.
- Examples remain generic, safe, and reproducible from local scripts.
- Plugin metadata updates to `1.0.0` only after readiness docs and checks are complete.
- Existing tests continue to pass.
- Plugin validation passes.
- No app integration is added.

## Backlog Outside v1.0.0

- Live Obsidian integration.
- App integration through `.app.json`.
- CI/CD static analysis helper.
- Automatic external incident timeline discovery.
- Provider-authenticated cloud, cluster, CI, or model registry adapters.
- Writable MCP tools.
- Release publishing automation.
