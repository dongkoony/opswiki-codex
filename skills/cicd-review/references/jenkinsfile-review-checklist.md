# Jenkinsfile Review Checklist

## Pipeline Structure

- Use stages that map to build, test, package, scan, and deploy.
- Keep deploy stages guarded by branch, tag, parameter, or approval.
- Avoid hidden state between stages unless the workspace is explicitly preserved.

## Credentials

- Use Jenkins credentials bindings instead of plain environment variables.
- Avoid echoing secrets or command lines that expand secrets.
- Limit credential scope to the stage that needs it.

## Shell Safety

- Use strict shell behavior where practical.
- Quote variables that may contain spaces or special characters.
- Avoid `sudo` unless the runner model requires it and the risk is documented.

## Docker

- Confirm whether the agent has Docker access.
- Avoid broad host mounts unless required.
- Clean up images or containers when runners are long-lived.

## Artifacts

- Archive test reports and build artifacts explicitly.
- Keep artifact paths narrow enough to avoid uploading secrets or workspace caches.

## Deployment

- Require approval or protected branch conditions for production.
- Include rollback information in release notes or deployment output.
- Surface deployment URL, version, or image digest when available.
