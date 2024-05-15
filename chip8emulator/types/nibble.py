class Nibble:
    def __init__(self, value: int):
        """
        Class to represent a nibble (4 bits) in the Chip-8 system.
        Bits above 4 are ignored.

        Args:
            value (int): The value to be stored in the Nibble object.

        Examples:
        >>> Nibble(0x1)
        "0x1"
        >>> Nibble(0xA)
        "0xA"
        >>> Nibble(0xF)
        "0xF"
        >>> Nibble(0x10)
        "0x0"
        """
        self.value = value & 0xF

    def __str__(self):
        return f"{self.value:01X}"

    def __add__(self, other) -> "Nibble":
        if not isinstance(other, (int, Nibble)):
            return NotImplemented

        if isinstance(other, int):
            return Nibble(self.value + other)
        elif isinstance(other, Nibble):
            return Nibble(self.value + other.value)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other) -> "Nibble":
        if not isinstance(other, (int, Nibble)):
            return NotImplemented

        if isinstance(other, int):
            return Nibble(abs(self.value - other))
        elif isinstance(other, Nibble):
            return Nibble(abs(self.value - other.value))

    def __rsub__(self, other):
        return self.__sub__(other)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (int, Nibble)):
            return NotImplemented

        if isinstance(other, int):
            return self.value == other
        elif isinstance(other, Nibble):
            return self.value == other.value
