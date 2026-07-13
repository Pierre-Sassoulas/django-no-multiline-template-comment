"""Golden-master tests for the checker, driven by pytest-remaster.

Each ``tests/fixtures/*.html`` template is run through the checker and its report
(``line: message`` per offending line) is compared to a golden ``<name>.out`` file
sitting next to it. A clean template produces no report and therefore has no
golden file. Regenerate the goldens after an intentional behaviour change with::

    pytest --remaster

CLI exit codes are covered separately below (a golden captures output, not the
process exit status).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from pytest_remaster import CaseData, GoldenMaster, discover_test_files

from django_no_multiline_template_comment.__main__ import main
from django_no_multiline_template_comment._check import MESSAGE, fix, offending_lines

FIXTURES = Path(__file__).parent / "fixtures"


def _report(template: Path) -> str:
    text = template.read_text(encoding="utf-8")
    return "\n".join(f"{line}: {MESSAGE}" for line in offending_lines(text))


@pytest.mark.parametrize("case", discover_test_files(FIXTURES, "*.html"))
def test_fixture_report(case: CaseData, golden_master: GoldenMaster) -> None:
    golden_master.check(_report(case.input), case.expected(suffix=".out"))


def test_cli_clean_template_passes(capsys: pytest.CaptureFixture[str]) -> None:
    template = FIXTURES / "single_line_ok.html"
    with patch("sys.argv", ["prog", str(template)]):
        with pytest.raises(SystemExit) as exit_info:
            main()
    assert exit_info.value.code == 0
    assert capsys.readouterr().out == ""


def test_cli_wrapped_template_fails(capsys: pytest.CaptureFixture[str]) -> None:
    template = FIXTURES / "wrapped_comment.html"
    with patch("sys.argv", ["prog", str(template)]):
        with pytest.raises(SystemExit) as exit_info:
            main()
    assert exit_info.value.code == 1
    # `{#` opens on line 2 (not the `#}` line); output is prefixed with the path.
    assert f"{template}:2: {MESSAGE}" in capsys.readouterr().out


def test_cli_no_args_passes() -> None:
    with patch("sys.argv", ["prog"]):
        with pytest.raises(SystemExit) as exit_info:
            main()
    assert exit_info.value.code == 0


def test_fix_converts_multiline_only() -> None:
    text = "<p>{# ok #}</p>\n{# broken\n   wraps #}\n"
    fixed = fix(text)
    assert "{# ok #}" in fixed  # valid single-line comment left untouched
    assert "{% comment %} broken\n   wraps {% endcomment %}" in fixed
    assert offending_lines(fixed) == []  # no longer offending


def test_fix_is_noop_on_clean_template() -> None:
    text = "<p>{# fine #}</p>\n{# also fine #}\n"
    assert fix(text) == text


def test_cli_fix_rewrites_offending_file(tmp_path: Path) -> None:
    template = tmp_path / "page.html"
    template.write_text("{# a\n b #}\n", encoding="utf-8")
    with patch("sys.argv", ["prog", "--fix", str(template)]):
        with pytest.raises(SystemExit) as exit_info:
            main()
    # A modified file fails the run so pre-commit re-stages it.
    assert exit_info.value.code == 1
    rewritten = template.read_text(encoding="utf-8")
    assert "{% comment %}" in rewritten
    assert offending_lines(rewritten) == []


def test_cli_fix_leaves_unterminated_comment(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    original = "{# no closing tag here\n<p>x</p>\n"
    template = tmp_path / "page.html"
    template.write_text(original, encoding="utf-8")
    with patch("sys.argv", ["prog", "--fix", str(template)]):
        with pytest.raises(SystemExit) as exit_info:
            main()
    assert exit_info.value.code == 1
    assert MESSAGE in capsys.readouterr().out  # reported, not silently "fixed"
    assert template.read_text(encoding="utf-8") == original
