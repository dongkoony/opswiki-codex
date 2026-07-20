# V1.0 Release Readiness Implementation Plan

> **For agentic workers:** This plan implements documentation-first release readiness. Production code changes are out of scope unless verification exposes a release-blocking defect.

**Goal:** Stabilize OpsWiki for Codex as a v1.0.0 local-first plugin release with clear release checks, upgrade guidance, validation commands, and documented post-v1.0 boundaries.

**Architecture:** Keep the existing skills, scripts, tests, CI workflow, and optional read-only MCP server unchanged. Add release documentation and update core project metadata so the repository describes the current stable local workflow set consistently.

**Tech Stack:** Markdown documentation, existing Python 3.12 `unittest` test suite, existing `uv --with ...` dependency pattern, existing plugin validator, GitHub Actions `tests` workflow.

---

## Confirmed Brief

- **Status:** approved
- **User value:** maintainers and users get a clear v1.0.0 release path without guessing which commands, docs, examples, and plugin metadata need validation.
- **Technical problem:** the repository has implemented v0.1.0 through v0.5.0 workflows, but v1.0.0 still needs release checklist documentation, upgrade guidance, validation matrix, and consistent release language.
- **Scope:** documentation-first v1.0.0 readiness, plugin version metadata, roadmap/README/architecture/contributing alignment.
- **Out of scope:** new app integration, live Obsidian integration, provider APIs, CI/CD static analysis helper, writable MCP tools, release tags, GitHub releases, and production-system integrations.
- **Approval path:** user approved proceeding with v1.0 stabilization and release preparation documentation on 2026-07-20.

## Context Used

- `docs/superpowers/specs/2026-07-06-v1-release-readiness.md`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/CONTRIBUTING.md`
- `.codex-plugin/plugin.json`
- `.github/workflows/ci.yml`
- `scripts/opswiki_export_context.py`
- `scripts/opswiki_generate_runbook.py`
- `scripts/opswiki_static_review.py`
- `mcp/opswiki_server.py`
- `tests/`

## Phase 0 Discovery

Completed on 2026-07-20.

Findings:

- The repository already has CI that installs `pyyaml` and `mcp`, runs `git diff --check`, runs unit tests, and validates core plugin manifest shape.
- The plugin manifest is at version `0.5.0` before this readiness implementation.
- The current roadmap names v1.0.0 as the next stable release target.
- The README documents v0.5.0 workflows and remaining limitations, but it does not yet provide v1.0 release checklist or upgrade guidance.
- The release readiness spec already defines v1.0.0 as a stabilization gate, not a new feature gate.

Unknowns:

- GitHub release/tag timing is not decided. This plan does not create tags or releases.
- A dedicated v1.0.0 GitHub milestone may be created later outside this local documentation change.

## Architecture Decisions

### Decision 1: Documentation-first v1.0.0

Use v1.0.0 to stabilize the existing local workflow set instead of adding another runtime capability.

Rationale:

- Existing v0.2 through v0.5 functionality is already local, deterministic, tested, and CI-backed.
- A stable release should make verification and upgrade expectations explicit.
- Adding app or provider integrations would expand safety and authentication scope beyond release readiness.

Tradeoff:

- This defers new feature work such as CI/CD static analysis helper or live Obsidian access.
- It reduces release risk and keeps the v1.0.0 PR small.

### Decision 2: Keep release automation manual

Document release checks without creating tags, GitHub releases, or release automation.

Rationale:

- Release publication should require explicit maintainer approval.
- The repository can mature release mechanics after the v1.0.0 docs and checks are stable.

Tradeoff:

- Maintainers still need to run release publication steps manually.
- The checklist makes those manual steps visible and repeatable.

## Phase Breakdown

## Phase 1: Release Planning Artifacts

- **Status:** code_complete
- **Prerequisites:** v1.0 readiness spec exists.
- **Likely files:** `docs/superpowers/plans/2026-07-20-v1-release-readiness-implementation.md`
- **Work:** add this implementation plan with phases, acceptance criteria, quality gates, and rollback notes.
- **Validation:** inspect plan for placeholders and forbidden attribution language.
- **Rollback:** remove the plan file.
- **Blocks next phase:** none after plan file is present.

## Phase 2: Release Checklist and Upgrade Guidance

- **Status:** code_complete
- **Prerequisites:** Phase 1 plan exists.
- **Likely files:** `docs/RELEASE_CHECKLIST.md`, `docs/UPGRADE.md`
- **Work:** add concrete v1.0.0 release checklist and v0.5.0-to-v1.0.0 upgrade guidance.
- **Validation:** ensure commands are copyable and match existing scripts/CI.
- **Rollback:** remove the new docs.
- **Blocks next phase:** none after docs are present.

## Phase 3: Core Documentation and Metadata Alignment

- **Status:** code_complete
- **Prerequisites:** Phase 2 docs exist.
- **Likely files:** `README.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/CONTRIBUTING.md`, `.codex-plugin/plugin.json`
- **Work:** update version language, repository structure, validation matrix, release links, roadmap wording, and plugin version metadata.
- **Validation:** plugin validator and docs placeholder scan.
- **Rollback:** revert the modified docs and metadata.
- **Blocks next phase:** none after metadata validates.

## Phase 4: Verification and Sample Freshness

- **Status:** code_complete
- **Prerequisites:** documentation and metadata changes are present.
- **Likely files:** sample outputs only if regeneration changes content.
- **Work:** run existing unit tests, plugin validation, whitespace check, `.app.json` diff check, and sample regeneration commands.
- **Validation:** compare regenerated sample outputs to the working tree.
- **Rollback:** revert any sample output changes that are not deterministic or in scope.
- **Blocks next phase:** failing verification blocks PR preparation.

## Phase 5: PR Preparation

- **Status:** pending
- **Prerequisites:** verification passes.
- **Likely files:** no additional files.
- **Work:** summarize changes, recommended commit message, and PR metadata for maintainer review.
- **Validation:** final `git status --short --branch`.
- **Rollback:** not applicable for reporting.
- **Blocks next phase:** commit, push, and PR require explicit user request.

## Test Strategy

- **Unit tests:** run the existing Python unittest suite.
- **Integration-style script checks:** rerun local exporter, runbook generator, and static review helper against sample inputs.
- **MCP checks:** existing MCP unit tests cover indexing, read guards, and FastMCP registration.
- **Plugin validation:** run the plugin-creator validator against the repository root.
- **Documentation checks:** run `git diff --check` and scan changed docs for unresolved placeholders or forbidden attribution language.
- **Visual QA:** not applicable; this is not UI work.

## Quality Gates

Required:

```powershell
uv run --with pyyaml --with mcp python -m unittest discover -s tests -v
uv run --with pyyaml --with mcp python C:\Users\dongh\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py C:\Users\dongh\iCloudDrive\opswiki-codex
git diff --check
git diff -- .app.json
```

Recommended:

```powershell
uv run python scripts/opswiki_export_context.py --input examples/sample-obsidian-vault --output examples/sample-output --project-name sample-obsidian-vault
uv run python scripts/opswiki_generate_runbook.py --input examples/sample-obsidian-vault --output examples/sample-output/runbook-example.md --title "Kubernetes CrashLoopBackOff" --service "sample-obsidian-vault" --severity "SEV3" --focus "kubernetes"
uv run --with pyyaml python scripts/opswiki_static_review.py --input examples/sample-infra --output examples/sample-output/static-review.md --project-name sample-infra
```

## Rollback Strategy

- Documentation-only files can be reverted independently.
- Plugin version metadata can be reverted from `1.0.0` to `0.5.0` if release readiness is deferred.
- No data migration, credentials, external service state, or generated release artifact is changed by this plan.
- No `.app.json` should be introduced by this work.

## Acceptance Criteria

- `docs/RELEASE_CHECKLIST.md` exists and includes concrete local and CI release checks.
- `docs/UPGRADE.md` exists and explains the v0.5.0 to v1.0.0 transition.
- README includes v1.0.0 release language, validation matrix, and links to release docs.
- Architecture and roadmap docs consistently describe v1.0.0 as a stable local-first release.
- Plugin manifest version is updated to `1.0.0` after docs are complete.
- Existing tests pass.
- Plugin validation passes.
- No app integration is added.
- No runtime behavior is changed.

## Progress Tracking

- **Last updated:** 2026-07-20
- **Brief:** approved
- **Phase 1:** code_complete
- **Phase 2:** code_complete
- **Phase 3:** code_complete
- **Phase 4:** code_complete
- **Phase 5:** in_progress

## Notes and Learnings

- The branch name follows repository rules by using the `feature/` prefix.
- The existing CI workflow already covers the core v1.0 test and plugin validation path.
- Release publication remains an explicit maintainer action outside this plan.
- 2026-07-20 verification passed: full unit tests, plugin validation, whitespace check, `.app.json` diff check, and sample output regeneration.
