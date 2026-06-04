# GitHub Actions Review Checklist

## Triggers

- Confirm `pull_request`, `push`, `workflow_dispatch`, and tag triggers are intentional.
- Avoid running privileged deploy jobs on untrusted pull request code.
- Use path filters only when missing files cannot hide required checks.

## Permissions

- Set top-level or job-level `permissions`.
- Prefer `contents: read` unless the job needs writes.
- Use OIDC for cloud access when possible instead of long-lived keys.

## Actions and Dependencies

- Pin third-party actions by commit SHA or trusted version policy.
- Keep setup actions close to the jobs that use them.
- Use lockfiles for package managers.

## Secrets

- Do not print secrets or write them into artifacts.
- Keep environment secrets scoped to protected environments.
- Avoid passing secrets into scripts that run on untrusted input.

## Build and Test

- Make cache keys include lockfiles and relevant runtime versions.
- Upload test reports or logs for failed jobs.
- Keep matrix jobs explicit and bounded.

## Deployments

- Use protected environments for production.
- Gate deploys on branch, tag, or manual approval.
- Emit deployed version, artifact digest, or release reference.
