#!/bin/bash
echo "
format = \"\$git_branch \$git_status\\n> \"
" > ~/.config/starship.toml
echo "
starship init fish | source
" >> ~/.config/fish/config.fish
uv generate-shell-completion fish > ~/.config/fish/completions/uv.fish
uv sync --link-mode=copy
/workspaces/chip8emulator/.venv/bin/pre-commit install --install-hooks
/workspaces/chip8emulator/.venv/bin/pre-commit autoupdate
