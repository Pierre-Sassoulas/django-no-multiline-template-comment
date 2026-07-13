"""Reject multi-line Django `{# #}` template comments. Used by pre-commit."""

from __future__ import annotations

import argparse
import logging
import sys

from django_no_multiline_template_comment._check import MESSAGE, fix, offending_lines

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    found = False
    for file_name in args.filenames:
        try:
            with open(file_name, encoding="utf8") as f:
                file_content = f.read()
        except UnicodeDecodeError as e:  # pragma: no cover
            logger.exception(e)
            continue
        lines = offending_lines(file_content)
        if not lines:
            continue
        found = True
        if args.fix:
            fixed = fix(file_content)
            if fixed != file_content:
                with open(file_name, "w", encoding="utf8") as f:
                    f.write(fixed)
                print(f"{file_name}: rewrote multi-line '{{# #}}' comment(s)")
                continue
        for line_number in lines:
            print(f"{file_name}:{line_number}: {MESSAGE}")
    sys.exit(1 if found else 0)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        metavar="FILES",
        help="File names to check",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        # No '%' here: argparse (3.14+) reads it as a format specifier.
        help="Rewrite offending multi-line comments to a comment/endcomment block.",
    )
    args = parser.parse_args(argv)
    return args


if __name__ == "__main__":  # pragma: no cover
    main()
