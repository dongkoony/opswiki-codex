# AGENTS.md

## Project Context
- Generated from OpsWiki notes in `examples/sample-obsidian-vault` for `sample-obsidian-vault`.

## Operational Rules
- Separate confirmed facts from assumptions before proposing infrastructure, deployment, or incident actions.
- Begin incident work with read-only diagnosis before state-changing commands.
- Treat example names, namespaces, accounts, regions, and service identifiers as placeholders unless source notes confirm them.
- Do not include secrets, credentials, private keys, tokens, or personal access keys in commits or generated output.

## Verification Commands

```bash
aws lambda get-function --function-name <function-name> --region <region>
aws sts get-caller-identity
```

```bash
whoami
id
docker version
ls -l /var/run/docker.sock
```

```bash
kubectl get pods -n <namespace>
kubectl logs <pod> -n <namespace> --previous
kubectl describe pod <pod> -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
```

```bash
terraform fmt -check -recursive
terraform validate
terraform plan
```

## Review Focus
- Terraform and AWS: IAM scope, public ingress, state impact, and ownership tags.
- Kubernetes: pod state, rollout status, probes, events, and rollback path.
- CI/CD: credentials, Docker access, deployment gates, artifacts, and logs.

## Related OpsWiki Notes
- [[AWS Lambda InvalidArn]]
- [[Jenkins Docker Permission Denied]]
- [[Kubernetes CrashLoopBackOff]]
- [[Terraform Security Group Review]]
