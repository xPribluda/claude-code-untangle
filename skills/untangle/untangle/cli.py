"""untangle command line.

  untangle dump [SESSION] [--cwd DIR] [--out FILE] [--max-chars N]

SESSION is a session file path or id; without it, the newest session for
--cwd (default: current folder) is used.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .reader import find_session, read_session, to_text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="untangle")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dump", help="print a Claude Code session as a numbered transcript")
    d.add_argument("session", nargs="?")
    d.add_argument("--cwd")
    d.add_argument("--out")
    d.add_argument("--max-chars", type=int, default=2000)
    args = ap.parse_args(argv)

    path = find_session(args.session, args.cwd)
    messages = read_session(path)
    text = to_text(messages, args.max_chars)
    header = f"# session: {path}\n# messages: {len(messages)}, characters: {len(text)}\n\n"
    if args.out:
        Path(args.out).write_text(header + text, encoding="utf-8")
        print(header.strip())
        print(f"# written to: {args.out}")
    else:
        sys.stdout.write(header + text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
