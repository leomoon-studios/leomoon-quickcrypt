# Contributing to LeoMoon QuickCrypt

Use Python 3.12 or newer and create dependencies only inside `.venv`:

```sh
python -m venv .venv
.venv/bin/python -m pip install "uv==0.13.5"
.venv/bin/uv sync --all-extras --locked
```

When changing files under `src/leomoon_quickcrypt/ui/`, regenerate the tracked Qt output before committing:

```sh
.venv/bin/python scripts/generate_qt.py
```

Before opening a change, run the maintained checks:

```sh
.venv/bin/uv run ruff check .
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME=none .venv/bin/python -m pytest -q
.venv/bin/uv run pip-audit
```

Use the **Release** GitHub Actions workflow for native platform-package tests. Manual runs do not publish a release. Pushing a `vMAJOR.MINOR.PATCH` tag is the only publishing trigger. It builds Windows x64 and ARM64 installers, Linux x86_64 and ARM64 AppImages, and the macOS ARM64 DMG after all checks pass.

Do not commit certificates, private keys, provisioning profiles, Apple passwords, tokens, package outputs, virtual environments, local signing keychains, or generated release metadata. Put protected signing credentials only in GitHub repository secrets.
