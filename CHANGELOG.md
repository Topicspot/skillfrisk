# Changelog

## Unreleased

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
