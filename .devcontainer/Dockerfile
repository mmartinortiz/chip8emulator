FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

RUN <<EOF
    apt update
    apt install --yes freeglut3
    rm -rf /var/lib/apt/lists/*
EOF
