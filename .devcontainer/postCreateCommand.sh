#!/bin/bash
uv generate-shell-completion fish | source
uv sync --link-mode=copy
/workspaces/chip8emulator/.venv/bin/pre-commit install --install-hooks
/workspaces/chip8emulator/.venv/bin/pre-commit autoupdate
