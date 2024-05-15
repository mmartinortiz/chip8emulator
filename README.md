# CHIP-8 Emulator

An emulator for the CHIP-8 Chip written in Python. A small project for learning and understanding emulators.

## Development

This project uses [devbox](https://www.jetify.com/devbox) to provide all the libraries you need for development. Check the file [devbox.json](./devbox.json) for an updated list, basically, they are:

- [Python 3.12](https://www.python.org/downloads/release/python-312/)
- [Poetry](https://python-poetry.org/)
- [Pre-commit](https://pre-commit.com/)

Run the following install script as a non-root user to install the latest version of Devbox:

```bash
curl -fsSL https://get.jetify.com/devbox | bash
```

Initialize the development environment with

```bash
devbox shell
```

This will install do multiple things for you:

1. Create an environment for development isolated from your system
2. Install Python 3.12
3. Install Poetry
4. Install pre-commit
5. Install pre-commit hooks
6. Install all the project's Python dependencies with Poetry

Later, you only need to activate the virtual environment created by poetry for having local access to Python 3.12 and the project dependencies.

If you use VS Code, there are a bunch of recommended extensions that you can install if you want.

```bash
# Format code
ruff format .

# Sort imports
ruff check --select I --fix

# Testing
pytest
```

## References

- [How to write an emulator (CHIP-8 interpreter)](https://multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/)
- [CHIP 8 description](https://en.wikipedia.org/wiki/CHIP-8#Virtual_machine_description)
