from functools import reduce

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
        self.pixels = [bitarray("0" * self.width) for _ in range(self.height)]

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
        if x >= self.width or y >= self.height:
            raise IndexError(
                f"Pixel out of bounds: ({x}, {y}). Screen size: {self.width}x{self.height}"
            )

        return self.pixels[y][x]

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
        if x >= self.width or y >= self.height:
            raise IndexError(
                f"Pixel out of bounds: ({x}, {y}). Screen size: {self.width}x{self.height}"
            )

        length = 8
        end = x + length

        if end > self.width:
            end = self.width
            length = end - x

        screen_line = self.pixels[y][x:end]
        if len(screen_line) == 8:
            return ba2int(screen_line, signed=False)
        else:
            rest = self.pixels[y][0 : 8 - len(screen_line)]
            return ba2int(screen_line + rest, signed=False)

    def set(self, x: int, y: int, value: int) -> None:
        """
        Set the pixel value at the specified coordinates. The origin (0, 0)
        is at the top-left corner.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            value (int): Value to set the pixel-byte to.
        """
        if x >= self.width or y >= self.height:
            raise IndexError(
                f"Pixel out of bounds: ({x}, {y}). Screen size: {self.width}x{self.height}"
            )

        if value not in (0, 1):
            raise ValueError("Pixel value must be 0 or 1")

        self.pixels[y][x] = value

    def set_byte(self, x: int, y: int, value: int) -> None:
        """
        Set the pixel byte at the specified coordinates. The origin (0, 0)
        is at the top-left corner.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            value (int): Value to set the pixel-byte to.
        """
        if x >= self.width or y >= self.height:
            raise IndexError(
                f"Pixel out of bounds: ({x}, {y}). Screen size: {self.width}x{self.height}"
            )

        if value < 0 or value > 255:
            raise ValueError("Pixel value must be between 0 and 255 (0xFF)")

        length = 8
        end = x + length

        # The length is always specified as 8 to ensure that leading 0s are kept.
        if end > self.width:
            # If the sprite is bigger than the screen, it is wrapped around.
            draw_to = self.width - x
            self.pixels[y][x : self.width] = int2ba(value, length=8)[:draw_to]
            wrapped = end - self.width
            self.pixels[y][0 : end - self.width] = int2ba(value, length=8)[-wrapped:]
        else:
            self.pixels[y][x:end] = int2ba(value, length=8)[:length]

    def as_list_of_integers(self) -> list[int]:
        """
        Convert the pixel values to a list of integers.
        """
        return [ba2int(self.pixels[i : i + 8]) for i in range(0, len(self.pixels), 8)]

    def as_bitarray(self) -> bitarray:
        """
        Convert the pixel values to a bitarray.
        """
        return reduce(lambda x, y: x + y, self.pixels)

    def __repr__(self) -> str:
        """
        Print the graphic's pixels as a string of 'X' and '.' to represent the 1s and 0s.
        """
        rows = []
        for row in self.pixels:
            rows.append(row.to01().replace("1", "X").replace("0", "."))

        return "\n".join(rows)
