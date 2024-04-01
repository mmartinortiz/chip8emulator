from pathlib import Path

from chip8emulator.graphics import Graphics
from chip8emulator.keypad import Keypad
from chip8emulator.memory import Memory


class Processor:
    def __init__(self, memory: Memory, graphics: Graphics, keypad: Keypad) -> None:
        self.memory = memory
        self.graphics = graphics
        self.keypad = keypad

        # Registers
        self.v0 = 0
        self.v1 = 0
        self.v2 = 0
        self.v3 = 0
        self.v4 = 0
        self.v5 = 0
        self.v6 = 0
        self.v7 = 0
        self.v8 = 0
        self.v9 = 0
        self.vA = 0
        self.vB = 0
        self.vC = 0
        self.vD = 0
        self.vE = 0

        # Also known as vF
        self.carry_flag = 0

        # Program counter
        self.program_counter = 0x200

        # Index registry
        self.index_registry = 0

        # Timers
        self.sound_timer = 0
        self.delay_timer = 0

        # Stack
        self.stack = [0] * 16
        self.stack_pointer = 0

    def load_program(self, program: Path) -> None:
        if not program.exists():
            raise FileNotFoundError(f"Program file {program} not found")
        with program.open("rb") as f:
            pointer = 0x000
            while chunk := f.read(1):
                self.memory[pointer] = chunk
                pointer += 1

    def fetch_opcode(self) -> int:
        opcode = (
            self.memory[self.program_counter] << 8
            | self.memory[self.program_counter + 1]
        )
        return opcode

    def cycle(self) -> None:
        # Fetch opcode
        opcode = self.fetch_opcode()
        # Decode opcode
        # Execute opcode
        # Update timers
        self.execute_opcode(opcode)
