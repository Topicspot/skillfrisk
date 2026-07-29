# skillfrisk

[English](../README.md) · **Русский** · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Português](README.pt-BR.md)

[![PyPI](https://img.shields.io/pypi/v/skillfrisk?style=flat-square&label=pypi&color=3775A9)](https://pypi.org/project/skillfrisk/)
[![Python](https://img.shields.io/pypi/pyversions/skillfrisk?style=flat-square&color=4B8BBE)](https://pypi.org/project/skillfrisk/)
[![CI](https://github.com/Topicspot/skillfrisk/actions/workflows/ci.yml/badge.svg)](https://github.com/Topicspot/skillfrisk/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](https://github.com/Topicspot/skillfrisk/blob/main/LICENSE)

`skillfrisk` — статический сканер безопасности для скиллов ИИ-агентов и MCP-серверов.

## Зачем

Агенты ставят сторонние скиллы, MCP-серверы, хуки и скрипты, которые читают файлы, ходят в сеть
и влияют на выбор инструментов. Вредоносный или просто небрежный скилл может спрятать
prompt-инъекцию, утащить секреты или выполнить разрушительную команду раньше, чем это заметят.
Обычные SAST-инструменты этого не видят: они не понимают ни скрытых инструкций в Markdown, ни
фронтматтера `SKILL.md`, ни прав MCP-инструментов.

## Установка

```bash
pipx install skillfrisk   # или: uv tool install skillfrisk / pip install skillfrisk
skillfrisk scan path/to/skill-or-mcp
```

Разовый запуск без установки:

```bash
uvx skillfrisk scan path/to/skill-or-mcp
```

В CI как GitHub Action:

```yaml
- uses: Topicspot/skillfrisk@main
  with:
    path: "."
```

Код возврата `2`, если найдены проблемы уровня high или critical.

## Что находит

- prompt-инъекции в Markdown и конфигурациях;
- `curl`/`wget`, направленные в shell;
- чтение `.env`, `~/.ssh`, `os.environ` и подобных хранилищ секретов;
- разрушительные команды вида `rm -rf $HOME`;
- скрытые невидимые и двунаправленные Unicode-символы;
- `eval`/`exec` и `subprocess(..., shell=True)`;
- wildcard-права и опасные инструменты в MCP-манифестах.

## Ложные срабатывания

В `tests/corpus/` лежат 10 реальных скиллов (92 файла) из репозитория
[anthropics/skills](https://github.com/anthropics/skills). Тесты падают, если сканер выдаст на
них хотя бы одно срабатывание уровня high. Текущее состояние: 0 срабатываний, около 45 мс на
скилл.

## Ограничения

Статический анализ не видит поведения во время выполнения, правила на регулярных выражениях
меняют точность на скорость, AST-проверок для JavaScript и TypeScript пока нет.

Полная документация, сравнение с альтернативами и планы — в
[английском README](../README.md).

