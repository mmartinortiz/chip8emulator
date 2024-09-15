import pytest

from chip8emulator.decoder import decode
from chip8emulator.opcodes import OPCODE


@pytest.mark.parametrize(
    "opcode, expected",
    [
        (0x1000, OPCODE.x1NNN),
        (0x2000, OPCODE.x2NNN),
        (0x3000, OPCODE.x3XNN),
        (0x4000, OPCODE.x4XNN),
        (0x5000, OPCODE.x5XY0),
        (0x6000, OPCODE.x6XNN),
        (0x7000, OPCODE.x7XNN),
        (0x8000, OPCODE.x8XY0),
        (0x8001, OPCODE.x8XY1),
        (0x8002, OPCODE.x8XY2),
        (0x8003, OPCODE.x8XY3),
        (0x8004, OPCODE.x8XY4),
        (0x8005, OPCODE.x8XY5),
        (0x8006, OPCODE.x8XY6),
        (0x8007, OPCODE.x8XY7),
        (0x800E, OPCODE.x8XYE),
        (0x9000, OPCODE.x9XY0),
        (0xA000, OPCODE.xANNN),
        (0xB000, OPCODE.xBNNN),
        (0xC000, OPCODE.xCXNN),
        (0xD000, OPCODE.xDXYN),
        (0xE09E, OPCODE.xEX9E),
        (0xE0A1, OPCODE.xEXA1),
        (0xF007, OPCODE.xFX07),
        (0xF00A, OPCODE.xFX0A),
        (0xF015, OPCODE.xFX15),
        (0xF018, OPCODE.xFX18),
        (0xF01E, OPCODE.xFX1E),
        (0xF029, OPCODE.xFX29),
        (0xF033, OPCODE.xFX33),
        (0xF055, OPCODE.xFX55),
        (0xF065, OPCODE.xFX65),
        (0x00E0, OPCODE.x00E0),
        (0x00EE, OPCODE.x00EE),
    ],
)
def test_decode(opcode, expected):
    assert decode(opcode) == expected
