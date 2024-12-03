#!/bin/bash
uv sync --link-mode=copy
/workspaces/chip8emulator/.venv/bin/pre-commit install --install-hooks
/workspaces/chip8emulator/.venv/bin/pre-commit autoupdate
