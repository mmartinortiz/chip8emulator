FROM mcr.microsoft.com/devcontainers/base:ubuntu

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
