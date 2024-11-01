#!/bin/bash
poetry install --with dev
/workspaces/chip8emulator/.venv/bin/pre-commit install --install-hooks
/workspaces/chip8emulator/.venv/bin/pre-commit autoupdate
