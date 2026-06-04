# Runbook: Kubernetes CrashLoopBackOff

## Purpose

Use this runbook when a Kubernetes workload repeatedly restarts and reports `CrashLoopBackOff`.

## Scope

- In scope: pod startup failures, container logs, probes, configuration, and recent rollouts.
- Out of scope: cluster-wide node outages unless pod events indicate scheduling or node pressure.

## Symptoms

- Pod status is `CrashLoopBackOff`.
- Restart count increases.
- Previous container logs show startup failure or early process exit.

## Confirmed Facts

- `kubectl logs --previous` can show the prior failed container execution.
- Pod events can show probe failures, image issues, or volume mount errors.
- Recent rollouts can introduce image, config, or dependency changes.

## Assumptions

- The namespace and deployment name must be confirmed before running commands.
- Example command values are placeholders.

## Diagnosis Steps

```bash
kubectl get pods -n <namespace>
kubectl logs <pod> -n <namespace> --previous
kubectl describe pod <pod> -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl rollout status deployment/<deployment> -n <namespace>
```

## Resolution Steps

1. Fix missing or invalid configuration when logs identify a config error.
2. Adjust startup or probe settings when the app is healthy but probes fail too early.
3. Roll back when the crash began immediately after a deployment.

## Rollback

```bash
kubectl rollout undo deployment/<deployment> -n <namespace>
```

## Verification

- Desired and ready replica counts match.
- Restart count stops increasing.
- Previous error no longer appears in logs.
- Service endpoints exist when the workload backs a service.
