import argparse
import sys
from pathlib import Path

import arcade
from arcade import SpriteList, SpriteSolidColor
from loguru import logger

from chip8emulator.graphics import Graphics
from chip8emulator.keypad import Keypad
from chip8emulator.memory import Memory
from chip8emulator.processor import Processor

parser = argparse.ArgumentParser()
parser.add_argument("rom_path", nargs="?", default="roms/IBM Logo.ch8")
parser.add_argument(
    "--debug",
    action="store_true",
    help="Set loguru level to debug",
)
args = parser.parse_args()

rom_path = Path(args.rom_path)

logger.remove()
logger.add(sys.stderr, level="DEBUG" if args.debug else "INFO")


class Chip8Emulator(arcade.View):
    def __init__(self, rom: Path, height: int = 320, width: int = 640):
        super().__init__()
        self.memory = Memory()
        self.graphics = Graphics()
        self.keypad = Keypad()
        self.processor = Processor(
            memory=self.memory,
            graphics=self.graphics,
            keypad=self.keypad,
        )
        self.processor.reset()
        self.rom = rom
        self.height = height
        self.width = width

        self.keymap = {
            arcade.key.KEY_1: 0x1,
            arcade.key.KEY_2: 0x2,
            arcade.key.KEY_3: 0x3,
            arcade.key.KEY_4: 0xC,
            arcade.key.Q: 0x4,
            arcade.key.W: 0x5,
            arcade.key.E: 0x6,
            arcade.key.R: 0xD,
            arcade.key.A: 0x7,
            arcade.key.S: 0x8,
            arcade.key.D: 0x9,
            arcade.key.F: 0xE,
            arcade.key.Z: 0xA,
            arcade.key.X: 0x0,
            arcade.key.C: 0xB,
            arcade.key.V: 0xF,
        }

        # Chip8 has only one color
        self.sprites = SpriteList()
        for x in range(self.graphics.width):
            for y in range(self.graphics.height):
                sprite = SpriteSolidColor(10, 10, arcade.color.WHITE)
                sprite.center_x = x * 10
                sprite.center_y = y * 10
                self.sprites.append(sprite)

    def flip_and_scale_y_axis(self, y: int) -> int:
        """For Chip-8, the origin is at the top-left corner, but for arcade, it is at
        the bottom-left corner. This function flips the y-axis and scales it to the
        arcade window size.
        """
        return (self.height // 10) - (y // 10) - 1

    def scale_x_axis(self, x: int) -> int:
        """Scale the x-axis to the arcade window size."""
        return x // 10

    def setup(self):
        # Load the ROM into memory
        self.processor.load_program(self.rom)
        logger.debug(f"ROM {self.rom} loaded into memory")

    def on_draw(self):
        self.clear()
        for sprite in self.sprites:
            y = self.flip_and_scale_y_axis(sprite.center_y)
            x = self.scale_x_axis(sprite.center_x)
            pixel = self.graphics.get(x, y)
            sprite.color = arcade.color.WHITE if pixel == 1 else arcade.color.BLACK

        self.sprites.draw()

    def on_key_press(self, key, modifiers):
        if key in self.keymap:
            self.keypad.press_key(self.keymap[key])
        else:
            logger.debug(f"Key {key} not mapped")

    def on_key_release(self, key, modifiers):
        if key in self.keymap:
            self.keypad.release_key(self.keymap[key])
        else:
            logger.debug(f"Key {key} not mapped")

        if key == arcade.key.ESCAPE:
            arcade.exit()

    def on_update(self, delta_time):
        # Emulate one cycle
        self.processor.cycle()


def main():
    window = arcade.Window(width=640, height=320, title="Chip-8 Emulator")
    chip8 = Chip8Emulator(rom=rom_path)
    chip8.setup()

    window.show_view(chip8)
    arcade.run()


if __name__ == "__main__":
    main()
