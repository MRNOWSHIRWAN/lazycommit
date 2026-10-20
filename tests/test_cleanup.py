from lazycommit import cleanup


def test_plain_message_passes_through():
    assert cleanup.clean("feat(auth): add login retry") == "feat(auth): add login retry"


def test_strips_code_fence():
    assert cleanup.clean("```\nfix: handle empty diff\n```") == "fix: handle empty diff"


def test_strips_quotes_and_prefix():
    assert cleanup.clean('Commit message: "docs: update readme"') == "docs: update readme"


def test_takes_first_non_empty_line():
    assert cleanup.clean("\n\ntest: add cleanup tests\nextra explanation") == "test: add cleanup tests"


def test_empty_when_nothing_usable():
    assert cleanup.clean("   \n ``` \n") == ""


def test_summary_lowercased_after_prefix():
    assert cleanup.clean("feat(auth): Add retry logic") == "feat(auth): add retry logic"


def test_non_conventional_message_untouched():
    assert cleanup.clean("Add retry logic") == "Add retry logic"
