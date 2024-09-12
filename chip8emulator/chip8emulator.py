import arcade

from chip8emulator.memory import Memory
from chip8emulator.processor import Processor


class Chip8Emulator(arcade.Window):
    def __init__(self):
        super().__init__(640, 320, "Chip-8 Emulator")
        self.memory = Memory(size=4096)
        self.processor = Processor(memory=self.memory)
        self.processor.reset()

    def setup(self):
        # Set up the game
        pass

    def on_draw(self):
        # Draw the screen
        pass

    def on_key_press(self, key, modifiers):
        # Press the key
        pass

    def on_key_release(self, key, modifiers):
        # Release the key
        pass

    def update(self, delta_time):
        # Emulate one cycle
        self.processor.cycle()

        # If the draw flag is set, update the screen

        # Store key press state (Press and Release)


def main():
    window = Chip8Emulator()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
