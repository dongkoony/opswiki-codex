# MLOps Deployment Checklist

## Artifact

- Confirm model name and version.
- Confirm artifact registry or storage location.
- Confirm checksum, digest, or immutable reference when available.
- Confirm training data and feature schema version when documented.

## Serving

- Confirm serving runtime and resource requirements.
- Confirm CPU, memory, GPU, and autoscaling settings.
- Confirm request and response schema compatibility.
- Confirm timeout and batch-size settings.

## Release

- Define rollout type: canary, shadow, blue-green, rolling, or manual.
- Define success metrics and abort conditions.
- Confirm rollback target.
- Confirm who approves production promotion.

## Monitoring

- Infrastructure: latency, errors, saturation, restarts.
- Model: prediction distribution, drift signal, confidence, business metric proxy.
- Data: schema mismatch, missing features, null rate, freshness.

## Verification

- Smoke test inference endpoint.
- Compare expected schema with live payload.
- Check recent logs for load or deserialization errors.
- Check dashboard or metric query for rollout window.
