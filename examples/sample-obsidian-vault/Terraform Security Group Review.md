# Terraform Security Group Review

Tags: #terraform #aws #security

Related: [[AWS Lambda InvalidArn]]

## Review Goal

Check whether a Terraform change broadens network access beyond the intended service boundary.

## Confirmed Facts

- Security group ingress rules should use the narrowest practical CIDR or source security group.
- Public ingress must be documented and tied to a user-facing service.
- Egress rules can create data boundary concerns even when ingress is narrow.

## Checklist

- Does any ingress rule use `0.0.0.0/0` or `::/0`?
- Is the exposed port required by the service?
- Is the source better represented as a security group reference?
- Are tags present for owner, service, and environment?
- Does the plan replace a security group attached to running workloads?

## Verification

```bash
terraform fmt -check -recursive
terraform validate
terraform plan
```

## Output Shape

Use confirmed facts, assumptions, verification, and findings in the review response.
