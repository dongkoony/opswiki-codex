# Kubernetes Triage Checklist

## Context

- Confirm cluster context.
- Confirm namespace.
- Confirm workload type: Deployment, StatefulSet, DaemonSet, Job, CronJob, or bare Pod.
- Confirm whether a rollout happened recently.

## Pod State

- Pending: check scheduling, node selectors, taints, PVCs, and resource requests.
- CrashLoopBackOff: check previous logs, exit codes, probes, config, and dependencies.
- ImagePullBackOff: check image name, tag, registry auth, and pull policy.
- Running but not ready: check readiness probe, service dependencies, and startup time.
- Evicted: check node pressure and pod requests.

## Networking

- Confirm Service selector matches pod labels.
- Confirm Endpoints or EndpointSlices exist.
- Confirm Ingress routes to the expected Service and port.
- Check NetworkPolicy only after service and selector basics are verified.

## Configuration

- Check ConfigMap and Secret references.
- Check environment variables and mounted volumes.
- Check service account and RBAC when API calls fail.

## Verification

- Rollout status returns success.
- Ready pods match desired replicas.
- Recent logs do not show the original error.
- Service endpoints exist.
- External health check passes when applicable.
