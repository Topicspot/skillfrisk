# skillfrisk

[English](../README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · **Português**

[![PyPI](https://img.shields.io/pypi/v/skillfrisk?style=flat-square&label=pypi&color=3775A9)](https://pypi.org/project/skillfrisk/)
[![Python](https://img.shields.io/pypi/pyversions/skillfrisk?style=flat-square&color=4B8BBE)](https://pypi.org/project/skillfrisk/)
[![CI](https://github.com/Topicspot/skillfrisk/actions/workflows/ci.yml/badge.svg)](https://github.com/Topicspot/skillfrisk/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](https://github.com/Topicspot/skillfrisk/blob/main/LICENSE)

`skillfrisk` é um scanner de segurança estático para skills de agentes de IA e servidores MCP.

## Por que

Agentes instalam skills, servidores MCP, hooks e scripts de terceiros que leem arquivos, acessam
a rede e influenciam o uso de ferramentas. Um skill malicioso ou apenas descuidado pode esconder
injeção de prompt, roubar segredos ou rodar um comando destrutivo antes que alguém perceba.
Ferramentas SAST genéricas não enxergam isso: elas não entendem instruções escondidas em
Markdown, o frontmatter de `SKILL.md` nem as permissões das ferramentas MCP.

## Instalação

```bash
pipx install skillfrisk   # ou: uv tool install skillfrisk / pip install skillfrisk
skillfrisk scan path/to/skill-or-mcp
```

Execução avulsa, sem instalar:

```bash
uvx skillfrisk scan path/to/skill-or-mcp
```

Em CI como GitHub Action:

```yaml
- uses: Topicspot/skillfrisk@main
  with:
    path: "."
```

O comando sai com código `2` quando há achados de severidade high ou critical.

## O que ele encontra

- instruções de injeção de prompt em Markdown e arquivos de configuração;
- `curl`/`wget` redirecionados para um shell;
- leituras de `.env`, `~/.ssh`, `os.environ` e fontes de segredos parecidas;
- comandos destrutivos como `rm -rf $HOME`;
- caracteres Unicode invisíveis e controles bidirecionais escondidos;
- `eval`/`exec` e `subprocess(..., shell=True)`;
- permissões com curinga e ferramentas perigosas em manifestos MCP.

## Controle de falsos positivos

`tests/corpus/` traz 10 skills reais (92 arquivos) do repositório
[anthropics/skills](https://github.com/anthropics/skills). A suíte de testes falha se o scanner
relatar um único achado de severidade high sobre eles. Situação atual: 0 achados, cerca de 45 ms
por skill.

## Limites

Análise estática não vê comportamento em tempo de execução, regras por expressão regular trocam
precisão por velocidade, e checagens de AST para JavaScript e TypeScript ainda não existem.

Documentação completa, comparação com alternativas e roadmap estão no
[README em inglês](../README.md).

