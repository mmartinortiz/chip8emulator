FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

RUN <<EOF
    apt update
    apt install --yes \
        libdbus-1-3 \
        libegl1 \
        libgl-dev \
        libpulse0 \
        libxkbcommon0 \
        libxkbcommon-dev \
        qt6-wayland
    rm -rf /var/lib/apt/lists/*
EOF
