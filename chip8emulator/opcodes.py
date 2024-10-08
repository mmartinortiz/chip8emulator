from enum import StrEnum, auto


class OPCODE(StrEnum):
    x0NNN = auto()
    x00E0 = auto()
    x00EE = auto()
    x1NNN = auto()
    x2NNN = auto()
    x3XNN = auto()
    x4XNN = auto()
    x5XY0 = auto()
    x6XNN = auto()
    x7XNN = auto()
    x8XY0 = auto()
    x8XY1 = auto()
    x8XY2 = auto()
    x8XY3 = auto()
    x8XY4 = auto()
    x8XY5 = auto()
    x8XY6 = auto()
    x8XY7 = auto()
    x8XYE = auto()
    x9XY0 = auto()
    xANNN = auto()
    xBNNN = auto()
    xCXNN = auto()
    xDXYN = auto()
    xEX9E = auto()
    xEXA1 = auto()
    xFX07 = auto()
    xFX0A = auto()
    xFX15 = auto()
    xFX18 = auto()
    xFX1E = auto()
    xFX29 = auto()
    xFX33 = auto()
    xFX55 = auto()
    xFX65 = auto()

    def __repr__(self) -> str:
        return f"0x{self.name[1:].upper()}"


def get_high_byte(value) -> int:
    return (value & 0xFF00) >> 8


def get_low_byte(value) -> int:
    return value & 0x00FF


def get_first_nibble(value) -> int:
    return (value & 0xF000) >> 12


def get_second_nibble(value) -> int:
    return (value & 0x0F00) >> 8


def get_third_nibble(value) -> int:
    return (value & 0x00F0) >> 4


def get_fourth_nibble(value) -> int:
    return value & 0x000F
