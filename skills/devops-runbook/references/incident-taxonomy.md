# Incident Taxonomy

Use these categories to classify operational notes and runbooks.

## Availability

- service unavailable
- elevated error rate
- timeout
- dependency outage
- failed deployment

## Performance

- latency regression
- queue backlog
- CPU saturation
- memory pressure
- slow database query

## Configuration

- invalid ARN
- missing environment variable
- wrong region
- wrong namespace
- incorrect IAM permission
- stale DNS or certificate setting

## Data and State

- migration failure
- schema mismatch
- storage quota
- corrupted artifact
- replay or backfill issue

## CI/CD

- failed build
- failed test stage
- artifact upload failure
- container permission issue
- missing secret or environment binding

## Kubernetes

- CrashLoopBackOff
- ImagePullBackOff
- Pending pod
- failed readiness probe
- failed liveness probe
- service endpoint mismatch

## MLOps

- model artifact missing
- model version mismatch
- feature schema drift
- serving latency regression
- rollback to previous model

## Severity Hints

- SEV1: broad outage, data loss risk, or critical production path unavailable.
- SEV2: degraded production behavior with workaround or partial scope.
- SEV3: limited user impact, non-critical failure, or internal workflow issue.
- SEV4: documentation, cleanup, or low-risk follow-up.
