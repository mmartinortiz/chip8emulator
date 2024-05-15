from chip8emulator.types import Byte, Nibble


class Word:
    def __init__(self, value: int):
        self.value = value

    def get_high_byte(self) -> Byte:
        return Byte((self.value & 0xFF00) >> 8)

    def get_low_byte(self) -> Byte:
        return Byte(self.value & 0x00FF)

    def get_first_nibble(self) -> Nibble:
        return Nibble((self.value & 0xF000) >> 12)

    def get_second_nibble(self) -> Nibble:
        return Nibble((self.value & 0x0F00) >> 8)

    def get_third_nibble(self) -> Nibble:
        return Nibble((self.value & 0x00F0) >> 4)

    def get_fourth_nibble(self) -> Nibble:
        return Nibble(self.value & 0x000F)

    def __add__(self, other: "Word") -> "Word":
        if not isinstance(other, (int, Word)):
            return NotImplemented

        if isinstance(other, int):
            result = self.value + other
        elif isinstance(other, Word):
            result = self.value + other.value

        return Word(result & 0xFFFF)

    def __radd__(self, other) -> "Word":
        return self.__add__(other)

    def __sub__(self, other: "Word") -> "Word":
        if not isinstance(other, (int, Word)):
            return NotImplemented

        if isinstance(other, int):
            result = abs(self.value - other)
        elif isinstance(other, Word):
            result = abs(self.value - other.value)

        return Word(result & 0xFFFF)

    def __rsub__(self, other) -> "Word":
        return self.__sub__(other)

    def __and__(self, other) -> "Word":
        if not isinstance(other, (int, Word)):
            return NotImplemented

        if isinstance(other, int):
            result = self.value & other
        elif isinstance(other, Word):
            result = self.value & other.value

        return Word(result)

    def __eq__(self, other) -> bool:
        if not isinstance(other, (int, Word)):
            return NotImplemented

        if isinstance(other, int):
            return self.value == other
        elif isinstance(other, Word):
            return self.value == other.value

    def __lt__(self, other) -> bool:
        if not isinstance(other, (int, Word)):
            return NotImplemented

        if isinstance(other, int):
            return self.value < other
        elif isinstance(other, Word):
            return self.value < other.value

    def __repr__(self) -> str:
        return hex(self.value)
