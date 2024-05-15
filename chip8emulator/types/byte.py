from functools import total_ordering

from chip8emulator.types import Nibble


@total_ordering
class Byte:
    """The Byte class helps to manage Bytes in the emulator.
    The Byte object always have 8 bits and does not handle over or
    underflow. It is up to the user to handle it externally.
    """

    def __init__(self, value: int):
        self.value = value

    def get_high_nibble(self) -> Nibble:
        return Nibble((self.value & 0xF0) >> 4)

    def get_low_nibble(self) -> Nibble:
        return Nibble(self.value & 0x0F)

    def __add__(self, other) -> "Byte":
        """
        Add two byte. Does not handle overflow

        Examples:
        >>> Byte(0x10) + Byte(0x20)
        "0x30"
        >>> Byte(0xFF) + Byte(20)
        "0x1F"
        """
        if not isinstance(other, (int, Byte)):
            return NotImplemented

        if isinstance(other, int):
            result = self.value + other
        elif isinstance(other, Byte):
            result = self.value + other.value

        return Byte(result & 0xFF)

    def __radd__(self, other) -> "Byte":
        return self.__add__(other)

    def __sub__(self, other: "Byte") -> "Byte":
        """Subtracts another Byte to the current Byte. Underflow
        is not handled

        Examples:
        >>> Byte(0x20) - Byte(0x10)
        "0x10"
        >>> Byte(0x30) - Byte(0x40)
        "0x10"
        """
        if not isinstance(other, (int, Byte)):
            return NotImplemented

        if isinstance(other, int):
            result = abs(self.value - other)
        elif isinstance(other, Byte):
            result = abs(self.value - other.value)

        return Byte(result & 0xFF)

    def __rsub__(self, other) -> "Byte":
        return self.__sub__(other)

    def __eq__(self, other: "Byte") -> bool:
        if isinstance(other, int):
            return self.value == other
        elif isinstance(other, Byte):
            return self.value == other.value

    def __lt__(self, other: "Byte") -> bool:
        if isinstance(other, int):
            return self.value < other
        elif isinstance(other, Byte):
            return self.value < other.value

    def __abs__(self) -> "Byte":
        return Byte(abs(self.value) & 0xFF)

    def __repr__(self) -> str:
        return hex(self.value)
