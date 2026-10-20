"""Turn raw model output into one clean commit message line."""

from __future__ import annotations

import re

_PREFIXES = re.compile(
    r"^(commit message|message|output|answer|response)\s*[:\-]\s*", re.IGNORECASE
)


def clean(raw: str) -> str:
    """Best-effort cleanup of small-model output.

    Strips markdown fences, quotes, common lead-ins, then takes the first
    non-empty line. Never invents content: if nothing usable remains, the
    caller gets an empty string and must handle it honestly.
    """
    text = raw.strip()
    # drop markdown code fences the model may wrap around the answer
    text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    for line in text.splitlines():
        line = _PREFIXES.sub("", line.strip())
        line = line.strip().strip('"').strip("'").strip("`").strip()
        if line:
            # conventional commits: summary starts lowercase
            m = re.match(r"^([a-z]+(\([^)]*\))?!?:\s+)([A-Z])(.*)$", line)
            if m:
                line = m.group(1) + m.group(3).lower() + m.group(4)
            return line
    return ""
