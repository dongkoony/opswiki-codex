# AWS Terraform Patterns

## IAM

- Prefer least-privilege actions over `*`.
- Scope resources to exact ARNs when the resource identity is known.
- Use IAM conditions for cross-service access when supported.
- Keep human, workload, and CI roles separate.

## Networking

- Public ingress should be intentional and documented.
- Security groups should use service-specific ports and narrow CIDRs.
- Prefer explicit egress where compliance or data boundaries matter.
- Keep private workloads behind private subnets, internal load balancers, or service endpoints.

## Storage

- Enable encryption at rest where the AWS service supports it.
- Keep lifecycle and retention policies explicit.
- Avoid exposing sensitive values through outputs or tags.

## Compute

- Check deployment rollback path before replacing compute resources.
- Keep user data and environment variables free of secrets.
- Use instance profiles or workload identity instead of static keys.

## Observability

- Add logs, metrics, and alarms for user-facing or production resources.
- Include ownership tags so incidents can be routed.
- Capture resource names in outputs only when the values are not sensitive.

## Review Questions

- Could this plan affect production by selecting the wrong account, region, or workspace?
- Does the change broaden network or IAM access?
- Does any resource replacement need a maintenance window?
- Are backups, logs, and rollback paths clear enough for an on-call engineer?
