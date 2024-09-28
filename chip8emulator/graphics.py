class Graphics:
    def __init__(self, width: int = 64, height: int = 32) -> None:
        self.width = width
        self.height = height

        self.pixels = [[0] * width for _ in range(height)]

    def clear(self) -> None:
        """
        Clear the screen by setting all pixels to 0.
        """
        self.pixels = [[0] * self.width for _ in range(self.height)]

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
        return self.pixels[y][x]

    def set(self, x: int, y: int, value: int) -> None:
        """
        Set the pixel value at the specified coordinates. The origin (0, 0)
        is at the top-left corner.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            value (int): Value to set the pixel to.
        """
        self.pixels[y][x] = value

    def __repr__(self) -> str:
        return "\n".join(
            "".join("X" if pixel == 1 else "." for pixel in row) for row in self.pixels
        )
