"""
MCP server exposing git tools for commit and PR review.

Exposes three read-only tools over a local repository:
    - list_changes(ref_base): commits and files changed since ref_base
    - get_diff(ref_base, file): diff of files since ref_base
    - read_file(path): current content of a file (extra context)

The path to the local repository must be passed as an argument when running
the script. Example:
    python servidor_git.py /path/to/repo
"""

import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("git-revisao")

REPO = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
MAX_CHARS = 20_000  # Protect model context against huge diffs


def _git(*args: str) -> str:
    """Run a git command in the repository and return its output."""
    resultado = subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    if resultado.returncode != 0:
        return f"Error running git: {resultado.stdout.strip()}"
    return resultado.stdout

def _truncate(text: str, limit: int = MAX_CHARS) -> str:
    """Truncate text to the character limit if necessary."""
    if len(text) <= limit:
        return text
    return (
        text[:limit]
        + f"\n\n[... truncated: {len(text) - limit} characters omitted. "
        "Use get_diff with the 'file' parameter to view one file at a time.]"
    )

@mcp.tool()
def list_changes(ref_base: str = "HEAD~1") -> str:
    """List commits and files changed from ref_base to HEAD.

    Use as the FIRST step of any review to get an overview before diving into diffs.

    Args:
        ref_base: Comparison reference. E.g.: 'main', 'HEAD~1', 'HEAD~3'.
    """
    commits = _git("log", "--oneline", f"{ref_base}..HEAD")
    files = _git("diff", "--name-only", f"{ref_base}..HEAD")
    if commits.startswith("Error") or files.startswith("Error"):
        return commits if commits.startswith("Error") else files
    if not commits.strip():
        return f"No commits found since '{ref_base}'."
    return (
        f"## Commits ({ref_base}..HEAD)\n{commits}\n"
        f"## Changed files\n{files}"
    )

@mcp.tool()
def get_diff(ref_base: str = "HEAD~1", file: str = "") -> str:
    """
    Return the diff between ref_base and HEAD.

    Args:
        ref_base: Comparison reference (e.g.: 'main', 'HEAD~1').
        file: Optional file path to limit the diff to a specific file.
    """
    args = ["diff", f"{ref_base}..HEAD"]
    if file:
        args += ["--", file]
    return _truncate(_git(*args) or "Empty diff.")

@mcp.tool()
def read_file(path: str) -> str:
    """
    Read the CURRENT content of a file in the repository.

    Use when the diff alone does not provide enough context (e.g. to
    understand a function that was partially modified).

    Args:
        path: File path relative to the repository root.
    """
    target = (REPO / path).resolve()
    if not target.is_relative_to(REPO):
        return f"Error: the file '{path}' is not inside the repository."
    if not target.is_file():
        return f"Error: the path '{path}' does not point to a file."
    return _truncate(target.read_text(encoding="utf-8", errors="replace"))

if __name__ == "__main__":
    mcp.run(transport="stdio")
    