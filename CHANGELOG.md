# Changelog

## 0.2.3 - 2026-07-29

- README shows a real terminal recording instead of a hand-drawn SVG. It is generated from
  live runs by `scripts/demo_gif.py`, so it cannot drift away from the actual output.
- A clean scan prints a one line summary instead of an empty table.
- Severity is coloured in the findings table, and the table title reports how many files were
  scanned.
- Fixed: pointing the scanner at a single file scanned nothing and reported a clean result.

## Unreleased

## 0.2.2 - 2026-07-29

- Fixed `--version`: it printed 0.2.0 on a 0.2.1 install because the version string was
  duplicated in `__init__.py`. The package version is now read from installed metadata and a
  test fails if it ever drifts from pyproject.toml.
- Added README translations (Русский, 简体中文, Español, Português) with a language switcher
  and a badge row.

## 0.2.1 - 2026-07-29

- Added SARIF output (`--sarif`) for GitHub code scanning integrations.
- Added a GitHub Action `sarif` input and README upload example.
- Added `--version` to the CLI.
- Fixed the README demo image so it renders on PyPI: the relative path is now an absolute
  raw.githubusercontent.com URL.
- Added `[project.urls]` so the PyPI page links to the repository, issues and changelog.
  The 0.2.0 page has no links because metadata is only refreshed by a new release.
- Added a release workflow that publishes to PyPI with Trusted Publishing (OIDC), builds
  once, verifies that the tag matches the project version, and creates the GitHub release.

## 0.2.0 - 2026-07-28

- Renamed the project from skillscan to skillfrisk; the CLI command is now `skillfrisk`.
- First release on PyPI.
- Regression corpus expanded from 3 to 10 anthropics/skills skills (92 files); fixed the false positives this exposed in OBFUSCATION, PY_DYNAMIC_EXEC, and SECRET_ACCESS.
- Added a reproducible benchmark harness (`benchmarks/run.py`) with pinned versions of cisco-ai-skill-scanner and SkillSpector, plus recorded results.

## 0.1.0 - Unreleased

- Initial scanner for SKILL.md files and MCP manifests.
- Terminal, JSON, and HTML reports.
- CI with Ruff and Pytest.
