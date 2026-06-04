---
name: cicd-review
description: Use when reviewing Jenkinsfiles, GitHub Actions workflows, CI/CD pipelines, release automation, build permissions, deployment gates, artifact handling, caching, Docker build steps, or secret usage.
---

# CI/CD Review

Use this skill to review pipeline changes for reliability, security, and deployability.

## Workflow

1. Identify changed workflow files and the events that trigger them.
2. Check permissions, secrets, dependency installation, caching, artifact boundaries, and deployment gates.
3. Confirm whether jobs run on pull requests, protected branches, tags, or manual dispatch.
4. Look for shell quoting, credential exposure, non-pinned actions, and missing failure handling.
5. Separate findings from assumptions and verification steps.

## Review Focus

- least-privilege token permissions
- safe secret handling and masking
- pinned or trusted third-party actions/plugins
- reproducible dependency installation
- Docker socket and file permission risks
- deploy jobs gated by branch, environment, approval, or tag
- artifact upload/download paths
- cache key correctness and invalidation
- test results and logs available for failed runs

## References

- `references/jenkinsfile-review-checklist.md`
- `references/github-actions-review-checklist.md`
