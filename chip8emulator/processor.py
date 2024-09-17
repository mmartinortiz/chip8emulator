import random
from pathlib import Path

from chip8emulator.decoder import decode
from chip8emulator.graphics import Graphics
from chip8emulator.keypad import Keypad
from chip8emulator.memory import Memory
from chip8emulator.opcodes import (
    OPCODE,
    get_fourth_nibble,
    get_low_byte,
    get_second_nibble,
    get_third_nibble,
)


class Processor:
    def __init__(self, memory: Memory, graphics: Graphics, keypad: Keypad) -> None:
        self.memory = memory
        self.graphics = graphics
        self.keypad = keypad

        self.reset()

    def reset(self) -> None:
        # Registers
        self.registry = {k: v for k, v in enumerate([0] * 15)}

        # Also known as vF
        self.carry_flag = 0x0

        # Program counter
        self.program_counter = 0x200

        # Index registry
        self.index_registry = 0x0

        # Timers
        self.sound_timer = 0x0
        self.delay_timer = 0x0

        # Stack
        self.stack = [0x0] * 16
        self.stack_pointer = 0x0

        self.load_font(font_file=Path(__file__).parent / Path("fonts.ch8"))

    def load_font(self, font_file: Path) -> None:
        if not font_file.exists():
            raise FileNotFoundError(f"Font file {font_file} not found")
        with font_file.open("rb") as f:
            pointer = 0x050
            while chunk := f.read(1):
                self.memory[pointer] = chunk
                pointer += 1

    def load_program(self, program: Path) -> None:
        if not program.exists():
            raise FileNotFoundError(f"Program file {program} not found")
        with program.open("rb") as f:
            pointer = 0x200
            while chunk := f.read(1):
                self.memory[pointer] = chunk
                pointer += 1

    def fetch_opcode(self) -> int:
        opcode = (
            self.memory[self.program_counter] << 8
            | self.memory[self.program_counter + 1]
        )
        return opcode

    def opcode_0NNN(self, opcode: int) -> None:
        pass

    def opcode_00E0(self) -> None:
        """Clear screen"""
        self.graphics.clear()

        self.program_counter += 2

    def opcode_00EE(self) -> None:
        """Return from a subroutine. Restore the program counter to the address
        pointed by the tip of the stack pointer and decrease the stack pointer."""
        # The stack pointer points to the next free position of the stack, so we need
        # to decrease it by 1 to get the address of the last subroutine call.
        self.program_counter = self.stack[self.stack_pointer - 1]

        # Decrease the stack pointer
        self.stack_pointer -= 1

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
        # Store the instruction next to the current one into the stack
        self.stack[self.stack_pointer] = self.program_counter + 2

        # Increase the stack pointer
        self.stack_pointer += 1

        # Call the subroutine at NNN
        address = opcode & 0x0FFF
        self.program_counter = address

    def opcode_3XNN(self, opcode: int) -> None:
        """
        Skips the next instruction if VX equals NN (usually the next instruction is
        a jump to skip a code block)
        """
        registry = get_second_nibble(opcode)

        if registry not in self.registry.keys():
            raise ValueError(f"Unexpected value {registry}")

        value = get_low_byte(opcode)

        if self.registry[registry] == value:
            self.program_counter += 4
            return

        self.program_counter += 2

    def opcode_4XNN(self, opcode: int) -> None:
        """
        Skips the next instruction if VX does not equal NN (usually the next instruction
        is a jump to skip a code block)
        """
        registry = get_second_nibble(opcode)

        if registry not in self.registry.keys():
            raise ValueError(f"Unexpected value {registry}")

        value = get_low_byte(opcode)

        if self.registry[registry] != value:
            self.program_counter += 4
            return

        self.program_counter += 2

    def opcode_5XY0(self, opcode: int) -> None:
        """
        Skips the next instruction if VX equals VY (usually the next instruction is a
        jump to skip a code block).
        """
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        if (
            registry_x not in self.registry.keys()
            or registry_y not in self.registry.keys()
        ):
            raise ValueError(f"Unexpected value {registry_x} or {registry_y}")

        if self.registry[registry_x] == self.registry[registry_y]:
            self.program_counter += 4
            return

        self.program_counter += 2

    def opcode_6XNN(self, opcode: int) -> None:
        """Sets VX to NN"""
        registry = get_second_nibble(opcode)
        value = get_low_byte(opcode)

        self.registry[registry] = value
        self.program_counter += 2

    def opcode_7XNN(self, opcode: int) -> None:
        """Adds NN to VX (carry flag is not changed)"""
        registry = get_second_nibble(opcode)
        value = get_low_byte(opcode)

        new_value = (self.registry[registry] + value) & 0xFF
        self.registry[registry] = new_value
        self.program_counter += 2

    def opcode_8XY0(self, opcode: int) -> None:
        """Sets VX to the value of VY"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        self.registry[registry_x] = self.registry[registry_y]
        self.program_counter += 2

    def opcode_8XY1(self, opcode: int) -> None:
        """Sets VX to VX OR VY"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        self.registry[registry_x] |= self.registry[registry_y]
        self.program_counter += 2

    def opcode_8XY2(self, opcode: int) -> None:
        """Sets VX to VX AND VY"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        self.registry[registry_x] &= self.registry[registry_y]
        self.program_counter += 2

    def opcode_8XY3(self, opcode: int) -> None:
        """Sets VX to VX XOR VY"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        self.registry[registry_x] ^= self.registry[registry_y]
        self.program_counter += 2

    def opcode_8XY4(self, opcode: int) -> None:
        """Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        self.registry[registry_x] += self.registry[registry_y]

        if self.registry[registry_x] > 255:
            self.registry[registry_x] &= 0x0FF
            self.carry_flag = 0b1
        else:
            self.carry_flag = 0b0

        self.program_counter += 2

    def opcode_8XY5(self, opcode: int) -> None:
        """VY is subtracted from VX. VF is set to 0 when there's an underflow, and 1
        when there is not. (i.e. VF set to 1 if VX >= VY and 0 if not)."""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        if self.registry[registry_x] >= self.registry[registry_y]:
            self.carry_flag = 0b1
        else:
            self.carry_flag = 0b0

        new_value = (self.registry[registry_x] - self.registry[registry_y]) & 0xFF

        self.registry[registry_x] = new_value

        self.program_counter += 2

    def opcode_8XY6(self, opcode: int) -> None:
        """Stores the least significant bit of VX in VF and
        then shifts VX to the right by 1"""
        registry_x = get_second_nibble(opcode)

        # Store the least significant bit of VX in VF
        self.carry_flag = self.registry[registry_x] & 0b1

        # Shift VX to the right by 1
        self.registry[registry_x] >>= 1

        self.program_counter += 2

    def opcode_8XY7(self, opcode: int) -> None:
        """Sets VX to VY minus VX. VF is set to 0 when there's an underflow,
        and 1 when there is not. (i.e. VF set to 1 if VY >= VX)"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        if self.registry[registry_y] >= self.registry[registry_x]:
            self.carry_flag = 0b1
        else:
            self.carry_flag = 0b0

        self.registry[registry_x] = abs(
            self.registry[registry_y] - self.registry[registry_x]
        )

        self.program_counter += 2

    def opcode_8XYE(self, opcode: int) -> None:
        """Stores the most significant bit of VX in VF and then
        shifts VX to the left by 1"""
        registry_x = get_second_nibble(opcode)

        # Store the most significant bit of VX in VF
        self.carry_flag = 0x1 if (self.registry[registry_x] & 0b10000000) > 0 else 0x0

        # Shift VX to the left by 1
        new_value = self.registry[registry_x] << 1
        self.registry[registry_x] = new_value & 0xFF

        self.program_counter += 2

    def opcode_9XY0(self, opcode: int) -> None:
        """Skips the next instruction if VX does not equal VY. (Usually the next
        instruction is a jump to skip a code block)"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        if self.registry[registry_x] != self.registry[registry_y]:
            self.program_counter += 4
        else:
            self.program_counter += 2

    def opcode_ANNN(self, opcode: int) -> None:
        """
        Sets the value of the index registry to the address specified in the opcode.

        Parameters:
        - opcode (int): The opcode containing the address to be set.
        """
        address = opcode & 0x0FFF
        self.index_registry = address
        self.program_counter += 2

    def opcode_BNNN(self, opcode: int) -> None:
        """Jumps to the address NNN plus V0"""

        address = opcode & 0x0FFF
        self.program_counter = (address + self.registry[0]) & 0xFFFF

    def opcode_CXNN(self, opcode: int) -> None:
        """Sets VX to the result of a bitwise 'and' operation on a random number
        (Typically: 0 to 255) and NN"""
        registry = get_second_nibble(opcode)
        value = get_low_byte(opcode)

        random_value = random.randint(0, 255)

        self.registry[registry] = random_value & value

    def opcode_DXYN(self, opcode: int) -> None:
        """
        Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height
        of N pixels. Each row of 8 pixels is read as bit-coded starting from memory
        location I; I value doesn't change after the execution of this instruction.
        As described above, VF is set to 1 if any screen pixels are flipped from set
        to unset when the sprite is drawn, and to 0 if that doesn't happen.
        """
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)
        height = get_fourth_nibble(opcode)

        x = self.registry[registry_x]
        y = self.registry[registry_y]

        self.carry_flag = 0

        for y_line in range(0, height):
            pixel = self.memory[self.index_registry + y_line]

            for x_line in range(0, 8):
                # Check if the bit of the pixel to be drawn is set to 1
                if (pixel & (0x80 >> x_line)) != 0:
                    if self.graphics.get(x + x_line, y + y_line) == 1:
                        self.carry_flag = 1
                    self.graphics.set(x + x_line, y + y_line, 1)

        self.program_counter += 2
        self.draw_flag = True

    def opcode_EX9E(self, opcode: int) -> None:
        """Skips the next instruction if the key stored in VX is pressed (usually the
        next instruction is a jump to skip a code block)."""
        registry_x = get_second_nibble(opcode)

        if self.registry[registry_x] == self.keypad.get_pressed_key():
            self.program_counter += 2

    def opcode_EXA1(self, opcode: int) -> None:
        """Skips the next instruction if the key stored in VX is not pressed (usually
        the next instruction is a jump to skip a code block)."""
        registry_x = get_second_nibble(opcode)

        if self.registry[registry_x] != self.keypad.get_pressed_key():
            self.program_counter += 2

    def opcode_FX07(self, opcode: int) -> None:
        """Sets VX to the value of the delay timer."""
        registry_x = get_second_nibble(opcode)

        self.registry[registry_x] = self.delay_timer
        self.program_counter += 2

    def opcode_FX0A(self, opcode: int) -> None:
        """A key press is awaited, and then stored in VX (blocking operation, all
        instruction halted until next key event)."""
        registry_x = get_second_nibble(opcode)

        key = self.keypad.get_pressed_key_as_nibble()

        if key is None:
            return

        self.registry[registry_x] = key
        self.program_counter += 2

    def opcode_FX15(self, opcode: int) -> None:
        """Sets the delay timer to VX"""
        registry_x = get_second_nibble(opcode)

        self.delay_timer = self.registry[registry_x]
        self.program_counter += 2

    def opcode_FX18(self, opcode: int) -> None:
        """Sets the sound timer to VX"""
        registry_x = get_second_nibble(opcode)

        self.sound_timer = self.registry[registry_x]
        self.program_counter += 2

    def opcode_FX1E(self, opcode: int) -> None:
        """Adds VX to I. VF is not affected."""
        registry_x = get_second_nibble(opcode)

        self.index_registry += self.registry[registry_x]
        self.program_counter += 2

    def opcode_FX29(self, opcode: int) -> None:
        """The index register I is set to the address of the hexadecimal character in
        VX."""
        registry_x = get_second_nibble(opcode)

        self.index_registry = self.registry[registry_x]
        self.program_counter += 2

    def opcode_FX33(self, opcode: int) -> None:
        """It takes the number in VX (which is one byte, so it can be any number
        from 0 to 255) and converts it to three decimal digits, storing these digits in
        memory at the address in the index register I.

        For example, if VX contains 156 (or 9C in hexadecimal), it would put the
        number 1 at the address in I, 5 in address I + 1, and 6 in address I + 2."""
        registry_x = get_second_nibble(opcode)

        value = self.registry[registry_x]

        self.memory[self.index_registry] = value // 100
        self.memory[self.index_registry + 1] = (value // 10) % 10
        self.memory[self.index_registry + 2] = value % 10

        self.program_counter += 2

    def opcode_FX55(self, opcode: int) -> None:
        """The value of each variable register from V0 to VX inclusive (if X is 0, then
        only V0) will be stored in successive memory addresses, starting with the one
        that's stored in I. V0 will be stored at the address in I, V1 will be stored
        in I + 1, and so on, until VX is stored in I + X.
        """
        registry_x = get_second_nibble(opcode)

        for i in range(registry_x + 1):
            self.memory[self.index_registry + i] = self.registry[i]

        self.program_counter += 2

    def opcode_FX65(self, opcode: int) -> None:
        """The values of each variable register from V0 to VX inclusive (if X is 0, then
        only V0) will be filled with values from memory addresses starting with the one
        that's stored in I. V0 will be filled with the value in the address in I, V1 will
        be filled with the value in I + 1, and so on, until VX is filled with the value
        in I + X.
        """
        registry_x = get_second_nibble(opcode)

        for i in range(registry_x + 1):
            self.registry[i] = self.memory[self.index_registry + i]

        self.program_counter += 2

    def cycle(self) -> None:
        # Fetch opcode
        opcode = self.fetch_opcode()

        # Decode & execute the opcode
        match decode(opcode):
            case OPCODE.x0NNN:
                self.opcode_0NNN(opcode)
            case OPCODE.x00E0:
                self.opcode_00E0()
            case OPCODE.x00EE:
                self.opcode_00EE()
            case OPCODE.x1NNN:
                self.opcode_1NNN(opcode)
            case OPCODE.x2NNN:
                self.opcode_2NNN(opcode)
            case OPCODE.x3XNN:
                self.opcode_3XNN(opcode)
            case OPCODE.x4XNN:
                self.opcode_4XNN(opcode)
            case OPCODE.x5XY0:
                self.opcode_5XY0(opcode)
            case OPCODE.x6XNN:
                self.opcode_6XNN(opcode)
            case OPCODE.x7XNN:
                self.opcode_7XNN(opcode)
            case OPCODE.x8XY0:
                self.opcode_8XY0(opcode)
            case OPCODE.x8XY1:
                self.opcode_8XY1(opcode)
            case OPCODE.x8XY2:
                self.opcode_8XY2(opcode)
            case OPCODE.x8XY3:
                self.opcode_8XY3(opcode)
            case OPCODE.x8XY4:
                self.opcode_8XY4(opcode)
            case OPCODE.x8XY5:
                self.opcode_8XY5(opcode)
            case OPCODE.x8XY6:
                self.opcode_8XY6(opcode)
            case OPCODE.x8XY7:
                self.opcode_8XY7(opcode)
            case OPCODE.x8XYE:
                self.opcode_8XYE(opcode)
            case OPCODE.x9XY0:
                self.opcode_9XY0(opcode)
            case OPCODE.xANNN:
                self.opcode_ANNN(opcode)
            case OPCODE.xBNNN:
                self.opcode_BNNN(opcode)
            case OPCODE.xCXNN:
                self.opcode_CXNN(opcode)
            case OPCODE.xDXYN:
                self.opcode_DXYN(opcode)
            case OPCODE.xEX9E:
                self.opcode_EX9E(opcode)
            case OPCODE.xEXA1:
                self.opcode_EXA1(opcode)
            case OPCODE.xFX07:
                self.opcode_FX07(opcode)
            case OPCODE.xFX0A:
                self.opcode_FX0A(opcode)
            case OPCODE.xFX15:
                self.opcode_FX15(opcode)
            case OPCODE.xFX18:
                self.opcode_FX18(opcode)
            case OPCODE.xFX1E:
                self.opcode_FX1E(opcode)
            case OPCODE.xFX29:
                self.opcode_FX29(opcode)
            case OPCODE.xFX33:
                self.opcode_FX33(opcode)
            case OPCODE.xFX55:
                self.opcode_FX55(opcode)
            case OPCODE.xFX65:
                self.opcode_FX65(opcode)

        # Update timers
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
