class Graphics:
    def __init__(self, width: int = 64, height: int = 32) -> None:
        self.width = width
        self.height = height

        self.pixels = [0] * width * height
