---
name: opswiki-context
description: Use when converting Markdown, Obsidian-style notes, or operational documentation into reusable Codex context, project-specific AGENTS.md guidance, or a compact DevOps/MLOps knowledge pack.
---

# OpsWiki Context

Use this skill to turn operational notes into structured context that Codex can safely reuse in a DevOps, MLOps, Cloud, or SRE project.

## Workflow

1. Identify the source notes, repository docs, and existing AGENTS.md files.
2. Preserve source boundaries by recording file paths, note titles, tags, and useful `[[wikilink]]` relationships.
3. Extract only operationally useful knowledge:
   - confirmed facts
   - assumptions
   - project conventions
   - runbook steps
   - verification commands
   - escalation or rollback guidance
4. Separate evergreen guidance from incident-specific details.
5. Convert the result into one of these outputs:
   - a concise context brief for the current Codex task
   - a reusable AGENTS.md section
   - a runbook seed
   - a checklist for infrastructure, CI/CD, Kubernetes, AWS, or MLOps review
6. Mark anything not proven by the source as an assumption.

## Output Rules

- Do not invent infrastructure names, account IDs, regions, namespaces, credentials, endpoints, or ownership.
- Do not include secrets, tokens, private keys, session cookies, or personal access keys.
- Prefer exact source paths over vague phrases such as "the docs say".
- Keep AGENTS.md output short, operational, and scoped to the project.
- Use clear sections for confirmed facts, assumptions, verification, and next actions.

## References

- `references/context-format.md`
- `references/agents-md-guidelines.md`
