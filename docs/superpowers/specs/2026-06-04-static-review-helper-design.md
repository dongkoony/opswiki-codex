# Static Review Helper Design

## Summary

v0.4.0 adds a local static review helper for Terraform and Kubernetes files. The helper scans repository files and writes a Markdown report that helps Codex start an infrastructure or workload review with concrete findings, assumptions, and verification questions.

This feature continues the existing OpsWiki pattern:

- v0.2.0: local Markdown context exporter
- v0.3.0: local runbook generator
- v0.4.0: local static review helper

The helper does not replace specialist tools such as `terraform validate`, `terraform plan`, `tflint`, `checkov`, `kubectl`, `kubeconform`, or policy engines. It provides a lightweight operational pre-review that is deterministic, testable, and safe to run on local files.

## Goals

- Add one local-only CLI script for Terraform and Kubernetes static review.
- Scan Terraform `.tf` and `.tfvars` files for high-signal operational review risks.
- Scan Kubernetes `.yaml` and `.yml` manifests for common security, reliability, and operability risks.
- Write a Markdown report with findings, assumptions, and verification questions.
- Keep v0.2 exporter and v0.3 runbook generator behavior unchanged.
- Keep plugin behavior unchanged: no MCP server, no app integration, no external connection, and no command execution.
- Make rules deterministic and unit-testable with Python standard library plus PyYAML only when YAML parsing is needed.

## Non-Goals

- No live cloud account, Kubernetes cluster, CI system, model registry, or remote API access.
- No execution of `terraform`, `tofu`, `kubectl`, or scanner binaries.
- No full Terraform HCL evaluation, module expansion, provider schema validation, or plan interpretation.
- No full Kubernetes schema validation or admission-policy emulation.
- No automatic code modification.
- No attempt to replace dedicated security or compliance scanners.
- No `.mcp.json`, `.app.json`, `mcpServers`, or `apps` fields.

## Best-Practice Basis

The design follows the same conservative boundary used by Terraform and Kubernetes documentation:

- Terraform `validate` is a safe automated syntax and consistency check, but workspace-specific correctness still requires plan context.
- Kubernetes probes are an operational reliability signal, especially readiness, liveness, and startup behavior.
- Kubernetes Pod Security Standards define common security boundaries such as privileged containers, host namespace access, and restricted security contexts.
- Kubernetes resource requests and limits are core scheduling and reliability inputs.

The helper therefore reports static signals as review findings or questions, not final production truth.

## User Workflow

The user runs:

```powershell
uv run python scripts/opswiki_static_review.py --input examples/sample-infra --output examples/sample-output/static-review.md --project-name sample-infra
```

The script writes one Markdown report:

```text
examples/sample-output/static-review.md
```

The report is intended for Codex review prompts, PR review preparation, incident context, and OpsWiki documentation. It should be readable without running any external command.

## File Structure

Create:

- `scripts/opswiki_static_review.py`
- `tests/test_opswiki_static_review.py`
- `examples/sample-infra/terraform/security_group.tf`
- `examples/sample-infra/terraform/iam.tf`
- `examples/sample-infra/kubernetes/deployment.yaml`
- `examples/sample-infra/kubernetes/service.yaml`
- `examples/sample-output/static-review.md`
- `docs/superpowers/plans/2026-06-04-v0.4-static-review-helper-implementation.md`

Modify:

- `.codex-plugin/plugin.json`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

Do not create:

- `.mcp.json`
- `.app.json`

## CLI Design

The script exposes these flags:

```text
--input <directory>
--output <markdown-file>
--project-name <name>
--focus <terraform|kubernetes|all>
```

Defaults:

- `--project-name` defaults to the input directory name.
- `--focus` defaults to `all`.

Failure behavior:

- Missing input path returns exit code `1` with a clear error.
- Non-directory input returns exit code `1`.
- No supported files returns exit code `1`.
- Output path that already exists as a directory returns exit code `1`.
- Invalid UTF-8 in Terraform files returns exit code `1`.
- Invalid YAML in Kubernetes files produces a finding when possible; if the file cannot be parsed at all, it is reported as a parse finding rather than crashing.

## Internal Model

Use small plain Python classes, consistent with existing scripts:

- `ReviewError`
- `SourceFile`
- `Finding`
- `StaticReviewReport`

Finding fields:

- `domain`: `terraform` or `kubernetes`
- `severity`: `high`, `medium`, or `low`
- `path`
- `line`
- `rule_id`
- `message`
- `recommendation`

Report fields:

- `project_name`
- `input_root`
- `files_scanned`
- `findings`
- `assumptions`
- `verification_questions`

## Terraform Rule Set

The v0.4.0 Terraform scanner is intentionally text-oriented. It should find high-signal patterns without pretending to fully evaluate HCL.

Rules:

- `TF_PUBLIC_INGRESS`: flag `cidr_blocks` or `ipv6_cidr_blocks` containing `0.0.0.0/0` or `::/0` near ingress-like resources or attributes.
- `TF_WILDCARD_IAM_ACTION`: flag IAM policies with `"Action": "*"` or wildcard-heavy actions such as `"s3:*"`.
- `TF_WILDCARD_IAM_RESOURCE`: flag IAM policies with `"Resource": "*"`.
- `TF_SENSITIVE_OUTPUT`: flag Terraform `output` blocks whose names suggest secrets, tokens, passwords, keys, or credentials unless `sensitive = true` appears in the block.
- `TF_MISSING_TAGS`: flag AWS resource blocks likely to require ownership tags when no `tags` block or `tags =` assignment appears nearby.

The scanner should include file and best-effort line numbers. It should prefer false-negative behavior over noisy findings for ambiguous text.

## Kubernetes Rule Set

The Kubernetes scanner parses YAML documents and inspects workload and service objects.

Rules:

- `K8S_LATEST_IMAGE_TAG`: flag containers using `:latest` or no explicit tag.
- `K8S_MISSING_RESOURCE_REQUESTS`: flag containers without CPU or memory requests.
- `K8S_MISSING_RESOURCE_LIMITS`: flag containers without CPU or memory limits.
- `K8S_MISSING_READINESS_PROBE`: flag Deployment, StatefulSet, DaemonSet, and Pod containers without a readiness probe.
- `K8S_MISSING_LIVENESS_PROBE`: flag Deployment, StatefulSet, DaemonSet, and Pod containers without a liveness probe.
- `K8S_PRIVILEGED_CONTAINER`: flag `securityContext.privileged: true`.
- `K8S_HOST_PATH_VOLUME`: flag `hostPath` volumes.
- `K8S_HOST_NETWORK`: flag `hostNetwork: true`.
- `K8S_DEFAULT_NAMESPACE`: flag workload manifests without `metadata.namespace`.
- `K8S_SERVICE_SELECTOR_WITHOUT_MATCHING_WORKLOAD`: flag Service selectors when no scanned workload labels appear to match.

The scanner should handle multi-document YAML. It should ignore empty YAML documents.

## Markdown Report Shape

The generated report should use this shape:

```markdown
# Static Review: <project-name>

## Summary

- Files scanned: <count>
- Findings: <count>
- Terraform findings: <count>
- Kubernetes findings: <count>

## Findings

- [high] terraform `path:line` TF_PUBLIC_INGRESS - Public ingress allows `0.0.0.0/0`.
  Recommendation: Confirm this is an intentionally public service and restrict CIDR where possible.

## Assumptions

- Static review does not evaluate Terraform modules, variables, provider schemas, or plan output.
- Static review does not contact a Kubernetes API server or validate manifests against a live cluster.

## Verification Questions

- Run `terraform validate` or `tofu validate` in the relevant module.
- Review `terraform plan` for replacements, public exposure, and IAM blast radius.
- Validate Kubernetes manifests with the repository's normal manifest tooling before deploy.
```

Commands in verification questions are documentation only. The script must not execute them.

## Data Flow

1. Validate CLI paths.
2. Discover supported files.
3. Load Terraform files as UTF-8 text.
4. Load Kubernetes YAML files with PyYAML.
5. Run deterministic rule functions.
6. Aggregate findings into a report model.
7. Render Markdown.
8. Write the output file.

## Testing Strategy

Use `unittest`, matching existing tests.

Parser and rule tests:

- Terraform public ingress is detected.
- Terraform wildcard IAM action and resource are detected.
- Terraform sensitive output without `sensitive = true` is detected.
- Kubernetes missing resources and probes are detected.
- Kubernetes privileged container, hostPath, hostNetwork, latest image, and missing namespace are detected.
- Service selector mismatch is detected when scanned workload labels do not match.

CLI tests:

- Sample infra directory generates a Markdown report.
- `--focus terraform` excludes Kubernetes findings.
- `--focus kubernetes` excludes Terraform findings.
- Missing input directory fails.
- Empty input directory fails.
- Output path that exists as a directory fails.
- Invalid YAML is reported as a finding instead of crashing.

Full verification:

```powershell
uv run python -m unittest discover -s tests -v
uv run --with pyyaml python C:\Users\dongh\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py C:\Users\dongh\iCloudDrive\opswiki-codex
git diff -- .mcp.json .app.json
```

## Release Documentation

README should document:

- v0.4.0 static review helper purpose
- example command
- generated report path
- local-only behavior
- no command execution
- no external connections

Architecture should document:

- v0.2 exporter, v0.3 generator, and v0.4 static review helper as separate local scripts
- static review limitations
- why findings are review prompts rather than authoritative policy decisions

Roadmap should mark v0.4.0 implemented after verification.

Plugin manifest should update only:

```json
"version": "0.4.0"
```

## Acceptance Criteria

- Static review CLI exists and is covered by tests.
- Terraform and Kubernetes sample files produce a deterministic Markdown report.
- Report includes findings, assumptions, and verification questions.
- The script reads local files only.
- The script does not execute external commands.
- The script does not add MCP or app integration.
- Existing v0.2 and v0.3 tests continue to pass.
- Plugin validation passes.
