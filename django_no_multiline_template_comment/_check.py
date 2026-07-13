from __future__ import annotations

import re

_SINGLE_LINE = re.compile(r"\{#[^\n]*?#\}")
_COMMENT = re.compile(r"\{#(.*?)#\}", re.DOTALL)

MESSAGE = (
    "multi-line '{# #}' comment — use '{% comment %}…{% endcomment %}' "
    "(a wrapped '{# #}' renders as visible text)"
)


def offending_lines(text: str) -> list[int]:
    """Return the 1-indexed lines where a ``{#`` opens a comment that wraps.

    Django's ``{# #}`` comment is single-line only. We blank every well-formed
    single-line comment (keeping newlines so line numbers stay put); any ``{#``
    left over opens a comment that runs onto a later line.
    """
    stripped = _SINGLE_LINE.sub(lambda m: " " * len(m.group()), text)
    return [i for i, line in enumerate(stripped.splitlines(), 1) if "{#" in line]


def fix(text: str) -> str:
    """Rewrite multi-line ``{# … #}`` comments to ``{% comment %}…{% endcomment %}``.

    Only comments that span lines (the broken ones) are converted; well-formed
    single-line ``{# … #}`` comments are left untouched. An unterminated ``{#``
    (no closing ``#}``) can't be paired, so it is left as-is and stays flagged.
    """

    def _replace(match: re.Match[str]) -> str:
        if "\n" not in match.group(0):
            return match.group(0)
        return "{% comment %}" + match.group(1) + "{% endcomment %}"

    return _COMMENT.sub(_replace, text)
