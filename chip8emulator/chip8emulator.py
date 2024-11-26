import argparse
import sys
from pathlib import Path

import arcade
from arcade.gl import geometry
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


class Chip8Emulator(arcade.Window):
    def __init__(self, rom: Path, width: int = 640, height: int = 320, ips: int = 700):
        super().__init__(width, height, title="Chip-8 Emulator")
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
        self.fps = 60

        # Instructions per second
        self.ips = ips

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

        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform mat4 projection;

            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 v_uv;

            void main() {
                gl_Position = projection * vec4(in_vert, 0.0, 1.0);
                v_uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330

            // Unsigned integer sampler for reading uint data from texture
            uniform usampler2D screen;

            in vec2 v_uv;
            out vec4 out_color;

            void main() {
                // Calculate the bit position on the x axis
                uint bit_pos = uint(round((v_uv.x * 64) - 0.5)) % 8u;
                // Create bit mask we can AND the fragment with to extract the pixel value
                uint flag = uint(pow(2u, 7u - bit_pos));
                // Read the fragment value (We reverse the y axis here as well)
                uint frag = texture(screen, v_uv * vec2(1.0, -1.0)).r;
                // Write the pixel value. Values above 1 will be clamped to 1.
                out_color = vec4(vec3(frag & flag), 1.0);
            }
            """,
        )
        # 8 x 4
        self.program["projection"] = self.projection
        self.program["screen"] = 0
        border = 0  # border to test scale
        self.quad = geometry.screen_rectangle(
            border, border, width - border * 2, height - border * 2
        )
        self.texture = self.ctx.texture((8, 32), components=1, dtype="i1")

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
        if self.processor.redraw:
            self.clear()
            self.texture.write(self.graphics.as_bitarray())

            self.texture.use(0)
            self.quad.render(self.program)
            self.processor.redraw = False

    def on_key_press(self, key, modifiers):
        if key in self.keymap:
            self.keypad.press_key(self.keymap[key])
        else:
            logger.debug(f"Key {key} not mapped")

    def on_key_release(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.exit()

        if key in self.keymap:
            self.keypad.release_key(self.keymap[key])
        else:
            logger.debug(f"Key {key} not mapped")

    def on_update(self, delta_time):
        self.processor.emulate(7)
        # self.processor.emulate(self.ips // self.fps)


def main():
    chip8 = Chip8Emulator(rom=rom_path)
    chip8.setup()

    arcade.run()


if __name__ == "__main__":
    main()
