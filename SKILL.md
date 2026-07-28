---
name: skillfrisk
description: Security-scan any AI-agent skill or MCP server before installing or publishing it. Use when the user asks to check, audit, or vet a skill/MCP server, or before adding third-party skills from GitHub. Detects prompt injection, secret exfiltration, remote code execution, destructive commands, and dangerous MCP permissions.
---

# skillfrisk — vet skills and MCP servers before trusting them

Third-party skills and MCP servers are executable instructions for your agent.
Scan them before installing. skillfrisk statically checks SKILL.md files, bundled
scripts, and MCP manifests for high-risk patterns.

## Run a scan

No installation needed (requires `uv`):

```bash
uvx --from "git+https://github.com/Topicspot/skillfrisk" skillfrisk scan path/to/skill-or-mcp
```

Machine-readable output for your own decision-making:

```bash
uvx --from "git+https://github.com/Topicspot/skillfrisk" skillfrisk scan path/to/skill --json
```

Exit code `2` means high/critical findings — do NOT install the scanned skill
without showing the findings to the user first.

## Typical workflow

1. User asks to install a third-party skill or MCP server (e.g. from GitHub).
2. Clone or download it to a temp directory first — do not install yet.
3. Run skillfrisk on that directory.
4. Exit 0 → proceed. Exit 2 → stop, show the findings table to the user, and
   let them decide.

## What it detects

- Prompt-injection instructions hidden in skill docs and HTML comments
- Access to credentials, key files, and environment secrets, plus exfiltration to remote hosts
- Remote code execution: piping downloads into a shell, dynamic code evaluation, unsafe subprocess use
- Destructive filesystem commands and fork bombs
- Over-broad MCP manifests (wildcard permissions, dangerous tool combinations)

False positives are controlled by a regression corpus of popular real-world
skills (see `tests/corpus/`).

## CI usage

```yaml
- uses: Topicspot/skillfrisk@main
  with:
    path: "."
```
