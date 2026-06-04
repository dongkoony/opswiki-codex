# Model Serving Runbook

```markdown
# Runbook: Model Serving Incident

## Purpose
Use this runbook when an inference service has elevated errors, latency, bad responses, or suspected model artifact issues.

## Scope
- In scope: model artifact rollout, serving runtime, inference API, feature schema, monitoring.
- Out of scope: retraining strategy unless the incident requires rollback to a known-good model.

## Confirmed Facts
- Model name:
- Current version:
- Previous healthy version:
- Serving runtime:
- Deployment target:

## Assumptions
- List assumptions that need verification before action.

## Diagnosis
1. Check rollout status.
2. Check inference service logs.
3. Check latency, error rate, saturation, and restart metrics.
4. Check feature schema or payload validation errors.
5. Compare current model artifact reference with the previous healthy version.

## Resolution
1. Pause or reduce rollout if canary or weighted routing is available.
2. Roll back to the previous healthy artifact when user impact is confirmed.
3. Re-run smoke tests against the serving endpoint.

## Rollback
- Restore previous model artifact or image digest.
- Restore previous routing weight.
- Confirm health checks and model-specific metrics return to baseline.

## Verification
- Error rate returns to expected range.
- P95 latency returns to expected range.
- Payload schema errors stop increasing.
- Business or model-quality proxy metric is stable.
```
