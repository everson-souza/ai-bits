---
name: revisao-pr
description: Workflow to review commits and generate a pull request description. Use whenever the user asks for code review, commit analysis, or PR description drafting.
---

# Skill de revisão de commits e descrição de PR

## Workflow

Follow these steps IN THIS order:

1. **Overview first.** Call `list_changes` with the ref_base provided
  by the user (default: `HEAD~1` for the last commit; use `main` when
  reviewing an entire branch). Note the commits and the files touched.

2. **Read diffs.** Call `get_diff`. If the output is truncated or there
  are many files, call `get_diff` once per file, prioritizing the most
  relevant files (code over configs). Ignore generated/lock files in the
  detailed review, but mention them in the changes list.

3. **Fetch context when necessary.** If a diff snippet is unclear
  (partially modified function, use of something defined outside the diff),
  call `read_file` on the file in question. Do not read files that were
  not touched unless they are essential to understand a change.

4. **Review using the checklist:**
  - **Correctness**: obvious bugs, unhandled edge cases, inverted logic,
    off-by-one, resource leaks.
  - **Security**: committed secrets/credentials, injection (SQL, shell,
    path traversal), missing input validation.
  - **Clarity**: misleading names, dead code, introduced duplication.
  - **Consistency**: does the change follow the surrounding file style?
  - **Tests**: does the change include tests? If not, point that out.

5. **Generate the PR description.** Use the exact template in
  `references/template_pr.md` (read it before writing). Base EACH
  statement on what is present in the diffs — never invent behavior,
  motivation, or impact that cannot be verified in the changes.

## Rules

- Separate review findings from the PR description: first the findings
  list (if any), then the ready-to-copy PR description.
- Classify each finding as [critical], [suggestion], or [nit].
- If there are no relevant findings, state that in one line — do not
  invent issues to appear thorough.
  - Cite file and code snippet when pointing out a problem (e.g. `agente.py`,
  function `respond`).
- Write the PR description in English by default. If the commits and code
  are clearly in Portuguese, ask the user which language they prefer before
  generating the final description.

When emitting the PR description in the agent response, delimit it between
the lines `===PR===` and `===END===` so the caller can reliably extract it.
