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

    @property
    def carry_flag(self) -> int:
        """VF is also used as a flag register; many instructions will set it to
        either 1 or 0 based on some rule, for example using it as a carry flag"""
        return self.registry[0xF]

    @carry_flag.setter
    def carry_flag(self, value: int) -> None:
        self.registry[0xF] = value

    def reset(self) -> None:
        # Registers.
        # VF is also used as a flag register; many instructions will set it to
        # either 1 or 0 based on some rule, for example using it as a carry flag
        self.registry = {k: v for k, v in enumerate([0] * 16)}

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

        self.font_memory_map = {
            0x0: None,
            0x1: None,
            0x2: None,
            0x3: None,
            0x4: None,
            0x5: None,
            0x6: None,
            0x7: None,
            0x8: None,
            0x9: None,
            0xA: None,
            0xB: None,
            0xC: None,
            0xD: None,
            0xE: None,
            0xF: None,
        }
        self.load_font(font_file=Path(__file__).parent / Path("fonts.ch8"))

        # Flag that indicates if the CPU is blocked in a blocking operation
        # Used in the FX0A opcode to wait for a key to be pressed. When the
        # execution is blocked, the CPU will not advance to the next instruction.
        self.withhold_execution = False
        self.redraw = False

    def load_font(self, font_file: Path) -> None:
        if not font_file.exists():
            raise FileNotFoundError(f"Font file {font_file} not found")
        with font_file.open("rb") as f:
            pointer = 0x050
            for key in self.font_memory_map.keys():
                self.font_memory_map[key] = pointer
                bytes_read = 0
                while bytes_read < 5:
                    chunk = f.read(1)
                    if not chunk:
                        break
                    self.memory[pointer] = int.from_bytes(chunk)
                    pointer += 1
                    bytes_read += 1

    def load_program(self, program: Path) -> None:
        program = Path(program)
        if not program.exists():
            raise FileNotFoundError(f"Program file {program} not found")
        with program.open("rb") as f:
            pointer = 0x200
            while chunk := f.read(1):
                self.memory[pointer] = chunk
                pointer += 1

    def skip_next_instruction(self) -> None:
        if not self.withhold_execution:
            self.program_counter += 4

    def continue_to_next_instruction(self) -> None:
        if not self.withhold_execution:
            self.program_counter += 2

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

        self.continue_to_next_instruction()
        self.redraw = True

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
            self.skip_next_instruction()
        else:
            self.continue_to_next_instruction()

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
            self.skip_next_instruction()
        else:
            self.continue_to_next_instruction()

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
            self.skip_next_instruction()
        else:
            self.continue_to_next_instruction()

    def opcode_6XNN(self, opcode: int) -> None:
        """Sets VX to NN"""
        registry = get_second_nibble(opcode)
        value = get_low_byte(opcode)

        self.registry[registry] = value
        self.continue_to_next_instruction()

    def opcode_7XNN(self, opcode: int) -> None:
        """Adds NN to VX (carry flag is not changed)"""
        registry = get_second_nibble(opcode)
        value = get_low_byte(opcode)

        new_value = (self.registry[registry] + value) & 0xFF
        self.registry[registry] = new_value
        self.continue_to_next_instruction()

    def opcode_8XY0(self, opcode: int) -> None:
        """Sets VX to the value of VY"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        self.registry[registry_x] = self.registry[registry_y]
        self.continue_to_next_instruction()

    def opcode_8XY1(self, opcode: int) -> None:
        """Sets VX to VX OR VY"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        self.registry[registry_x] |= self.registry[registry_y]
        self.continue_to_next_instruction()

    def opcode_8XY2(self, opcode: int) -> None:
        """Sets VX to VX AND VY"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        self.registry[registry_x] &= self.registry[registry_y]
        self.continue_to_next_instruction()

    def opcode_8XY3(self, opcode: int) -> None:
        """Sets VX to VX XOR VY"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        self.registry[registry_x] ^= self.registry[registry_y]
        self.continue_to_next_instruction()

    def opcode_8XY4(self, opcode: int) -> None:
        """Vx is set to the value of Vx + Vy. Vy is not affected.

        Unlike 7XNN, this addition will affect the carry flag. If the result is larger
        than 255 (and thus overflows the 8-bit register VX), the flag register VF is set
        to 1. If it doesn't overflow, VF is set to 0."""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        value = self.registry[registry_x] + self.registry[registry_y]

        if value > 255:
            self.registry[registry_x] = value & 0xFF
            self.carry_flag = 0b1
        else:
            self.registry[registry_x] = value
            self.carry_flag = 0b0

        self.continue_to_next_instruction()

    def opcode_8XY5(self, opcode: int) -> None:
        """Sets VX = VX - VY.

        This subtraction will also affect the carry flag. If the minuend (the first
        operand) is larger than the subtrahend (second operand), VF will be set to 1.

        If the subtrahend is larger, and we “underflow” the result, VF is set to 0.
        Another way of thinking of it is that VF is set to 1 before the subtraction,
        and then the subtraction either borrows from VF (setting it to 0) or not.

        """
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        value = (self.registry[registry_x] - self.registry[registry_y]) & 0xFF

        if self.registry[registry_x] >= self.registry[registry_y]:
            # Heads up!: if vF is also the carry flag, and the carry flag will
            # be the last to be set, even if it overwrites the operation result.
            self.registry[registry_x] = value
            self.carry_flag = 0b1
        else:
            self.registry[registry_x] = value
            self.carry_flag = 0b0

        self.continue_to_next_instruction()

    def opcode_8XY6(self, opcode: int) -> None:
        """vX = vY >> 1

        Put the value of VY into VX, and then shifted the value in VX 1 bit to the
        right. VY was not affected, but the flag register VF would be set to the bit
        that was shifted out.

        1. Set VX to the value of VY
        2. Shift the value of VX one bit to the right
        3. Set VF to 1 if the bit that was shifted out was 1, or 0 if it was 0
        """
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        self.registry[registry_x] = self.registry[registry_y]

        shifted = self.registry[registry_x] & 0b1

        self.registry[registry_x] = (self.registry[registry_x] >> 1) & 0xFF
        self.carry_flag = shifted

        self.continue_to_next_instruction()

    def opcode_8XY7(self, opcode: int) -> None:
        """Sets VX = VY - VX

        This subtraction will also affect the carry flag. If the minuend (the first
        operand) is larger than the subtrahend (second operand), VF will be set to 1.

        If the subtrahend is larger, and we “underflow” the result, VF is set to 0.
        Another way of thinking of it is that VF is set to 1 before the subtraction,
        and then the subtraction either borrows from VF (setting it to 0) or not.
        """
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        value = (self.registry[registry_y] - self.registry[registry_x]) & 0xFF
        self.registry[registry_x] = value

        if self.registry[registry_y] > self.registry[registry_x]:
            self.carry_flag = 0b1
        else:
            self.carry_flag = 0b0

        self.continue_to_next_instruction()

    def opcode_8XYE(self, opcode: int) -> None:
        """vX = vY << 1

        Put the value of VY into VX, and then shifted the value in VX 1 bit to the left.
        VY was not affected, but the flag register VF would be set to the bit that was
        shifted out.

        1. Set VX to the value of VY
        2. Shift the value of VX one bit to the left
        3. Set VF to 1 if the bit that was shifted out was 1, or 0 if it was 0"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        self.registry[registry_x] = self.registry[registry_y]

        shifted = 0x1 if (self.registry[registry_x] & 0b10000000) > 0 else 0x0

        self.registry[registry_x] = (self.registry[registry_x] << 1) & 0xFF
        self.carry_flag = shifted

        self.continue_to_next_instruction()

    def opcode_9XY0(self, opcode: int) -> None:
        """Skips the next instruction if VX does not equal VY. (Usually the next
        instruction is a jump to skip a code block)"""
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)

        if self.registry[registry_x] != self.registry[registry_y]:
            self.skip_next_instruction()
        else:
            self.continue_to_next_instruction()

    def opcode_ANNN(self, opcode: int) -> None:
        """
        Sets the value of the index registry to the address specified in the opcode.

        Parameters:
        - opcode (int): The opcode containing the address to be set.
        """
        address = opcode & 0x0FFF
        self.index_registry = address
        self.continue_to_next_instruction()

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
        It will draw an N pixels tall sprite from the memory location that the I index
        register is holding to the screen, at the horizontal X coordinate in VX and
        the Y coordinate in VY.

        All the pixels that are “on” in the sprite will flip the pixels on the screen
        that it is drawn to (from left to right, from most to least significant bit).

        If any pixels on the screen were turned “off” by this, the VF flag register
        is set to 1. Otherwise, it's set to 0.
        """
        registry_x = get_second_nibble(opcode)
        registry_y = get_third_nibble(opcode)
        height = get_fourth_nibble(opcode)

        x = self.registry[registry_x]
        y = self.registry[registry_y]

        self.carry_flag = 0

        sprite = self.memory[self.index_registry : self.index_registry + height]

        for line, sprite_line in enumerate(sprite):
            screen_line = self.graphics.get_byte(x, y + line)

            # Perform a bitwise XOR operation to flip the pixels
            self.graphics.set_byte(x, y + line, sprite_line ^ screen_line)

            # If any pixel on the screen was turned off, set the carry flag to 1
            if self.carry_flag == 0 and sprite_line & screen_line > 0:
                self.carry_flag = 1

        self.continue_to_next_instruction()
        self.redraw = True

    def opcode_EX9E(self, opcode: int) -> None:
        """Skips the next instruction if the key stored in VX is pressed (usually the
        next instruction is a jump to skip a code block)."""
        registry_x = get_second_nibble(opcode)

        if self.keypad.is_key_pressed(self.registry[registry_x]):
            self.skip_next_instruction()
        else:
            self.continue_to_next_instruction()

    def opcode_EXA1(self, opcode: int) -> None:
        """Skips the next instruction if the key stored in VX is not pressed (usually
        the next instruction is a jump to skip a code block)."""
        registry_x = get_second_nibble(opcode)

        if not self.keypad.is_key_pressed(self.registry[registry_x]):
            self.skip_next_instruction()
        else:
            self.continue_to_next_instruction()

    def opcode_FX07(self, opcode: int) -> None:
        """Sets VX to the value of the delay timer."""
        registry_x = get_second_nibble(opcode)

        self.registry[registry_x] = self.delay_timer
        self.continue_to_next_instruction()

    def opcode_FX0A(self, opcode: int) -> None:
        """A key press is awaited, and then stored in VX (blocking operation, all
        instruction halted until next key event).

        In other words: Wait for a key to pressed and then released. The original COSMAC
        VIP only registered the key when it was pressed and then released."""
        # If the execution is not halted and there is a key available, ignore such
        # key and continue, halting until there is a new key available.
        # This is done to mimic the implementation of the original COSMAC VIP, where
        # this instruction waits for a key to be pressed and then released. In the current
        # keypad implementation, the key is kept registered until a new one fullfils
        # the press-release cycle.
        if not self.withhold_execution and self.keypad.is_key_available():
            _ = self.keypad.get_pressed_key()

        if self.keypad.is_key_available():
            self.withhold_execution = False

            registry_x = get_second_nibble(opcode)
            self.registry[registry_x] = self.keypad.get_pressed_key()
            self.continue_to_next_instruction()
        else:
            self.withhold_execution = True

    def opcode_FX15(self, opcode: int) -> None:
        """Sets the delay timer to VX"""
        registry_x = get_second_nibble(opcode)

        self.delay_timer = self.registry[registry_x]
        self.continue_to_next_instruction()

    def opcode_FX18(self, opcode: int) -> None:
        """Sets the sound timer to VX"""
        registry_x = get_second_nibble(opcode)

        self.sound_timer = self.registry[registry_x]
        self.continue_to_next_instruction()

    def opcode_FX1E(self, opcode: int) -> None:
        """Adds VX to I. VF is not affected."""
        registry_x = get_second_nibble(opcode)

        self.index_registry += self.registry[registry_x]
        self.continue_to_next_instruction()

    def opcode_FX29(self, opcode: int) -> None:
        """The index register I is set to the address of the hexadecimal character in
        VX."""
        registry_x = get_second_nibble(opcode)

        character = self.registry[registry_x]
        self.index_registry = self.font_memory_map[character]

        self.continue_to_next_instruction()

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

        self.continue_to_next_instruction()

    def opcode_FX55(self, opcode: int) -> None:
        """The value of each variable register from V0 to VX inclusive (if X is 0, then
        only V0) will be stored in successive memory addresses, starting with the one
        that's stored in I. V0 will be stored at the address in I, V1 will be stored
        in I + 1, and so on, until VX is stored in I + X.
        """
        registry_x = get_second_nibble(opcode)

        for i in range(registry_x + 1):
            self.memory[self.index_registry + i] = self.registry[i]

        self.continue_to_next_instruction()

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

        self.continue_to_next_instruction()

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
