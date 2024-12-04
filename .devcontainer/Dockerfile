FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

RUN <<EOF
    apt update
    apt install --yes libxkbcommon-dev libgl-dev libegl1 libdbus-1-3 qt6-wayland
    rm -rf /var/lib/apt/lists/*
EOF
