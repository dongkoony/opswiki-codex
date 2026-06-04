# Terraform Review Checklist

## Scope

- Identify all changed `.tf`, `.tfvars`, module, and provider files.
- Confirm whether the change is for development, staging, production, or shared infrastructure.
- Check whether backend, workspace, or provider aliases changed.

## Safety

- Look for forced replacement in plan output.
- Check for state moves, imports, or resource renames.
- Confirm destructive actions are intentional and reversible.
- Confirm data sources do not depend on unstable names.

## Security

- Avoid `0.0.0.0/0` ingress unless the service is explicitly public.
- Avoid wildcard IAM permissions unless bounded by resource, condition, or documented exception.
- Check encryption for storage, queues, databases, logs, and backups.
- Do not output secrets, tokens, passwords, or private keys.

## Reliability

- Check health checks, timeouts, lifecycle rules, deletion protection, and backup retention.
- Confirm multi-AZ or redundancy assumptions when the source claims high availability.
- Check autoscaling defaults and quotas.

## Operability

- Check tags for owner, service, environment, and cost center when required.
- Check logging, metrics, alarms, and dashboard hooks.
- Confirm names are stable and predictable without colliding across environments.

## Review Output

Use this shape:

```markdown
## Findings
- [severity] file:line - Issue and operational impact.

## Assumptions
- What could not be proven from the diff.

## Verification
- Command or plan excerpt needed before merge.
```
