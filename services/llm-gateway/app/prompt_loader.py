from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

RE_METADATA_LINE = re.compile(r"^(?P<key>[a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(?P<value>.+?)\s*$")
REQUIRED_KEYS = ("prompt_name", "prompt_version", "source_agent_reference")


@dataclass(frozen=True)
class PromptTemplate:
    prompt_name: str
    prompt_version: str
    source_agent_reference: str
    content: str


def load_prompt(prompt_path: Path) -> PromptTemplate:
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    raw_text = prompt_path.read_text(encoding="utf-8").strip()
    lines = raw_text.splitlines()

    metadata: dict[str, str] = {}
    body_start_index = 0
    for idx, line in enumerate(lines):
        if not line.strip():
            body_start_index = idx + 1
            break

        match = RE_METADATA_LINE.match(line.strip())
        if not match:
            body_start_index = idx
            break

        metadata[match.group("key")] = match.group("value").strip()

    missing = [key for key in REQUIRED_KEYS if key not in metadata]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Prompt metadata missing required keys: {joined}")

    content = "\n".join(lines[body_start_index:]).strip()
    if not content:
        raise ValueError(f"Prompt has no body content: {prompt_path}")

    return PromptTemplate(
        prompt_name=metadata["prompt_name"],
        prompt_version=metadata["prompt_version"],
        source_agent_reference=metadata["source_agent_reference"],
        content=content,
    )
