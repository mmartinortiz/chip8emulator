from chip8emulator.memory import Memory
from chip8emulator.processor import Processor


def chip8loop():
    memory = Memory(size=4096)
    processor = Processor(memory=memory)
    processor.reset()

    while True:
        # Emulate one cycle
        processor.cycle()

        # If the draw flag is set, update the screen

        # Store key press state (Press and Release)


if __name__ == "__main__":
    chip8loop()
