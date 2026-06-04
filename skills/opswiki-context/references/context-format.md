# OpsWiki Context Format

Use this structure when compiling notes into Codex-ready context.

## Source Index

Record each source with:

- path or note title
- tags
- relevant wikilinks
- last-known scope, if the source says it

Example:

```markdown
Source: docs/runbooks/lambda-invalid-arn.md
Tags: aws, lambda, iam, incident
Links: [[Terraform Security Group Review]]
Scope: AWS Lambda invoke failures caused by malformed or cross-account ARNs
```

## Context Brief

```markdown
# Context Brief

## Confirmed Facts
- Fact that is directly supported by a source.

## Assumptions
- Assumption that is reasonable but not proven by the source.

## Operational Rules
- Rule Codex should follow while editing or reviewing the project.

## Verification
- Command, console check, log query, or manual inspection step.

## Open Questions
- Question that must be resolved before risky changes.
```

## Classification Guide

- Confirmed fact: directly present in a note, config file, runbook, issue, or source file.
- Assumption: inferred from naming, project layout, examples, or incomplete notes.
- Verification step: a command or observation that can prove the next step is safe.
- Resolution step: an action that changes the system, repository, deployment, or configuration.

## Style

- Keep summaries short enough to paste into AGENTS.md or a Codex prompt.
- Keep commands generic unless the source provides exact project values.
- Prefer bullet lists over prose when the output will guide operational action.
