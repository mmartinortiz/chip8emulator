from pathlib import Path

from chip8emulator.graphics import Graphics
from chip8emulator.keypad import Keypad
from chip8emulator.memory import Memory


class Processor:
    def __init__(self, memory: Memory, graphics: Graphics, keypad: Keypad) -> None:
        self.memory = memory
        self.graphics = graphics
        self.keypad = keypad

        self.reset()

    def reset(self) -> None:
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

    def opcode_ANNN(self, opcode: int) -> None:
        """
        Sets the value of the index registry to the address specified in the opcode.

        Parameters:
        - opcode (int): The opcode containing the address to be set.
        """
        address = opcode & 0x0FFF
        self.index_registry = address
        self.program_counter += 2

    def opcode_00E0(self) -> None:
        """Clear screen"""
        # TODO: Clear screen
        ...

    def opcode_000E(self) -> None:
        # Restore the program counter
        self.program_counter = self.stack[self.stack_pointer]

        # Decrease the stack pointer
        self.stack_pointer -= 1

        # Move to next instruction
        self.program_counter += 2

    def opcode_1NNN(self, opcode: int) -> None:
        """
        Jumps to address NNN

        This is an unconditional transfer of control to another part of the program.
        The processor continues execution from the specified address NNN. The current
        address is not saved, so there's no intention to return back to the point from
        where the jump was made.
        """

        # Jump to address NNN
        address = opcode & 0x0FFF
        self.program_counter = address

    def opcode_2NNN(self, opcode: int):
        """
        Call a subroutine at address NNN: This is a transfer of control to a subroutine
        (a separate block of code that performs a specific task). The processor saves
        the address of the instruction following the "call" instruction (usually on a
        stack), and then continues execution from the specified address NNN. When the
        subroutine finishes (usually with a "return" instruction), the processor
        retrieves the saved address from the stack and continues execution from that
        point, allowing the program to "return" from the subroutine.
        """
        # Store the program_counter in the stack
        self.stack[self.stack_pointer] = self.program_counter

        # Increase the stack pointer
        self.stack_pointer += 1

        # Call the subroutine at NNN
        address = opcode & 0x0FFF
        self.program_counter = address

    def cycle(self) -> None:
        # Fetch opcode
        opcode = self.fetch_opcode()

        # Decode opcode
        match opcode & 0xF000:
            case 0x0000:
                match opcode & 0x000F:
                    case 0x0000:
                        # Clear the screen
                        self.opcode_00E0()
                    case 0x000E:
                        # Returns from a subroutine
                        self.opcode_000E()

            case 0x1000:
                # Jump to address NNN
                self.opcode_1NNN(opcode)
            case 0x2000:
                # Call to subroutine at NNN
                self.opcode_2NNN(opcode)
            case 0xA000:
                self.opcode_ANNN(opcode)
                # Sets I to the address NNN
        # Execute opcode
        # Update timers
        self.execute_opcode(opcode)

        self.update_timers()

    def update_timers(self) -> None:
        """
        Updates the delay and sound timers.
        """
        # Timers
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            if self.sound_timer == 1:
                print("BEEP")
            self.sound_timer -= 1
