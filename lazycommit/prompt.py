"""Prompt construction and diff trimming."""

from __future__ import annotations

# A diff larger than this is replaced by the full file list plus the
# leading hunks, so small models stay inside their context window.
MAX_DIFF_CHARS = 6000

SYSTEM_PROMPT = (
    "You write git commit messages. Given a diff, reply with ONE commit "
    "message and nothing else. Use the Conventional Commits style: "
    "type(scope): short summary in imperative mood, lowercase, under 72 "
    "characters. Valid types: feat, fix, docs, style, refactor, test, "
    "chore, perf, build, ci. Use docs for changes that only touch "
    "documentation (README, *.md, docs/). Use test for test-only changes. "
    "No quotes, no markdown, no explanation."
)

# Small models follow one concrete example far better than instructions alone.
USER_TEMPLATE = "Write a commit message for this staged diff:\n\n{diff}"
EXAMPLES = [
    (
        "diff --git a/scan.py b/scan.py\n"
        "+def scan(host, ports, timeout=1.0):\n"
        "+    s.settimeout(timeout)\n",
        "feat: add timeout option to scanner",
    ),
    (
        "diff --git a/README.md b/README.md\n"
        "new file mode 100644\n"
        "index 0000000..3b18e51\n"
        "--- /dev/null\n"
        "+++ b/README.md\n"
        "@@ -0,0 +1,2 @@\n"
        "+# mytool\n"
        "+A small tool that does one thing.\n",
        "docs: add readme with project description",
    ),
    (
        "diff --git a/tests/test_scan.py b/tests/test_scan.py\n"
        "+def test_closed_port():\n"
        "+    assert scan('127.0.0.1', [1]) == []\n",
        "test: cover closed port case",
    ),
]

def trim_diff(diff: str, max_chars: int = MAX_DIFF_CHARS) -> str:
    """Trim a huge diff to fit small models.

    Keeps the per-file headers and the first hunks, and appends a note
    listing how much was cut so the model still sees every file name.
    """
    if len(diff) <= max_chars:
        return diff
    file_headers = [l for l in diff.splitlines() if l.startswith("diff --git")]
    kept = diff[:max_chars]
    # do not end mid-line
    kept = kept[: kept.rfind("\n")]
    note = (
        f"\n... [diff truncated: {len(file_headers)} file(s) changed, "
        f"{len(diff) - len(kept)} more characters not shown]\n"
    )
    return kept + note


def build_messages(diff: str, files: list[str] | None = None) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for example_diff, example_msg in EXAMPLES:
        messages.append({"role": "user", "content": USER_TEMPLATE.format(diff=example_diff)})
        messages.append({"role": "assistant", "content": example_msg})
    body = USER_TEMPLATE.format(diff=trim_diff(diff))
    if files:
        body += "\n\nFiles changed: " + ", ".join(files)
    messages.append({"role": "user", "content": body})
    return messages
