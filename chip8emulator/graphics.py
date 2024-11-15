from bitarray import bitarray
from bitarray.util import ba2int, int2ba


class Graphics:
    def __init__(self, width: int = 64, height: int = 32) -> None:
        """
        Graphic interface for the Chip-8 emulator. Width and Height are provided for
        testing purposes, since the original Chip-8 had a screen size of 64x32 pixels.

        Args:
            width (int, optional): Screen width, in bits. Defaults to 64.
            height (int, optional): Screen height, in bits. Defaults to 32.
        """
        self.width = width
        self.height = height
        self.clear()

    def clear(self) -> None:
        """
        Clear the screen by setting all pixels to 0.
        """
        self.pixels = bitarray(self.width * self.height)

    def get(self, x: int, y: int) -> int:
        """
        Get the pixel value at the specified coordinates. The origin (0, 0)
        is at the top-left corner.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            int: Value of the pixel at the specified coordinates.
        """
        return self.pixels[x + (self.width * y)]

    def get_byte(self, x: int, y: int) -> int:
        """
        Get the pixel byte at the specified coordinates. The origin (0, 0)
        is at the top-left corner.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            int: Value of the pixel byte at the specified coordinates.
        """
        return ba2int(self.pixels[x + (self.width * y) : x + (self.width * y) + 8])

    def set(self, x: int, y: int, value: int) -> None:
        """
        Set the pixel value at the specified coordinates. The origin (0, 0)
        is at the top-left corner.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            value (int): Value to set the pixel-byte to.
        """
        self.pixels[x + (self.width * y)] = value

    def set_byte(self, x: int, y: int, value: int) -> None:
        """
        Set the pixel byte at the specified coordinates. The origin (0, 0)
        is at the top-left corner.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            value (int): Value to set the pixel-byte to.
        """
        self.pixels[x + (self.width * y) : x + (self.width * y) + 8] = int2ba(
            value, length=8
        )

    def as_list_of_integers(self) -> list[int]:
        """
        Convert the pixel values to a list of integers.
        """
        return [ba2int(self.pixels[i : i + 8]) for i in range(0, len(self.pixels), 8)]

    def __repr__(self) -> str:
        """
        Print the graphic's pixels as a string of 'X' and '.' to represent the 1s and 0s.
        """
        rows = []
        for row in range(0, self.height * self.width, self.width):
            rows.append(
                self.pixels[row : row + self.width]
                .to01()
                .replace("1", "X")
                .replace("0", ".")
            )

        return "\n".join(rows)
