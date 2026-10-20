"""lazycommit command line interface."""

from __future__ import annotations

import argparse
import os
import sys

from . import __version__, backend, cleanup, gitutil, prompt


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lazycommit",
        description="Write commit messages with a local, open-weight model. "
        "Your diff never leaves your machine.",
    )
    p.add_argument(
        "-c",
        "--commit",
        action="store_true",
        help="create the commit with the generated message "
        "(default: print the message only)",
    )
    p.add_argument(
        "--base-url",
        default=os.environ.get("LAZYCOMMIT_BASE_URL", backend.DEFAULT_BASE_URL),
        help="OpenAI-compatible server URL "
        "(env LAZYCOMMIT_BASE_URL, default %(default)s)",
    )
    p.add_argument(
        "--model",
        default=os.environ.get("LAZYCOMMIT_MODEL", backend.DEFAULT_MODEL),
        help="model name on that server (env LAZYCOMMIT_MODEL, default %(default)s)",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        diff = gitutil.staged_diff()
    except gitutil.GitError as exc:
        print(f"lazycommit: {exc}", file=sys.stderr)
        return 2

    if not diff.strip():
        print(
            "lazycommit: nothing staged. Stage your changes first: git add -p",
            file=sys.stderr,
        )
        return 2

    files = gitutil.staged_files()
    print(f"lazycommit: {len(files)} staged file(s): {', '.join(files)}")
    print(f"lazycommit: asking {args.model} at {args.base_url} ...")

    try:
        raw = backend.chat(
            prompt.build_messages(diff, files=files), base_url=args.base_url, model=args.model
        )
    except backend.BackendError as exc:
        print(f"lazycommit: {exc}", file=sys.stderr)
        return 3

    message = cleanup.clean(raw)
    if not message:
        print(
            "lazycommit: the model returned nothing usable. "
            "Write this one by hand (sorry).",
            file=sys.stderr,
        )
        return 3

    if not args.commit:
        print(message)
        return 0

    try:
        out = gitutil.commit(message)
    except gitutil.GitError as exc:
        print(f"lazycommit: {exc}", file=sys.stderr)
        return 2
    print(f"lazycommit: committed as: {message}")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
