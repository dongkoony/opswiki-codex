# Common Kubernetes Errors

## CrashLoopBackOff

Likely causes:

- application exits on startup
- missing environment variable
- failed database or service dependency
- permission error on mounted volume
- liveness probe kills the process too early

Checks:

```bash
kubectl logs <pod> -n <namespace> --previous
kubectl describe pod <pod> -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
```

## ImagePullBackOff

Likely causes:

- wrong image name or tag
- private registry credentials missing
- registry unavailable
- image pull policy mismatch

Checks:

```bash
kubectl describe pod <pod> -n <namespace>
kubectl get secret -n <namespace>
```

## Pending Pod

Likely causes:

- insufficient CPU or memory
- PVC cannot bind
- node selector does not match any node
- taints require tolerations

Checks:

```bash
kubectl describe pod <pod> -n <namespace>
kubectl get nodes
kubectl get pvc -n <namespace>
```

## Readiness Probe Failed

Likely causes:

- application is slow to start
- wrong probe path or port
- dependency is unavailable
- service listens on a different interface

Checks:

```bash
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace>
```
