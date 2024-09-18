class NoKeyAvailable(Exception):
    pass


class Keypad:
    def __init__(self) -> None:
        self.keys = [
            0x0,
            0x1,
            0x2,
            0x3,
            0x4,
            0x5,
            0x6,
            0x7,
            0x8,
            0x9,
            0xA,
            0xB,
            0xC,
            0xD,
            0xE,
            0xF,
        ]
        self.pressed_keys = []

    def press_key(self, key: int):
        if isinstance(key, int) and key in self.keys:
            self.pressed_keys.append(key)
        else:
            if isinstance(key, int):
                raise ValueError(f"Invalid key: {hex(key)}")
            else:
                raise ValueError(f"Invalid key: {key}")

    def get_pressed_key(self) -> int:
        if self.is_key_available():
            return self.pressed_keys.pop(0)
        else:
            raise NoKeyAvailable

    def is_key_available(self) -> bool:
        return len(self.pressed_keys) > 0
