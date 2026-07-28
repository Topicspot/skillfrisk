#!/usr/bin/env bash
# Single quality gate: the SAME list runs in pre-commit and in CI.
# Requires: uv (installs project tools), npx (markdownlint), gitleaks, lychee, docker (optional locally).
set -uo pipefail

FAILED=0
step() {
  local name="$1"
  shift
  echo "==> $name"
  if "$@"; then echo "OK"; else echo "FAILED: $name"; FAILED=1; fi
}

step "ruff format --check" uv run ruff format --check .
step "ruff check" uv run ruff check .
step "mypy --strict" uv run mypy
step "pytest" uv run python -m pytest
step "vulture" uv run vulture
step "gitleaks" gitleaks detect --source . --redact
export_req() { uv export --no-emit-project --extra dev -o /tmp/skillscan-req.txt -q; }
pip_audit() { export_req && uv run pip-audit --no-deps -r /tmp/skillscan-req.txt; }
step "pip-audit" pip_audit
step "markdownlint" npx -y markdownlint-cli2 "**/*.md"
step "lychee" lychee --no-progress --include-fragments README.md
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  step "docker build" docker build -t skillscan:ci .
  step "docker run demo" docker run --rm -v "$PWD/tests/fixtures/mcp_server:/scan" skillscan:ci scan /scan --json --no-fail-on-high
else
  echo "==> docker: SKIPPED (no docker daemon here; enforced in CI)"
fi

exit $FAILED
