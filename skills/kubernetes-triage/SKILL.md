---
name: kubernetes-triage
description: Use when troubleshooting Kubernetes workloads, pods, deployments, services, ingress, events, CrashLoopBackOff, ImagePullBackOff, Pending pods, readiness failures, or cluster deployment issues.
---

# Kubernetes Triage

Use this skill to investigate Kubernetes problems with read-only checks first and clear separation between diagnosis and remediation.

## Workflow

1. Identify namespace, workload name, cluster context, and recent deployment activity.
2. Start with read-only commands for pods, events, rollout status, logs, and descriptions.
3. Classify the failure mode before recommending a fix.
4. State assumptions when namespace, cluster, image tag, or ownership is not confirmed.
5. Include rollback and verification steps for any state-changing action.

## Read-Only Commands

```bash
kubectl config current-context
kubectl get pods -n <namespace>
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace> --previous
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl rollout status deployment/<deployment> -n <namespace>
```

Replace angle-bracket values with confirmed names before running commands.

## State-Changing Commands

Call these out clearly before using them:

```bash
kubectl rollout undo deployment/<deployment> -n <namespace>
kubectl delete pod <pod> -n <namespace>
kubectl scale deployment/<deployment> --replicas=<count> -n <namespace>
```

## References

- `references/kubernetes-triage-checklist.md`
- `references/common-k8s-errors.md`
