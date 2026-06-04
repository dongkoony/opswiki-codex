# Context Brief: sample-obsidian-vault

## Source Index
- `AWS Lambda InvalidArn.md` - AWS Lambda InvalidArn; tags: #aws, #lambda, #iam, #runbook; links: [[Terraform Security Group Review]]
- `Jenkins Docker Permission Denied.md` - Jenkins Docker Permission Denied; tags: #jenkins, #docker, #ci-cd; links: [[Kubernetes CrashLoopBackOff]]
- `Kubernetes CrashLoopBackOff.md` - Kubernetes CrashLoopBackOff; tags: #kubernetes, #triage, #runbook; links: [[Jenkins Docker Permission Denied]]
- `Terraform Security Group Review.md` - Terraform Security Group Review; tags: #terraform, #aws, #security; links: [[AWS Lambda InvalidArn]]

## Confirmed Facts
- From `AWS Lambda InvalidArn.md`: ARN strings must include the expected partition, service, region, account, and resource segments.
- From `AWS Lambda InvalidArn.md`: Cross-account invocation requires both caller permission and target resource policy support.
- From `AWS Lambda InvalidArn.md`: Region mismatch can make an otherwise valid ARN unusable for the caller.
- From `Jenkins Docker Permission Denied.md`: Docker access depends on the Jenkins agent model.
- From `Jenkins Docker Permission Denied.md`: Long-lived agents may need group membership or socket permissions.
- From `Jenkins Docker Permission Denied.md`: Containerized agents need explicit Docker socket or remote builder configuration.
- From `Terraform Security Group Review.md`: Security group ingress rules should use the narrowest practical CIDR or source security group.
- From `Terraform Security Group Review.md`: Public ingress must be documented and tied to a user-facing service.
- From `Terraform Security Group Review.md`: Egress rules can create data boundary concerns even when ingress is narrow.

## Assumptions
- From `AWS Lambda InvalidArn.md`: The example account IDs and function names in local notes are placeholders.
- From `AWS Lambda InvalidArn.md`: The caller is using an IAM role, not a static access key.

## Verification
- From `AWS Lambda InvalidArn.md`:

  ```bash
  aws lambda get-function --function-name <function-name> --region <region>
  aws sts get-caller-identity
  ```
- From `Jenkins Docker Permission Denied.md`:

  ```bash
  whoami
  id
  docker version
  ls -l /var/run/docker.sock
  ```
- From `Kubernetes CrashLoopBackOff.md`:

  ```bash
  kubectl get pods -n <namespace>
  kubectl logs <pod> -n <namespace> --previous
  kubectl describe pod <pod> -n <namespace>
  kubectl get events -n <namespace> --sort-by=.lastTimestamp
  ```
- From `Terraform Security Group Review.md`:

  ```bash
  terraform fmt -check -recursive
  terraform validate
  terraform plan
  ```

## Related Notes
- AWS Lambda InvalidArn links to [[Terraform Security Group Review]]
- Jenkins Docker Permission Denied links to [[Kubernetes CrashLoopBackOff]]
- Kubernetes CrashLoopBackOff links to [[Jenkins Docker Permission Denied]]
- Terraform Security Group Review links to [[AWS Lambda InvalidArn]]
