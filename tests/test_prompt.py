from lazycommit import prompt


def test_short_diff_is_kept_verbatim():
    diff = "diff --git a/x.py b/x.py\n+print('hi')\n"
    assert prompt.trim_diff(diff) == diff


def test_long_diff_is_truncated_with_note():
    diff = "diff --git a/big.py b/big.py\n" + ("+line\n" * 5000)
    out = prompt.trim_diff(diff, max_chars=1000)
    assert len(out) < 1200
    assert "diff truncated" in out
    assert "1 file(s) changed" in out


def test_build_messages_has_system_and_user():
    msgs = prompt.build_messages("diff --git a/x b/x\n+a\n")
    assert msgs[0]["role"] == "system"
    assert "Conventional Commits" in msgs[0]["content"]
    assert msgs[-1]["role"] == "user"
    assert "diff --git" in msgs[-1]["content"]
    assert msgs[-2]["role"] == "assistant"  # one-shot example for small models
