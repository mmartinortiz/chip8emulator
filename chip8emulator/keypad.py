class Keypad:
    def __init__(self) -> None:
        self.keys = "0123456789ABCDEF"
        self.pressed_key = None

    def press_key(self, key: str):
        if isinstance(key, str) and key in self.keys:
            self.pressed_key = key
        else:
            raise ValueError(f"Invalid key: {key}")

    def get_pressed_key(self) -> str:
        return self.pressed_key

    def wait_for_key(self):
        # TODO: Implement this method
        pass
