---
name: mlops-deployment
description: Use when reviewing or creating MLOps deployment guidance, model serving runbooks, model artifact rollout plans, inference service troubleshooting, feature schema checks, canary releases, monitoring, or rollback steps.
---

# MLOps Deployment

Use this skill for deployment and operation of model-serving systems. Keep the output practical for engineers who need to ship, verify, monitor, and roll back models.

## Workflow

1. Identify model artifact, version, serving runtime, feature schema, and deployment target.
2. Confirm build, packaging, registry, and promotion boundaries.
3. Check rollout strategy, health checks, monitoring, and rollback path.
4. Include data and model-specific verification, not only infrastructure checks.
5. Separate confirmed facts, assumptions, verification steps, and resolution steps.

## Review Focus

- model artifact immutability and traceability
- feature schema compatibility
- dependency and runtime reproducibility
- canary, shadow, blue-green, or phased rollout strategy
- inference latency, error rate, saturation, and model-quality signals
- rollback to previous artifact or routing weight
- safe handling of datasets, labels, and customer data

## References

- `references/mlops-deployment-checklist.md`
- `references/model-serving-runbook.md`
