---
name: terraform-review
description: Use when reviewing Terraform or OpenTofu changes, especially AWS infrastructure, IAM, networking, security groups, state changes, module patterns, cost risk, or drift-sensitive IaC updates.
---

# Terraform Review

Use this skill to review infrastructure-as-code changes with an operational lens.

## Workflow

1. Identify changed Terraform files, modules, variables, providers, and backend configuration.
2. Check formatting, validation, and plan output when available.
3. Review security, IAM scope, network exposure, state impact, naming, tagging, and lifecycle settings.
4. Separate findings into confirmed issues, assumptions, and verification questions.
5. Prefer small, actionable review comments with file and line references when possible.

## Review Focus

- public ingress, broad CIDR blocks, and overly permissive security groups
- wildcard IAM actions or resources
- resources that may be replaced instead of updated
- missing encryption, logging, retention, or backup settings
- provider or module version drift
- environment naming that could target the wrong account, region, or workspace
- missing tags required for ownership, cost, or compliance
- outputs that could expose sensitive values

## Suggested Commands

Run only when the repository and toolchain support them:

```bash
terraform fmt -check -recursive
terraform validate
terraform plan
```

For OpenTofu projects:

```bash
tofu fmt -check -recursive
tofu validate
tofu plan
```

## References

- `references/terraform-review-checklist.md`
- `references/aws-terraform-patterns.md`
