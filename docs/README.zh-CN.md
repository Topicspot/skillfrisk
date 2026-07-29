# skillfrisk

[English](../README.md) · [Русский](README.ru.md) · **简体中文** · [Español](README.es.md) · [Português](README.pt-BR.md)

[![PyPI](https://img.shields.io/pypi/v/skillfrisk?style=flat-square&label=pypi&color=3775A9)](https://pypi.org/project/skillfrisk/)
[![Python](https://img.shields.io/pypi/pyversions/skillfrisk?style=flat-square&color=4B8BBE)](https://pypi.org/project/skillfrisk/)
[![CI](https://github.com/Topicspot/skillfrisk/actions/workflows/ci.yml/badge.svg)](https://github.com/Topicspot/skillfrisk/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](https://github.com/Topicspot/skillfrisk/blob/main/LICENSE)

`skillfrisk` 是面向 AI 智能体技能（skills）与 MCP 服务器的静态安全扫描器。

![skillfrisk 扫描一个恶意技能和一个干净技能](https://raw.githubusercontent.com/Topicspot/skillfrisk/main/assets/demo.gif)

## 背景

智能体会安装第三方技能、MCP 服务器、钩子和脚本，它们可以读取文件、访问网络并影响工具调用。
恶意或粗心的技能可能藏有提示注入、窃取密钥，或在开发者察觉之前执行破坏性命令。通用 SAST
工具看不到这些：它们不理解 Markdown 中的隐藏指令、`SKILL.md` 的 frontmatter，也不理解 MCP
工具权限。

## 安装

```bash
pipx install skillfrisk   # 或：uv tool install skillfrisk / pip install skillfrisk
skillfrisk scan path/to/skill-or-mcp
```

免安装运行：

```bash
uvx skillfrisk scan path/to/skill-or-mcp
```

在 CI 中作为 GitHub Action 使用：

```yaml
- uses: Topicspot/skillfrisk@main
  with:
    path: "."
```

出现 high 或 critical 级别问题时退出码为 `2`。

## 检测内容

- Markdown 与配置文件中的提示注入指令；
- 将 `curl`/`wget` 直接管道传给 shell；
- 读取 `.env`、`~/.ssh`、`os.environ` 等密钥来源；
- `rm -rf $HOME` 一类的破坏性命令；
- 隐藏的不可见字符与双向 Unicode 控制符；
- `eval`/`exec` 以及 `subprocess(..., shell=True)`；
- MCP 清单中的通配符权限与危险工具。

## 误报控制

`tests/corpus/` 收录了来自 [anthropics/skills](https://github.com/anthropics/skills) 的 10 个
真实技能（92 个文件）。只要扫描器在其中报出一个 high 级别问题，测试就会失败。当前结果：0 个
误报，每个技能约 45 毫秒。

## 局限

静态分析无法覆盖运行时行为；正则规则以精确度换取速度；JavaScript 与 TypeScript 的 AST 检查
尚未实现。

完整文档、与同类工具的对比和路线图见[英文 README](../README.md)。

