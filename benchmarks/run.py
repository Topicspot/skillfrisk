"""Reproduce the false-positive comparison from the README.

Runs skillfrisk, cisco-ai-skill-scanner and skillspector (static mode) on the
regression corpus in tests/corpus and prints a Markdown table.

Usage (from the repository root, requires uv and network for the first run):

    uv run python benchmarks/run.py

Tool versions are pinned below; results in benchmarks/results-2026-07-28.md
were produced with exactly these versions.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "tests" / "corpus"
ENVS = REPO / "benchmarks" / ".envs"

CISCO_SPEC = "cisco-ai-skill-scanner==2.0.12"
NVIDIA_SPEC = "skillspector @ git+https://github.com/NVIDIA/SkillSpector@34f60308522f45447cd343da0aad77bcea308ad4"  # v2.5.0, not on PyPI
HIGH = {"HIGH", "CRITICAL"}


def make_env(name: str, spec: str) -> Path:
    env = ENVS / name
    if not (env / "bin").exists():
        subprocess.run(["uv", "venv", str(env)], check=True, capture_output=True)
        subprocess.run(
            ["uv", "pip", "install", "--python", str(env / "bin" / "python"), spec],
            check=True,
            capture_output=True,
        )
    return env


def corpus_dirs() -> list[Path]:
    return sorted(d for d in CORPUS.iterdir() if d.is_dir())


PerSkill = dict[str, tuple[int, int]]


def run_skillfrisk() -> tuple[PerSkill, float]:
    sys.path.insert(0, str(REPO / "src"))
    from skillfrisk.scanner import scan_path

    per: PerSkill = {}
    start = time.monotonic()
    for d in corpus_dirs():
        result = scan_path(d)
        highs = sum(1 for f in result.findings if f.severity.upper() in HIGH)
        per[d.name] = (len(result.findings), highs)
    elapsed = time.monotonic() - start
    return per, elapsed


def run_cisco(env: Path) -> tuple[PerSkill, float]:
    per: PerSkill = {}
    elapsed = 0.0
    for d in corpus_dirs():
        out = ENVS / f"cisco_{d.name}.json"
        start = time.monotonic()
        subprocess.run(
            [
                str(env / "bin" / "skill-scanner"),
                "scan",
                "--format",
                "json",
                "--output",
                str(out),
                str(d),
            ],
            capture_output=True,
        )
        elapsed += time.monotonic() - start
        data = json.loads(out.read_text())
        highs = sum(1 for f in data["findings"] if str(f.get("severity", "")).upper() in HIGH)
        per[d.name] = (int(data["findings_count"]), highs)
    return per, elapsed


def run_nvidia(env: Path) -> tuple[PerSkill, float]:
    per: PerSkill = {}
    elapsed = 0.0
    for d in corpus_dirs():
        out = ENVS / f"nvidia_{d.name}.json"
        start = time.monotonic()
        subprocess.run(
            [
                str(env / "bin" / "skillspector"),
                "scan",
                str(d),
                "--no-llm",
                "--format",
                "json",
                "--output",
                str(out),
            ],
            capture_output=True,
        )
        elapsed += time.monotonic() - start
        data = json.loads(out.read_text())
        issues = data["issues"]
        highs = sum(1 for i in issues if str(i.get("severity", "")).upper() in HIGH)
        per[d.name] = (len(issues), highs)
    return per, elapsed


def main() -> None:
    ENVS.mkdir(parents=True, exist_ok=True)
    n = len(corpus_dirs())
    print(f"Corpus: {n} skills from anthropics/skills (see tests/corpus/NOTICE.md)\n")
    rows = [("skillfrisk (this repo)", *run_skillfrisk())]
    rows.append((CISCO_SPEC, *run_cisco(make_env("cisco", CISCO_SPEC))))
    rows.append(("skillspector 2.5.0 (--no-llm)", *run_nvidia(make_env("nvidia", NVIDIA_SPEC))))
    print("| Scanner | Findings | High/Critical | Seconds per skill |")
    print("|---|---|---|---|")
    for name, per, elapsed in rows:
        total = sum(f for f, _ in per.values())
        high = sum(h for _, h in per.values())
        print(f"| {name} | {total} | {high} | {elapsed / n:.2f} |")
    print("\nPer-skill findings, shown as total (high/critical):\n")
    names = [name for name, _, _ in rows]
    print("| Skill | " + " | ".join(names) + " |")
    print("|---" * (len(names) + 1) + "|")
    for skill in sorted(rows[0][1]):
        cells = [f"{per[skill][0]} ({per[skill][1]})" for _, per, _ in rows]
        print(f"| {skill} | " + " | ".join(cells) + " |")
    print(
        "\nNote: snyk/agent-scan is excluded because it scans agent configurations"
        " installed on the machine via a cloud service, not a repository directory."
    )


if __name__ == "__main__":
    main()
