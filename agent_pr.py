"""
Commit review agent + PR description generator.

Reuses the Assistant class (agent.py), changing:
    - the MCP server: git_server.py (read-only git tools)
    - the identity: code reviewer
    - the mode: single-run (non-interactive) — runs, prints the review and
        saves the PR description to DESCRICAO_PR.md

The review workflow itself (step order, checklist, PR template)
is NOT in this code: it lives in the skill skills/revisao-pr/, which the
model reads on demand. To change the review process, edit the skill's
markdown.

Usage:
    python agent_pr.py /path/to/repo [base_ref]

    base_ref (optional): 'main' to review the branch against main,
    'HEAD~1' (default) to review only the last commit, 'HEAD~3' for the
    last three commits, etc.

Requirements:
    pip install mcp anthropic
    export ANTHROPIC_API_KEY="your-key"
"""

import asyncio
import sys
from pathlib import Path

from agent import Assistant

REVIEWER_IDENTITY = (
    "You are a senior code reviewer. You analyze changes in "
    "git repositories, point out issues precisely, and write clear "
    "pull request descriptions. You must not assert anything that "
    "you cannot verify in the diffs."
)

OUTPUT_FILE = "DESCRICAO_PR.md"


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python agent_pr.py /path/to/repo [base_ref]")
        sys.exit(1)

    repo = str(Path(sys.argv[1]).resolve())
    ref_base = sys.argv[2] if len(sys.argv) > 2 else "HEAD~1"

    assistant = Assistant(identity=REVIEWER_IDENTITY)
    try:
        await assistant.connect_stdio_server(
            command=sys.executable, args=["git_server.py", repo]
        )

        task = (
            f"Review the repository changes relative to '{ref_base}' and "
            "generate a pull request description. At the end of the reply, "
            "delimit the PR description between the lines '===PR===' and "
            "'===END===' so I can extract it."
        )
        response = await assistant.respond(task)
        print("\n" + response)

        # Extract and save only the PR description if the delimiter is present
        if "===PR===" in response and "===END===" in response:
            description = response.split("===PR===")[1].split("===END===")[0]
            Path(OUTPUT_FILE).write_text(description.strip() + "\n", "utf-8")
            print(f"\n[ok] PR description saved to {OUTPUT_FILE}")
    finally:
        await assistant.close()


if __name__ == "__main__":
    asyncio.run(main())