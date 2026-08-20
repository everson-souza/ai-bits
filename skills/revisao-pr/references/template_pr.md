# PR description template

Use this exact structure (in Markdown), filling it based on the diffs:

```markdown
## Summary

<1-3 sentences: what this PR does and why, as far as the commits and
diffs allow you to infer. Do not invent motivation.>

## Changes

<One-line items for each relevant change, grouped by area when helpful.
Each item should cite the file(s):>
- <description of change> (`file.py`)

## How to test

<Objective steps to verify the change. If the PR includes tests, indicate
the command to run them. If it cannot be inferred from the diffs, write
"To be provided by the author." >

## Risks and notes

<Breaking changes, required migrations, new dependencies, reviewer
attention points. If none, write "None identified." >
```

Filling rules:
- Everything must be verifiable in the diffs; nothing speculative without
  explicit hedging ("appears", "I assume"). Minimize speculation.
- Mention added/removed dependencies (requirements, package.json,
  pyproject) in the Risks section.
- If the diff includes generated or lock files, mention them in a single
  line under Changes without detailing them.
