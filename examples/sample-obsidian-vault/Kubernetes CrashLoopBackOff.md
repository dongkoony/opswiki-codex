# Kubernetes CrashLoopBackOff

Tags: #kubernetes #triage #runbook

Related: [[Jenkins Docker Permission Denied]]

## Symptom

A pod repeatedly starts and exits, then Kubernetes reports `CrashLoopBackOff`.

## Read-Only Checks

```bash
kubectl get pods -n <namespace>
kubectl logs <pod> -n <namespace> --previous
kubectl describe pod <pod> -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
```

## Common Causes

- Missing environment variable.
- Application cannot connect to a required dependency.
- File permission problem on a mounted volume.
- Liveness probe kills the container before startup completes.
- Image command or args exit immediately.

## Verification

- Previous container logs show the startup failure.
- Pod description shows restart count and probe failures.
- The latest rollout references the intended image tag.

## Resolution Notes

- Fix configuration first when logs show missing settings.
- Roll back the deployment if the failure started immediately after a release.
- Do not delete multiple pods before checking rollout history.
