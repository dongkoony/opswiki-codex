# AWS Lambda InvalidArn

Tags: #aws #lambda #iam #runbook

Related: [[Terraform Security Group Review]]

## Symptom

Lambda invocation fails with an `InvalidArn` style error during deployment or integration testing.

## Confirmed Facts

- ARN strings must include the expected partition, service, region, account, and resource segments.
- Cross-account invocation requires both caller permission and target resource policy support.
- Region mismatch can make an otherwise valid ARN unusable for the caller.

## Assumptions

- The example account IDs and function names in local notes are placeholders.
- The caller is using an IAM role, not a static access key.

## Verification

```bash
aws lambda get-function --function-name <function-name> --region <region>
aws sts get-caller-identity
```

## Resolution Notes

- Confirm the ARN is assembled from the same region and account as the target function.
- Confirm IAM policy resource scope matches the target Lambda ARN.
- Confirm the deployment template does not mix environment names in variables.
