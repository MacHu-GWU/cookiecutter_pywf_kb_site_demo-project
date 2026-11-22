#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Turn a WebVTT subtitle file (e.g. YouTube auto captions from yt-dlp) into plain paragraphs."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RE_TIMING = re.compile(r"^\d{2}:\d{2}(?::\d{2})?\.\d{3} --> ")
RE_TAG = re.compile(r"<[^>]+>")
HEADER_PREFIXES = ("WEBVTT", "Kind:", "Language:", "NOTE")


def vtt_lines(text: str) -> list[str]:
    """Caption text lines in order, with tags stripped and rolling duplicates removed."""
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if (
            not line
            or line.isdigit()
            or RE_TIMING.match(line)
            or line.startswith(HEADER_PREFIXES)
        ):
            continue
        line = re.sub(r"\s+", " ", RE_TAG.sub("", line)).strip()
        if line and (not lines or line != lines[-1]):
            lines.append(line)
    return lines


def _main(path: Path, lines_per_paragraph: int = 12) -> int:
    """Print the subtitle text of a .vtt file as paragraphs to stdout.

    Auto captions repeat each line across rolling cues; consecutive duplicates
    are dropped. Every lines_per_paragraph caption lines become one paragraph.

    Returns 0 on success, 1 on failure.
    """
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1
    lines = vtt_lines(path.read_text(encoding="utf-8"))
    if not lines:
        print(f"ERROR: no caption text in {path}", file=sys.stderr)
        return 1
    step = max(lines_per_paragraph, 1)
    paragraphs = [" ".join(lines[i : i + step]) for i in range(0, len(lines), step)]
    print("\n\n".join(paragraphs))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vtt_to_text",
        description="Turn a WebVTT subtitle file into plain paragraphs.",
    )
    parser.add_argument(
        "--path", type=Path, required=True, help="path to the .vtt file"
    )
    parser.add_argument(
        "--lines_per_paragraph",
        type=int,
        default=12,
        help="caption lines per output paragraph (default: 12)",
    )
    args = parser.parse_args(argv)
    return _main(path=args.path, lines_per_paragraph=args.lines_per_paragraph)


if __name__ == "__main__":
    sys.exit(main())
