# django-no-multiline-template-comment

[![PyPI version](https://badge.fury.io/py/django-no-multiline-template-comment.svg)](https://badge.fury.io/py/django-no-multiline-template-comment)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

`django-no-multiline-template-comment` rejects multi-line Django `{# … #}` template
comments.

## Why

Django's `{# #}` comment is **single-line only**. A `{#` whose closing `#}` is on a
later line does **not** comment the following lines — they render as visible text on the
page. Use `{% comment %}…{% endcomment %}` for anything that may wrap. This hook catches
the mistake in CI.

```jinja
{# ✗ broken: this comment
   spans two lines, so everything here leaks onto the page as text #}

{# ✓ fixed: single-line comment #}
{% comment %}
   ...or {% comment %} for anything that may wrap.
{% endcomment %}
```

## Installation

```yaml
- repo: https://github.com/Pierre-Sassoulas/django-no-multiline-template-comment/
  rev: v0.0.2
  hooks:
    - id: django-no-multiline-template-comment
```

## Autofix

Pass `--fix` to rewrite offending comments to `{% comment %}…{% endcomment %}` in place
(valid single-line comments and unterminated `{#` are left untouched). As with other
fixer hooks, a rewritten file fails the run so you review and re-stage it.

```yaml
- repo: https://github.com/Pierre-Sassoulas/django-no-multiline-template-comment/
  rev: v0.0.2
  hooks:
    - id: django-no-multiline-template-comment
      args: [--fix]
```
