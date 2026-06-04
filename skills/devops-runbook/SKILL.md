---
name: devops-runbook
description: Use when creating, reviewing, or improving DevOps/SRE runbooks, incident notes, troubleshooting guides, post-incident summaries, rollback steps, or operational checklists.
---

# DevOps Runbook

Use this skill for practical operational documentation. The goal is a runbook that helps an engineer diagnose, verify, act, and recover without guessing.

## Workflow

1. Identify the service, system boundary, severity, and affected users.
2. Separate confirmed facts from assumptions before proposing resolution steps.
3. Capture read-only diagnosis steps before any state-changing action.
4. Include escalation signals, rollback conditions, and verification steps.
5. Keep commands generic unless the source provides safe project-specific values.
6. End with evidence to collect for follow-up.

## Runbook Sections

- Purpose
- Scope
- Symptoms
- Confirmed facts
- Assumptions
- Safety checks
- Diagnosis steps
- Resolution steps
- Rollback
- Verification
- Escalation
- Related notes

## Safety Rules

- Do not recommend destructive commands without a clear backup, rollback, or approval gate.
- Do not include secrets, tokens, account IDs, private endpoints, or customer data.
- Mark commands that change state.
- Prefer reversible actions first.
- Never claim production readiness without verification evidence.

## References

- `references/runbook-template.md`
- `references/incident-taxonomy.md`
