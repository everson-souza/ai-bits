"""
Agent Skills loader.

Implements the Agent Skills pattern (agentskills.io) on the agent side:
    - discover_skills(): scans skills/*/SKILL.md and reads only frontmatter
    - build_system_prompt(): injects skill metadata into the system prompt
    - read_skill_file(): local tool to load the full content of a skill on demand
    - READ_SKILL_TOOL: tool definition in the API format

Expected structure of each skill:
    skills/
        <skill-name>/
            SKILL.md          (required: YAML frontmatter + instructions)
            references/       (optional: docs read only when needed)
            scripts/          (optional: executable code)
"""

from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"


def _read_frontmatter(skill_md_path: Path) -> dict | None:
    """Extracts `name` and `description` from a SKILL.md YAML frontmatter.

    Minimal parser (avoids PyYAML): expects frontmatter delimited by '---'
    with simple single-line keys or folded '>-' blocks.
    """
    lines = skill_md_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    metadata: dict[str, str] = {}
    current_key = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith((" ", "\t")) and current_key:
            metadata[current_key] += " " + line.strip()
        elif ":" in line:
            key, _, value = line.partition(":")
            current_key = key.strip()
            metadata[current_key] = value.strip().lstrip(">-").strip()
    if "name" in metadata and "description" in metadata:
        return metadata
    return None


def discover_skills(folder: Path = SKILLS_DIR) -> list[dict]:
    """Returns [{name, description, dir}] for each installed skill."""
    skills = []
    if not folder.is_dir():
        return skills
    for skill_md in sorted(folder.glob("*/SKILL.md")):
        meta = _read_frontmatter(skill_md)
        if meta:
            skills.append({**meta, "dir": skill_md.parent})
    return skills


def build_system_prompt(identity: str, skills: list[dict]) -> str:
    """Identity + skill metadata (first level of disclosure)."""
    if not skills:
        return identity
    lines = [identity, "", "## Installed skills", ""]
    for s in skills:
        lines.append(f"- **{s['name']}**: {s['description']}")
    lines += [
        "",
        "Before performing a task covered by a skill, read the file ",
        "'<skill-name>/SKILL.md' using the read_skill_file tool and follow ",
        "its instructions. Read files in references/ only when the SKILL.md ",
        "indicates.",
    ]
    return "\n".join(lines)


def read_skill_file(relative_path: str, folder: Path = SKILLS_DIR) -> str:
    """LOCAL tool: reads a file inside the skills folder, with
    protection against path traversal (../../etc/passwd will be rejected)."""
    base_dir = folder.resolve()
    target = (base_dir / relative_path).resolve()
    if not target.is_relative_to(base_dir):
        return "Error: path outside the skills folder."
    if not target.is_file():
        return f"Error: file '{relative_path}' not found."
    return target.read_text(encoding="utf-8")


READ_SKILL_TOOL = {
    "name": "read_skill_file",
    "description": (
        "Reads a file from an installed skill. Use to load a skill's SKILL.md "
        "before performing a task covered by it, or to read reference files "
        "mentioned by the SKILL.md."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": (
                    "Path relative to the skills/ folder. "
                    "E.g.: 'atendimento/SKILL.md' or "
                    "'atendimento/references/escalonamento.md'"
                ),
            }
        },
        "required": ["path"],
    },
}