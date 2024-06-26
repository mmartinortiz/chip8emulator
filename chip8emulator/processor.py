from collections import UserDict
from pathlib import Path
import random
from typing import List

from chip8emulator.graphics import Graphics
from chip8emulator.keypad import Keypad
from chip8emulator.memory import Memory
from chip8emulator.types import Byte, Nibble, Word


class Registry(UserDict):
    def __init__(self, values: List[Byte] = None):
        if not values:
            values = [Byte(0)] * 15

        self.data = {k: v for k, v in enumerate(values)}
        self.draw_flag = False
        super().__init__(self.data)

    def __transform_key(self, key: str | int | Nibble) -> int:
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

        if isinstance(key, Nibble):
            return key.value

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

    def __contains__(self, key: str | int | Nibble) -> bool:
        key = self.__transform_key(key)
        return key in self.data

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
        self.registry = Registry([Byte(0)] * 15)

        # Also known as vF
        self.carry_flag = Byte(0)

        # Program counter
        self.program_counter = Word(0x200)

        # Index registry
        self.index_registry = Word(0)

        # Timers
        self.sound_timer = 0
        self.delay_timer = 0

        # Stack
        self.stack = [Word(0)] * 16
        self.stack_pointer = Word(0)

    def load_program(self, program: Path) -> None:
        if not program.exists():
            raise FileNotFoundError(f"Program file {program} not found")
        with program.open("rb") as f:
            pointer = 0x000
            while chunk := f.read(1):
                self.memory[pointer] = chunk
                pointer += 1

    def fetch_opcode(self) -> Word:
        opcode = (
            self.memory[self.program_counter] << 8
            | self.memory[self.program_counter + 1]
        )
        return opcode

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

    def opcode_1NNN(self, opcode: Word) -> None:
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

    def opcode_2NNN(self, opcode: Word):
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

    def opcode_3NNN(self, opcode: Word) -> None:
        """
        Skips the next instruction if VX equals NN (usually the next instruction is
        a jump to skip a code block)
        """
        if isinstance(opcode, int):
            opcode = Word(opcode)
        registry = opcode.get_second_nibble()

        if registry not in self.registry.keys():
            raise ValueError(f"Unexpected value {registry}")

        value = opcode.get_low_byte()

        if self.registry[registry] == value:
            self.program_counter += 4

    def opcode_4NNN(self, opcode: Word) -> None:
        """
        Skips the next instruction if VX does not equal NN (usually the next instruction
        is a jump to skip a code block)
        """
        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry = opcode.get_second_nibble()

        if registry not in self.registry.keys():
            raise ValueError(f"Unexpected value {registry}")

        value = opcode.get_low_byte()

        if self.registry[registry] != value:
            self.program_counter += 4

    def opcode_5XY0(self, opcode: Word) -> None:
        """
        Skips the next instruction if VX equals VY (usually the next instruction is a
        jump to skip a code block).
        """
        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()
        registry_y = opcode.get_third_nibble()

        if (
            registry_x not in self.registry.keys()
            or registry_y not in self.registry.keys()
        ):
            raise ValueError(f"Unexpected value {registry_x} or {registry_y}")

        if self.registry[registry_x] == self.registry[registry_y]:
            self.program_counter += 4

    def opcode_6XNN(self, opcode: Word) -> None:
        """Sets VX to NN"""
        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry = opcode.get_second_nibble()
        value = opcode.get_low_byte()

        self.registry[registry] = value
        self.program_counter += 2

    def opcode_7XNN(self, opcode: Word) -> None:
        """Adds NN to VX (carry flag is not changed)"""
        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry = opcode.get_second_nibble()
        value = opcode.get_low_byte()

        self.registry[registry] += value
        self.program_counter += 2

    def opcode_8XY0(self, opcode: Word) -> None:
        """Sets VX to the value of VY"""
        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()
        registry_y = opcode.get_third_nibble()

        self.registry[registry_x] = self.registry[registry_y]
        self.program_counter += 2

    def opcode_8XY1(self, opcode: Word) -> None:
        """Sets VX to VX OR VY"""
        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()
        registry_y = opcode.get_third_nibble()

        self.registry[registry_x] |= self.registry[registry_y]
        self.program_counter += 2

    def opcode_8XY2(self, opcode: Word) -> None:
        """Sets VX to VX AND VY"""
        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()
        registry_y = opcode.get_third_nibble()

        self.registry[registry_x] &= self.registry[registry_y]
        self.program_counter += 2

    def opcode_8XY3(self, opcode: Word) -> None:
        """Sets VX to VX XOR VY"""
        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()
        registry_y = opcode.get_third_nibble()

        self.registry[registry_x] ^= self.registry[registry_y]
        self.program_counter += 2

    def opcode_8XY4(self, opcode: Word) -> None:
        """Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't"""
        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()
        registry_y = opcode.get_third_nibble()

        self.registry[registry_x] += self.registry[registry_y]

        if self.registry[registry_x] > 255:
            self.registry[registry_x] &= 0x0FF
            self.carry_flag = 0b1
        else:
            self.carry_flag = 0b0

        self.program_counter += 2

    def opcode_8XY5(self, opcode: Word) -> None:
        """VY is subtracted from VX. VF is set to 0 when there's an underflow, and 1
        when there is not. (i.e. VF set to 1 if VX >= VY and 0 if not)."""
        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()
        registry_y = opcode.get_third_nibble()

        if self.registry[registry_x] >= self.registry[registry_y]:
            self.carry_flag = 0b1
        else:
            self.carry_flag = 0b0

        self.registry[registry_x] = abs(
            self.registry[registry_x] - self.registry[registry_y]
        )

        self.program_counter += 2

    def opcode_8XY6(self, opcode: Word) -> None:
        """Stores the least significant bit of VX in VF and
        then shifts VX to the right by 1"""

        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()

        # Store the least significant bit of VX in VF
        self.carry_flag = self.registry[registry_x] & 0b1

        # Shift VX to the right by 1
        self.registry[registry_x] >>= 1

        self.program_counter += 2

    def opcode_8XY7(self, opcode: Word) -> None:
        """Sets VX to VY minus VX. VF is set to 0 when there's an underflow,
        and 1 when there is not. (i.e. VF set to 1 if VY >= VX)"""

        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()
        registry_y = opcode.get_third_nibble()

        if self.registry[registry_y] >= self.registry[registry_x]:
            self.carry_flag = 0b1
        else:
            self.carry_flag = 0b0

        self.registry[registry_x] = abs(
            self.registry[registry_y] - self.registry[registry_x]
        )

        self.program_counter += 2

    def opcode_8XYE(self, opcode: Word) -> None:
        """Stores the most significant bit of VX in VF and then
        shifts VX to the left by 1"""

        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()

        # Store the most significant bit of VX in VF
        self.carry_flag = (
            Byte(1) if (self.registry[registry_x] & 0b10000000) > 0 else Byte(0)
        )

        # Shift VX to the left by 1
        self.registry[registry_x] = Byte(self.registry[registry_x] << 1)

        self.program_counter += 2

    def opcode_9XY0(self, opcode: Word) -> None:
        """Skips the next instruction if VX does not equal VY. (Usually the next
        instruction is a jump to skip a code block)"""

        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()
        registry_y = opcode.get_third_nibble()

        if self.registry[registry_x] != self.registry[registry_y]:
            self.program_counter += 4
        else:
            self.program_counter += 2

    def opcode_ANNN(self, opcode: Word) -> None:
        """
        Sets the value of the index registry to the address specified in the opcode.

        Parameters:
        - opcode (int): The opcode containing the address to be set.
        """
        address = opcode & 0x0FFF
        self.index_registry = address
        self.program_counter += 2

    def opcode_BNNN(self, opcode: Word) -> None:
        """Jumps to the address NNN plus V0"""

        address = opcode & 0x0FFF
        self.program_counter = address + self.registry[0]

    def opcode_CXNN(self, opcode: Word) -> None:
        """Sets VX to the result of a bitwise and operation on a random number
        (Typically: 0 to 255) and NN"""

        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry = opcode.get_second_nibble()
        value = opcode.get_low_byte()

        random_value = Byte(random.randint(0, 255))

        self.registry[registry] = random_value & value

    def opcode_DXYN(self, opcode: Word) -> None:
        """
        Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height
        of N pixels. Each row of 8 pixels is read as bit-coded starting from memory
        location I; I value doesn’t change after the execution of this instruction.
        As described above, VF is set to 1 if any screen pixels are flipped from set
        to unset when the sprite is drawn, and to 0 if that doesn’t happen.
        """

        if not isinstance(opcode, Word):
            opcode = Word(opcode)

        registry_x = opcode.get_second_nibble()
        registry_y = opcode.get_third_nibble()
        height = opcode.get_fourth_nibble()

        x = self.registry[registry_x]
        y = self.registry[registry_y]

        self.carry_flag = 0

        for y_line in range(0, height.value):
            pixel = self.memory[self.index_registry + y_line]

            for x_line in range(0, 8):
                # Check if the bit of the pixel to be drawn is set to 1
                if (pixel & (0x80 >> x_line)) != 0:
                    if self.graphics.get(x + x_line, y + y_line) == 1:
                        self.carry_flag = 1
                    self.graphics.set(x + x_line, y + y_line, 1)

        self.program_counter += 2
        self.draw_flag = True

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
            case 0x7000:
                self.opcode_7XNN(opcode)
            case 0x8000:
                match opcode & 0x000F:
                    case 0x0000:
                        self.opcode_8XY0(opcode)
                    case 0x0001:
                        self.opcode_8XY1(opcode)
                    case 0x0002:
                        self.opcode_8XY2(opcode)
                    case 0x0003:
                        self.opcode_8XY3(opcode)
                    case 0x0004:
                        self.opcode_8XY4(opcode)
                    case 0x005:
                        self.opcode_8XY5(opcode)
                    case 0x0006:
                        self.opcode_8XY6(opcode)
                    case 0x0007:
                        self.opcode_8XY7(opcode)
                    case 0x000E:
                        self.opcode_8XYE(opcode)
            case 0x900:
                self.opcode_9XY0(opcode)
            case 0xA000:
                self.opcode_ANNN(opcode)
            case 0xB000:
                self.opcode_BNNN(opcode)
            case 0xC000:
                self.opcode_CXNN(opcode)

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
