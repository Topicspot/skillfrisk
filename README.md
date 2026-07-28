# skillscan

[![CI](https://github.com/Topicspot/skillscan/actions/workflows/ci.yml/badge.svg)](https://github.com/Topicspot/skillscan/actions/workflows/ci.yml)

`skillscan` is a static security scanner for AI-agent skills and MCP servers.

![skillscan demo](assets/demo.svg)

## Problem

AI agents increasingly install third-party skills, MCP servers, hooks, and scripts that can read files, call the network, and influence tool use. A malicious or careless skill can hide prompt injection, steal secrets, or run destructive shell commands before a developer notices.

## Why it matters

Generic SAST tools are useful, but they do not understand agent-specific risk: hidden instructions in Markdown, `SKILL.md` frontmatter, MCP tool permissions, or prompt-injection language embedded in docs. `skillscan` is a pre-install and CI gate for that niche.

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
uv run skillscan scan tests/fixtures/malicious_skill --json
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
pipx install git+https://github.com/Topicspot/skillscan.git
skillscan scan path/to/skill-or-mcp --html reports/skillscan.html
```

For local development:

```bash
git clone https://github.com/Topicspot/skillscan.git
cd skillscan && uv sync --extra dev
uv run skillscan scan tests/fixtures/malicious_skill --json
```

Install as an agent skill (teaches your agent to vet skills/MCP servers before installing them):

```bash
npx skills add Topicspot/skillscan
```

Use in CI as a GitHub Action:

```yaml
- uses: Topicspot/skillscan@main
  with:
    path: "."
```

Or with Docker:

```bash
docker build -t skillscan .
docker run --rm -v "$PWD:/scan" skillscan scan /scan --json
```

The command exits with code `2` when high or critical findings are present.

## Examples

Scan a safe skill:

```bash
uv run skillscan scan tests/fixtures/benign_skill
```

Scan an MCP manifest:

```bash
uv run skillscan scan tests/fixtures/mcp_server --json
```

Write an HTML report:

```bash
uv run skillscan scan . --html reports/report.html --no-fail-on-high
```

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

`tests/corpus/` vendors three popular real-world skills from
[anthropics/skills](https://github.com/anthropics/skills); the test suite fails if skillscan
reports a single high-severity finding on any of them.

## Limitations

- Static analysis can miss runtime-only behavior.
- Regex rules trade precision for speed and explainability; some findings may require human review.
- JavaScript/TypeScript AST checks are not implemented yet.
- SARIF output and PyPI publication are planned but not included in this first version.

## Roadmap

- SARIF reporter for GitHub code scanning.
- Dedicated JavaScript/TypeScript AST rules.
- Rule configuration file with allowlisted paths.
- Signed rule bundles and reproducible release workflow.

---

## ☕ Support the author

This project is free and MIT-licensed. If it saved you time, you can send a coffee — it directly funds the next feature.

**USDT — Tron network (TRC-20) only:**
TS9ywGeSyKQxiCszdKCHLR8DRAsnYCosNN
> ⚠️ Send **USDT on the Tron (TRC-20) network only**. Tokens sent on Ethereum, BSC or any other network will be lost forever.
> No account, no fees, no strings attached. A ⭐ star helps just as much.


**Other languages / Другие языки**

- **Українська:** Проєкт безкоштовний. Якщо він заощадив вам час — USDT лише в мережі TRC-20 на адресу вище; зірка ⭐ допомагає так само.
- **Русский:** Проект бесплатный. Если он сэкономил вам время — USDT только в сети TRC-20 на адрес выше; звезда ⭐ помогает так же.
- **Español:** El proyecto es gratuito. Si te ahorró tiempo — USDT solo por la red TRC-20 a la dirección de arriba; una estrella ⭐ ayuda igual.
- **Deutsch:** Das Projekt ist kostenlos. Wenn es dir Zeit gespart hat — USDT nur über das TRC-20-Netzwerk an die obige Adresse; ein Stern ⭐ hilft genauso.
- **Français:** Le projet est gratuit. S'il vous a fait gagner du temps — USDT uniquement via le réseau TRC-20 à l'adresse ci-dessus ; une étoile ⭐ aide tout autant.
- **Português:** O projeto é gratuito. Se ele economizou seu tempo — USDT apenas pela rede TRC-20 para o endereço acima; uma estrela ⭐ ajuda da mesma forma.
- **Türkçe:** Proje ücretsizdir. Size zaman kazandırdıysa — USDT yalnızca TRC-20 ağı üzerinden yukarıdaki adrese; bir yıldız ⭐ da aynı derecede yardımcı olur.
- **中文:** 本项目完全免费。如果它为你节省了时间——请仅通过 TRC-20 网络将 USDT 发送到上面的地址；点个 ⭐ 星同样有帮助。
- **日本語:** このプロジェクトは無料です。時間の節約になったなら、上記アドレスへ TRC-20 ネットワークのみで USDT を送ってください。⭐ スターも同じくらい助けになります。
- **हिन्दी:** यह प्रोजेक्ट मुफ़्त है। अगर इसने आपका समय बचाया — ऊपर दिए पते पर केवल TRC-20 नेटवर्क से USDT भेजें; एक ⭐ स्टार भी उतनी ही मदद करता है।
- **Bahasa Indonesia:** Proyek ini gratis. Jika menghemat waktu Anda — kirim USDT hanya melalui jaringan TRC-20 ke alamat di atas; bintang ⭐ juga sama membantunya.
