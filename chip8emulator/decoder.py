from chip8emulator.opcodes import OPCODE


def decode(opcode: int) -> OPCODE:
    """
    Decode the opcode and return the corresponding enum value.

    Args:
        opcode (int): Opcode to decode.

    Returns:
        Opcodes: Enum value corresponding to the opcode.
    """
    match opcode & 0xF000:
        case 0x1000:
            # Jump to address NNN
            return OPCODE.x1NNN
        case 0x2000:
            # Call to subroutine at NNN
            return OPCODE.x2NNN
        case 0x3000:
            return OPCODE.x3XNN
        case 0x4000:
            return OPCODE.x4XNN
        case 0x5000:
            return OPCODE.x5XY0
        case 0x6000:
            return OPCODE.x6XNN
        case 0x7000:
            return OPCODE.x7XNN
        case 0x8000:
            match opcode & 0x000F:
                case 0x0000:
                    return OPCODE.x8XY0
                case 0x0001:
                    return OPCODE.x8XY1
                case 0x0002:
                    return OPCODE.x8XY2
                case 0x0003:
                    return OPCODE.x8XY3
                case 0x0004:
                    return OPCODE.x8XY4
                case 0x0005:
                    return OPCODE.x8XY5
                case 0x0006:
                    return OPCODE.x8XY6
                case 0x0007:
                    return OPCODE.x8XY7
                case 0x000E:
                    return OPCODE.x8XYE
        case 0x9000:
            return OPCODE.x9XY0
        case 0xA000:
            return OPCODE.xANNN
        case 0xB000:
            return OPCODE.xBNNN
        case 0xC000:
            return OPCODE.xCXNN
        case 0xD000:
            return OPCODE.xDXYN
        case 0xE000:
            match opcode & 0x00FF:
                case 0x009E:
                    return OPCODE.xEX9E
                case 0x00A1:
                    return OPCODE.xEXA1
        case 0xF000:
            match opcode & 0x00FF:
                case 0x0007:
                    return OPCODE.xFX07
                case 0x000A:
                    return OPCODE.xFX0A
                case 0x0015:
                    return OPCODE.xFX15
                case 0x0018:
                    return OPCODE.xFX18
                case 0x001E:
                    return OPCODE.xFX1E
                case 0x0029:
                    return OPCODE.xFX29
                case 0x0033:
                    return OPCODE.xFX33
                case 0x0055:
                    return OPCODE.xFX55
                case 0x0065:
                    return OPCODE.xFX65

    match opcode & 0x00E0:
        case 0x00E0:
            match opcode & 0x00EE:
                case 0x00EE:
                    return OPCODE.x00EE
                case _:
                    return OPCODE.x00E0
