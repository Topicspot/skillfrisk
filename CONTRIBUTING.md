# Contributing

Thanks for improving `skillscan`.

1. Keep the scanner offline-first: no telemetry, no network calls during scans.
2. Add a fixture and a meaningful test for every rule change.
3. Prefer precise rules with clear recommendations over noisy generic regexes.
4. Run `uv run ruff check .` and `uv run pytest` before opening a PR.
