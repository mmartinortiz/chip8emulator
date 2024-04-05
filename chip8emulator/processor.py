from collections import UserDict
from pathlib import Path
from typing import List

from chip8emulator.graphics import Graphics
from chip8emulator.keypad import Keypad
from chip8emulator.memory import Memory


class Registry(UserDict):
    def __init__(self, values: List[int] = None):
        if not values:
            values = [0] * 15

        self.data = {k: v for k, v in enumerate(values)}
        super().__init__(self.data)

    def __transform_key(self, key):
        """
        Transforms the given key into its corresponding value. The key can be a
        an integer between 0 and 15, or a string starting with "V" followed by a
        number indicating the registry, or a string with an uppercase letter
        between A and F.


        Args:
            key (str): The key to be transformed.

        Returns:
            int: The transformed value of the key.

        Raises:
            ValueError: If the key is not a valid registry.

        """
        if isinstance(key, int):
            return key

        if key.lower().startswith("v"):
            key = key[1]

        if key.isdigit():
            key = int(key)
        elif key.upper() in "ABCDEF":
            if key.upper() == "A":
                key = 10
            elif key.upper() == "B":
                key = 11
            elif key.upper() == "C":
                key = 12
            elif key.upper() == "D":
                key = 13
            elif key.upper() == "E":
                key = 14
            else:
                raise ValueError(f"Unexpected registry {key}")

        return key

    def __getitem__(self, key):
        key = self.__transform_key(key)
        return self.data[key]

    def __setitem__(self, key, value):
        key = self.__transform_key(key)
        self.data[key] = value


class Processor:
    def __init__(self, memory: Memory, graphics: Graphics, keypad: Keypad) -> None:
        self.memory = memory
        self.graphics = graphics
        self.keypad = keypad

        self.registry = Registry()
        self.reset()

    def reset(self) -> None:
        # Registers
        self.registries = Registry([0] * 15)

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

    def opcode_3NNN(self, opcode: int) -> None:
        """
        Skips the next instruction if VX equals NN (usually the next instruction is
        a jump to skip a code block)
        """
        registry = (opcode & 0x0F00) >> 8

        if registry not in self.registry.keys():
            raise ValueError(f"Unexpected value {registry}")

        value = opcode & 0x00FF

        if self.registry[registry] == value:
            self.program_counter += 4

    def opcode_4NNN(self, opcode: int) -> None:
        """
        Skips the next instruction if VX does not equal NN (usually the next instruction
        is a jump to skip a code block)
        """
        registry = (opcode & 0x0F00) >> 8

        if registry not in self.registry.keys():
            raise ValueError(f"Unexpected value {registry}")

        value = opcode & 0x00FF

        if self.registry[registry] != value:
            self.program_counter += 4

    def opcode_5XY0(self, opcode: int) -> None:
        """
        Skips the next instruction if VX equals VY (usually the next instruction is a
        jump to skip a code block)."""
        registry_x = (opcode & 0x0F00) >> 8
        registry_y = (opcode & 0x00F0) >> 4

        if (
            registry_x not in self.registry.keys()
            or registry_y not in self.registry.keys()
        ):
            raise ValueError(f"Unexpected value {registry_x} or {registry_y}")

        if self.registry[registry_x] == self.registry[registry_y]:
            self.program_counter += 4

    def opcode_6XNN(self, opcode: int) -> None:
        """Sets VX to NN"""
        registry = (opcode & 0x0F00) >> 8
        value = opcode & 0x00FF

        self.registry[registry] = value

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
            case 0x3000:
                self.opcode_3NNN(opcode)
            case 0x4000:
                self.opcode_4NNN(opcode)
            case 0x5000:
                self.opcode_5XY0(opcode)
            case 0x6000:
                self.opcode_6XNN(opcode)
            case 0xA000:
                self.opcode_ANNN(opcode)
                # Sets I to the address NNN

            # (0x3E44 & 0x0F00) >> 8
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
