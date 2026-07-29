# skillfrisk

[English](../README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · **Español** · [Português](README.pt-BR.md)

[![PyPI](https://img.shields.io/pypi/v/skillfrisk?style=flat-square&label=pypi&color=3775A9)](https://pypi.org/project/skillfrisk/)
[![Python](https://img.shields.io/pypi/pyversions/skillfrisk?style=flat-square&color=4B8BBE)](https://pypi.org/project/skillfrisk/)
[![CI](https://github.com/Topicspot/skillfrisk/actions/workflows/ci.yml/badge.svg)](https://github.com/Topicspot/skillfrisk/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](https://github.com/Topicspot/skillfrisk/blob/main/LICENSE)

`skillfrisk` es un escáner de seguridad estático para skills de agentes de IA y servidores MCP.

## Por qué

Los agentes instalan skills, servidores MCP, hooks y scripts de terceros que leen archivos,
acceden a la red e influyen en qué herramientas se usan. Un skill malicioso o simplemente
descuidado puede esconder una inyección de prompt, robar secretos o ejecutar un comando
destructivo antes de que alguien lo note. Las herramientas SAST genéricas no lo ven: no
entienden instrucciones ocultas en Markdown, el frontmatter de `SKILL.md` ni los permisos de
las herramientas MCP.

## Instalación

```bash
pipx install skillfrisk   # o: uv tool install skillfrisk / pip install skillfrisk
skillfrisk scan path/to/skill-or-mcp
```

Ejecución puntual sin instalar:

```bash
uvx skillfrisk scan path/to/skill-or-mcp
```

En CI como GitHub Action:

```yaml
- uses: Topicspot/skillfrisk@main
  with:
    path: "."
```

El comando termina con código `2` cuando hay hallazgos de severidad high o critical.

## Qué detecta

- instrucciones de inyección de prompt en Markdown y configuraciones;
- `curl`/`wget` canalizados hacia un shell;
- lecturas de `.env`, `~/.ssh`, `os.environ` y almacenes de secretos similares;
- comandos destructivos como `rm -rf $HOME`;
- caracteres Unicode invisibles y controles bidireccionales ocultos;
- `eval`/`exec` y `subprocess(..., shell=True)`;
- permisos con comodín y herramientas peligrosas en manifiestos MCP.

## Control de falsos positivos

`tests/corpus/` incluye 10 skills reales (92 archivos) de
[anthropics/skills](https://github.com/anthropics/skills). La suite de tests falla si el
escáner reporta un solo hallazgo de severidad high sobre ellos. Estado actual: 0 hallazgos,
unos 45 ms por skill.

## Límites

El análisis estático no ve el comportamiento en tiempo de ejecución, las reglas por expresiones
regulares cambian precisión por velocidad, y todavía no hay comprobaciones AST para JavaScript
ni TypeScript.

La documentación completa, la comparación con alternativas y la hoja de ruta están en el
[README en inglés](../README.md).

