# AGENTS.md

## Project Context

This example project operates cloud infrastructure and deployment workflows. OpsWiki notes are used as supporting context for DevOps, MLOps, Cloud, and SRE tasks.

## Operational Rules

- Separate confirmed facts from assumptions before proposing infrastructure, deployment, or incident actions.
- Do not include secrets, credentials, account IDs, private keys, or personal access keys in commits, examples, or responses.
- Treat namespace names, AWS accounts, regions, and service names in examples as placeholders unless source notes confirm them.
- For incident work, begin with read-only diagnosis steps before state-changing commands.
- For deployment work, include rollback and verification notes in the final response.

## Verification Commands

Run these only when the relevant toolchain exists in the project:

```bash
terraform fmt -check -recursive
terraform validate
terraform plan
kubectl config current-context
kubectl get pods -n <namespace>
```

## Review Focus

- Terraform: IAM scope, public ingress, encryption, state replacement, ownership tags.
- Kubernetes: rollout status, pod events, probes, logs, service selectors, rollback path.
- CI/CD: permissions, secrets, deployment gates, artifacts, Docker access, cache keys.
- MLOps: model artifact version, feature schema compatibility, rollout metrics, rollback target.

## Related OpsWiki Notes

- [[AWS Lambda InvalidArn]]
- [[Kubernetes CrashLoopBackOff]]
- [[Jenkins Docker Permission Denied]]
- [[Terraform Security Group Review]]
