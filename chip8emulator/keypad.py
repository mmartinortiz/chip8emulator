from chip8emulator.types import Nibble


class Keypad:
    def __init__(self) -> None:
        self.keys = "0123456789ABCDEF"
        self.pressed_key = None

    def press_key(self, key: str | Nibble):
        if isinstance(key, str) and key in self.keys:
            self.pressed_key = key
        elif isinstance(key, Nibble):
            self.pressed_key = self.keys[key.to_int()]
        else:
            raise ValueError(f"Invalid key: {key}")

    def get_pressed_key(self) -> str:
        return self.pressed_key

    def get_pressed_key_as_nibble(self) -> Nibble:
        return Nibble(self.keys.index(self.pressed_key))
