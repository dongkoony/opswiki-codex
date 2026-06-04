# AGENTS.md Guidelines

OpsWiki-generated AGENTS.md content should guide Codex without turning the project into a static wiki.

## Recommended Sections

```markdown
# AGENTS.md

## Project Context
- What this project operates and which environment boundaries matter.

## Operational Rules
- Rules Codex must follow before changing infrastructure, deployment, or CI/CD files.

## Verification Commands
- Commands that are safe to run locally.

## Review Focus
- Terraform, Kubernetes, CI/CD, AWS, or MLOps checks that matter for this project.

## Incident Notes
- Short references to runbooks or known failure modes.
```

## Writing Rules

- Use project-specific rules only when they are supported by source notes.
- Keep secrets and account-specific credentials out of AGENTS.md.
- Put incident history in a short reference list, not a long narrative.
- Make verification commands explicit and safe.
- Include assumptions only when they affect Codex behavior.

## Good AGENTS.md Guidance

```markdown
- For Terraform changes, run `terraform fmt -check` and `terraform validate` when Terraform is available.
- Treat Kubernetes namespace names in examples as placeholders unless a source note confirms them.
- For deployment changes, include rollback and health-check notes in the final response.
```

## Poor AGENTS.md Guidance

```markdown
- Always deploy after editing Terraform.
- Use the production account by default.
- Restart every pod when Kubernetes looks unhealthy.
```
