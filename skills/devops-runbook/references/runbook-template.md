# DevOps Runbook Template

```markdown
# Runbook: <Issue or Service Name>

## Purpose
Explain when to use this runbook.

## Scope
- In scope:
- Out of scope:

## Symptoms
- Observable symptom:
- Alert or log signal:
- User impact:

## Confirmed Facts
- Fact supported by logs, metrics, config, or source notes.

## Assumptions
- Assumption that needs verification.

## Safety Checks
- Confirm the environment before changing anything.
- Confirm a recent backup, rollback path, or previous healthy version when relevant.
- Confirm whether the action affects shared infrastructure.

## Diagnosis Steps
1. Read-only check:
   ```bash
   command-that-does-not-change-state
   ```
2. Compare expected and actual behavior.

## Resolution Steps
1. State-changing action, if required:
   ```bash
   command-that-changes-state
   ```
2. Record who approved the action when approval is required.

## Rollback
```bash
command-or-procedure-to-return-to-last-known-good-state
```

## Verification
- Health check:
- Log check:
- Metric check:
- User-facing check:

## Escalation
- Escalate when:
- Include this evidence:

## Related Notes
- [[Related Operational Note]]
```

Replace angle-bracket placeholders before using the runbook in a live incident.
