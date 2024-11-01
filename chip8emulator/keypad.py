from loguru import logger


class Keypad:
    def __init__(self) -> None:
        # Keymap, indicating if a key is currently being pressed
        self.keys = {
            0x0: False,
            0x1: False,
            0x2: False,
            0x3: False,
            0x4: False,
            0x5: False,
            0x6: False,
            0x7: False,
            0x8: False,
            0x9: False,
            0xA: False,
            0xB: False,
            0xC: False,
            0xD: False,
            0xE: False,
            0xF: False,
        }
        # Last pressed-released key
        self.accumulator = -1

    def is_key_available(self) -> bool:
        """Indicates if there is a key available to be read"""
        return self.accumulator > 0

    def is_key_pressed(self, key: int) -> bool:
        """Indicates if a key is currently being pressed"""
        return self.keys[key]

    def get_pressed_key(self) -> int:
        """Returns the last pressed key"""
        if self.is_key_available():
            key = self.accumulator
            self.accumulator = -1
            return key
        else:
            return -1

    def press_key(self, key: int):
        """Set a key as currently be pressed"""
        if key in self.keys:
            self.keys[key] = True
        else:
            logger.debug(f"Invalid key pressed: {key}")

    def release_key(self, key: int):
        """Set a key as currently be released. This will make the key be available to
        be read"""
        if key in self.keys:
            self.keys[key] = False
            # On the original COSMAC VIP, the key was only registered when it was
            # pressed and then released.
            # self.accumulator.append(key)
            self.accumulator = key
            logger.debug(self.accumulator)
        else:
            logger.debug(f"Invalid key released: {key}")
