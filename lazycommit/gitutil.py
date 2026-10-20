"""Thin wrappers around the git CLI."""

from __future__ import annotations

import subprocess


class GitError(RuntimeError):
    pass


def _run_git(args: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError as exc:
        raise GitError("git is not installed or not on PATH") from exc


def staged_diff(cwd: str | None = None) -> str:
    """Return the staged diff. Raise GitError outside a repo."""
    proc = _run_git(["diff", "--cached", "--no-color", "--no-ext-diff"], cwd=cwd)
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or "git diff failed - are you inside a git repository?")
    return proc.stdout


def staged_files(cwd: str | None = None) -> list[str]:
    proc = _run_git(["diff", "--cached", "--name-only"], cwd=cwd)
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or "git diff failed - are you inside a git repository?")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def commit(message: str, cwd: str | None = None) -> str:
    """Create a commit with the given message. Returns git's stdout."""
    proc = _run_git(["commit", "-m", message], cwd=cwd)
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or "git commit failed")
    return proc.stdout.strip()
