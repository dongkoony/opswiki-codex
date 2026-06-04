# Runbook: Kubernetes CrashLoopBackOff

## Purpose

- Use this runbook when `Kubernetes CrashLoopBackOff` appears in OpsWiki notes.

## Scope

- Service: sample-obsidian-vault
- Severity: SEV3
- Source: local Markdown or Obsidian-style operational notes.

## Symptoms

- A pod repeatedly starts and exits, then Kubernetes reports `CrashLoopBackOff`.

## Confirmed Facts

- No confirmed facts were extracted from source notes.

## Assumptions

- Confirm environment, namespace, account, region, and affected workload before running commands.

## Safety Checks

- Start with read-only diagnosis before state-changing commands.
- Treat placeholder values such as `<namespace>` and `<pod>` as examples.
- Commands are documentation only; do not execute them from this generated runbook.

## Diagnosis Steps

- Collect logs, events, recent deployments, and ownership context before remediation.

## Commands

Commands are documentation only; do not execute them from this generated runbook.

```bash
kubectl get pods -n <namespace>
kubectl logs <pod> -n <namespace> --previous
kubectl describe pod <pod> -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
```

## Resolution Steps

- Fix configuration first when logs show missing settings.
- Roll back the deployment if the failure started immediately after a release.
- Do not delete multiple pods before checking rollout history.

## Rollback

- Confirm rollback target, blast radius, and owner approval before changing state.

## Verification

- Previous container logs show the startup failure.
- Pod description shows restart count and probe failures.
- The latest rollout references the intended image tag.

## Escalation

- Escalate to service owners when impact, ownership, or rollback safety is unclear.

## Related Notes

- Kubernetes CrashLoopBackOff
- Jenkins Docker Permission Denied
