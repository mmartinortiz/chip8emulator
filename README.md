# CHIP-8 Emulator

An emulator for the CHIP-8 Chip written in Python. A small project for learning and understanding emulators.

![The IBM logo](assets/ibm.png)

## Development

The project uses [devcontainers](https://containers.dev) to generate a development environment. However, if you do not want to use it, you can always use `poetry` directly.

## Running the emulator

You can run the emulator without installing the package:

```bash
poetry run python -m chip8_emulator <path_to_rom>
```

## References

- [How to write an emulator (CHIP-8 interpreter)](https://multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/)
- [Guide to making a CHIP-8 emulator](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/)
- [CHIP 8 description](https://en.wikipedia.org/wiki/CHIP-8#Virtual_machine_description)
- [CHIP-8 Test suite](https://github.com/Timendus/chip8-test-suite)
- [Awesome CHIP-8](https://github.com/tobiasvl/awesome-chip-8)
- [CHIP-8 Games](https://johnearnest.github.io/chip8Archive/)
