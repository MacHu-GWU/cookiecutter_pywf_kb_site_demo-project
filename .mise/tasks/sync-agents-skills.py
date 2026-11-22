# -*- coding: utf-8 -*-

"""
Copy the knowledge base skills from ``.claude/skills/`` (Claude Code, the
source) to ``.agents/skills/`` (Antigravity, a generated copy), mechanically.

Run it after every change to one of :data:`SKILLS` in ``.claude/skills/``;
never edit the ``.agents/skills/`` copy by hand. The port:

- rewrites every ``.claude/skills/`` path to ``.agents/skills/``;
- merges ``when_to_use`` into ``description`` (``"<description> Use when: <when_to_use>"``);
- turns ``argument-hint`` into a ``> Usage: `/<name> <hint>``` line under the front matter;
- names the agent's own web tools instead of Claude Code's (:data:`TOOL_WORDS`).

Skills that exist on one side only are left alone: ``antigravity-image-gen``
(Antigravity only), the ``pywf-oss-*`` family (Claude Code only).
"""

import re
import shutil
from pathlib import Path

dir_project_root = Path(__file__).absolute().parent.parent.parent
dir_claude_skills = dir_project_root / ".claude" / "skills"
dir_agents_skills = dir_project_root / ".agents" / "skills"

#: The skills that live in both ``.claude/skills/`` and ``.agents/skills/``.
SKILLS = [
    "blog-base",
    "blog-intake",
    "blog-plan",
    "blog-write",
    "blog-write-migrate-from-confluence",
    "blog-add-images",
    "sphinx-myst-kb-site",
    "sphinx-myst-kb-query",
    "sanhe-blog-language-style",
    "editorial-ink-art",
    "pypi-imgsqueeze",
]

#: Claude Code tool names in prose, and the words Antigravity reads instead.
TOOL_WORDS = [
    ("就改用 WebFetch,", "就改用 agent 自带的网页抓取工具,"),
    ("(WebSearch / WebFetch)", "(用网页搜索和网页抓取工具)"),
]

#: Text files whose content is ported; every other file is copied as is.
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".yml",
    ".txt",
    ".json",
    ".html",
    ".js",
    ".css",
    ".rst",
    ".ipynb",
}


def _unquote(value: str) -> str:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def port_front_matter(text: str, name: str) -> str:
    """
    Rewrite the front matter of a ``SKILL.md`` the way Antigravity reads it.
    """
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if match is None:
        raise ValueError(f"{name}: SKILL.md has no front matter")
    fields = dict()
    for line in match.group(1).splitlines():
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    description = _unquote(fields["description"])
    if "when_to_use" in fields:
        description = f"{description} Use when: {_unquote(fields['when_to_use'])}"
    out = f'---\nname: {fields["name"]}\ndescription: "{description}"\n---\n'
    if "argument-hint" in fields:
        out += f"\n> Usage: `/{name} {_unquote(fields['argument-hint'])}`\n"
    return out + text[match.end() :]


def port_skill(name: str):
    """
    Replace ``.agents/skills/<name>`` by a fresh port of ``.claude/skills/<name>``.
    """
    dir_src = dir_claude_skills / name
    dir_dst = dir_agents_skills / name
    if dir_dst.exists():
        shutil.rmtree(dir_dst)
    shutil.copytree(
        dir_src,
        dir_dst,
        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
    )
    for path in dir_dst.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        new_text = text.replace(".claude/skills/", ".agents/skills/")
        for before, after in TOOL_WORDS:
            new_text = new_text.replace(before, after)
        if path.name == "SKILL.md" and path.parent == dir_dst:
            new_text = port_front_matter(new_text, name)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")


def main():
    for name in SKILLS:
        port_skill(name)
        print(f"ported .claude/skills/{name} -> .agents/skills/{name}")


if __name__ == "__main__":
    main()
