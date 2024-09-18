import tempfile
from pathlib import Path

import pytest

from chip8emulator.graphics import Graphics
from chip8emulator.keypad import Keypad
from chip8emulator.memory import Memory
from chip8emulator.processor import Processor


@pytest.fixture
def processor():
    return Processor(
        memory=Memory(),
        graphics=Graphics(),
        keypad=Keypad(),
    )


@pytest.mark.parametrize(
    "memory_content, program_counter, expected_opcode",
    [
        ([0xA1, 0x23], 0, 0xA123),
        ([0xA1, 0x00], 0, 0xA100),
        ([0xA1, 0x23, 0x56, 0x78], 0, 0xA123),
        ([0xA1, 0x23, 0x56, 0x78], 1, 0x2356),
        ([0xA1, 0x23, 0x56, 0x78], 2, 0x5678),
    ],
)
def test_fetch_opcode(memory_content, program_counter, expected_opcode, processor):
    # Set up a test case with a specific opcode
    processor.memory = [byte for byte in memory_content]
    processor.program_counter = program_counter

    # Call the fetch_opcode method
    fetched_opcode = processor.fetch_opcode()

    # Assert that the fetched opcode matches the expected opcode
    assert fetched_opcode == expected_opcode


@pytest.mark.parametrize(
    "program_content",
    [
        bytearray(b"\xa0\xb0\xc0\xd0"),
    ],
)
def test_load_program(program_content, processor):
    with tempfile.NamedTemporaryFile(mode="wb") as temp_file:
        temp_file.write(program_content)
        temp_file.flush()

        processor.load_program(Path(temp_file.name))

        for i, byte in enumerate(program_content):
            assert processor.memory[0x200 + i] == byte


@pytest.mark.parametrize("opcode, expected_registers", [(0xA333, 0x0333)])
def test_opcode_annnn(opcode, expected_registers, processor):
    processor.opcode_ANNN(opcode)

    assert processor.index_registry == expected_registers


def test_opcode_00EE(processor):
    processor.stack_pointer = 3
    processor.stack = [0x0000, 0x0001, 0x0002] + [0] * 13
    processor.program_counter = 0x111
    processor.opcode_00EE()

    # The stack pointer has been decreased
    assert processor.stack_pointer == 2

    # The PC points to the previous tip of the stack
    assert processor.program_counter == 0x0002


def test_opcode_1NNN(processor):
    processor.stack_pointer = 1
    processor.program_counter = 0x111
    processor.opcode_1NNN(0x1333)

    # The stack and its pointer remain the same
    assert processor.stack_pointer == 1
    assert processor.stack == [0] * 16

    # The program counter contains the new address
    assert processor.program_counter == 0x0333


def test_opcode_2NNN(processor):
    processor.stack_pointer = 1
    processor.program_counter = 0x111
    processor.opcode_2NNN(0x1333)

    # Stack pointer increased by 1
    assert processor.stack_pointer == 2

    # The stack contains the previous program counter
    assert processor.stack == [0, 0x113] + [0] * 14

    # The program counter contains the new address
    assert processor.program_counter == 0x0333


@pytest.mark.parametrize(
    "registry, registry_value, program_counter, opcode, expected_program_counter",
    [
        # Registry value equal to opcode NN, program counter increased by 4
        (0x7, 0x33, 0x0110, 0x3733, 0x0114),
        # Registry value not equal to opcode NN, program counter not modified
        (0xA, 0x22, 0x0110, 0x3A33, 0x0112),
    ],
)
def test_opcode_3XNN(
    processor,
    registry,
    registry_value,
    program_counter,
    opcode,
    expected_program_counter,
):
    processor.registry[registry] = registry_value
    processor.program_counter = program_counter
    processor.opcode_3XNN(opcode)

    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize(
    "registry, registry_value, program_counter, opcode, expected_program_counter",
    [
        # Registry value equal to opcode NN, program counter not modified
        (0x7, 0x33, 0x0110, 0x3733, 0x0112),
        # Registry value not equal to opcode NN, program counter increased by 4
        (0xA, 0x22, 0x0110, 0x3A33, 0x0114),
    ],
)
def test_opcode_4XNN(
    processor,
    registry,
    registry_value,
    program_counter,
    opcode,
    expected_program_counter,
):
    processor.registry[registry] = registry_value
    processor.program_counter = program_counter
    processor.opcode_4XNN(opcode)

    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize(
    "registry_x, registry_x_value, registry_y, registry_y_value, program_counter, opcode, expected_program_counter",
    [
        # Registry X equal to registry Y, program counter increased by 4
        (0x7, 0x33, 0xA, 0x33, 0x0110, 0x57A0, 0x0114),
        # Registry X not equal to registry Y, program counter not modified
        (0x7, 0x33, 0xA, 0x22, 0x0110, 0x57A0, 0x0112),
    ],
)
def test_opcode_5XYN(
    processor,
    registry_x,
    registry_x_value,
    registry_y,
    registry_y_value,
    program_counter,
    opcode,
    expected_program_counter,
):
    processor.registry[registry_x] = registry_x_value
    processor.registry[registry_y] = registry_y_value
    processor.program_counter = program_counter
    processor.opcode_5XY0(opcode)

    assert processor.program_counter == expected_program_counter


def test_opcode_6XNN(processor):
    processor.program_counter = 0x110
    processor.opcode_6XNN(0x6333)

    assert processor.registry[0x3] == 0x33
    assert processor.program_counter == 0x112


def test_opcode_7XNN(processor):
    processor.program_counter = 0x110
    processor.registry[0x3] = 0x22
    processor.opcode_7XNN(0x7301)

    assert processor.registry[0x3] == 0x23
    assert processor.program_counter == 0x112


def test_opcode_8XY0(processor):
    processor.registry[0x3] = 0x33
    processor.registry[0x4] = 0x22
    processor.program_counter = 0x110
    processor.opcode_8XY0(0x8340)

    assert processor.registry[0x3] == 0x22
    assert processor.program_counter == 0x112


def test_opcode_8XY1(processor):
    processor.registry[0x3] = 0b1010
    processor.registry[0x4] = 0b1100
    processor.program_counter = 0x110
    processor.opcode_8XY1(0x8341)

    assert processor.registry[0x3] == 0b1110
    assert processor.program_counter == 0x112


def test_opcode_8XY2(processor):
    processor.registry[0x3] = 0b1010
    processor.registry[0x4] = 0b1100
    processor.program_counter = 0x110
    processor.opcode_8XY2(0x8342)

    assert processor.registry[0x3] == 0b1000
    assert processor.program_counter == 0x112


def test_opcode_8XY3(processor):
    processor.registry[0x3] = 0b1010
    processor.registry[0x4] = 0b1100
    processor.program_counter = 0x110
    processor.opcode_8XY3(0x8343)

    assert processor.registry[0x3] == 0b0110
    assert processor.program_counter == 0x112


@pytest.mark.parametrize(
    "registry_x, registry_y, value_x, value_y, expected, overflow",
    [
        (0x3, 0x4, 0x33, 0x22, 0x55, 0b0),
        (0x3, 0x4, 0xFF, 0x01, 0x00, 0b1),
        (0x3, 0x4, 0x11, 0xFF, 0x10, 0b1),
        (0x3, 0x4, 0x01, 0x01, 0x02, 0b0),
    ],
)
def test_opcode_8XY4(
    processor, registry_x, registry_y, value_x, value_y, expected, overflow
):
    processor.registry[registry_x] = value_x
    processor.registry[registry_y] = value_y
    processor.program_counter = 0x110
    processor.opcode_8XY4(0x8344)

    assert processor.registry[registry_x] == expected
    assert processor.carry_flag == overflow
    assert processor.program_counter == 0x112


@pytest.mark.parametrize(
    "registry_x, registry_y, value_x, value_y, expected, overflow",
    [
        (0x3, 0x4, 0x33, 0x22, 0x11, 0b1),
        (0x3, 0x4, 0x11, 0x22, 0xEF, 0b0),
        (0x3, 0x4, 0xAA, 0xEE, 0xBC, 0b0),
        (0x3, 0x4, 0x01, 0x01, 0x00, 0b1),
    ],
)
def test_opcode_8XY5(
    processor, registry_x, registry_y, value_x, value_y, expected, overflow
):
    processor.registry[registry_x] = value_x
    processor.registry[registry_y] = value_y
    processor.program_counter = 0x110
    processor.opcode_8XY5(int(f"0x8{registry_x}{registry_y}5", 16))

    assert processor.registry[registry_x] == expected
    assert processor.carry_flag == overflow
    assert processor.program_counter == 0x112


@pytest.mark.parametrize(
    "registry_x, value_x, program_counter, expected_registry, expected_carry, expected_program_counter",
    [
        (0x3, 0b1110, 0x110, 0b0111, 0, 0x112),
        (0x3, 0b1101, 0x110, 0b0110, 1, 0x112),
    ],
)
def test_opcode_8XY6(
    processor,
    registry_x,
    value_x,
    program_counter,
    expected_registry,
    expected_carry,
    expected_program_counter,
):
    processor.registry[registry_x] = value_x
    processor.program_counter = program_counter
    processor.opcode_8XY6(int(f"0x8{registry_x}06", 16))

    assert processor.registry[registry_x] == expected_registry
    assert processor.carry_flag == expected_carry
    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize(
    "registry_x, registry_y, value_x, value_y, expected, overflow",
    [
        (3, 4, 0x33, 0x22, 0x11, 0b0),
        (3, 4, 0x11, 0x22, 0x11, 0b1),
    ],
)
def test_opcode_8XY7(
    processor, registry_x, registry_y, value_x, value_y, expected, overflow
):
    processor.registry[registry_x] = value_x
    processor.registry[registry_y] = value_y
    processor.program_counter = 0x110
    processor.opcode_8XY7(int(f"0x8{registry_x}{registry_y}7", 16))

    assert processor.registry[registry_x] == expected
    assert processor.carry_flag == overflow
    assert processor.program_counter == 0x112


@pytest.mark.parametrize(
    "registry_x, value_x, expected_value, expected_carry",
    [
        (3, 0b01111111, 0b11111110, 0b0),
        (3, 0b10000000, 0b00000000, 0b1),
    ],
)
def test_opcode_8XYE(
    processor,
    registry_x,
    value_x,
    expected_value,
    expected_carry,
):
    processor.registry[registry_x] = value_x
    processor.program_counter = 0x110
    processor.opcode_8XYE(int(f"0x8{registry_x}0E", 16))

    assert processor.registry[registry_x] == expected_value
    assert processor.carry_flag == expected_carry
    assert processor.program_counter == 0x112


@pytest.mark.parametrize(
    "registry_x, registry_y, value_x, value_y, program_counter, expected_program_counter",
    [
        # VX not equal to VY, skip next instruction
        (0x3, 0x4, 0x33, 0x22, 0x0110, 0x0114),
        # VX equal to VY, do not skip next instruction
        (0x3, 0x4, 0x33, 0x33, 0x0110, 0x0112),
    ],
)
def test_opcode_9XY0(
    processor,
    registry_x,
    registry_y,
    value_x,
    value_y,
    program_counter,
    expected_program_counter,
):
    processor.registry[registry_x] = value_x
    processor.registry[registry_y] = value_y
    processor.program_counter = program_counter
    processor.opcode_9XY0(int(f"0x9{registry_x}{registry_y}0", 16))

    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize(
    "opcode, v0, expected_program_counter",
    [
        (0xB123, 0x0000, 0x0123),
        (0xB456, 0xB100, 0xB556),
    ],
)
def test_opcode_BNNN(processor, opcode, v0, expected_program_counter):
    processor.registry[0] = v0
    processor.opcode_BNNN(opcode)
    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize("registry, opcode, expected", [(3, 0xC3AA, 0xA)])
def test_opcode_CXNN(processor, registry, opcode, expected, monkeypatch):
    def mock_randint(a, b):
        return 0xF

    monkeypatch.setattr("random.randint", mock_randint)

    processor.opcode_CXNN(opcode)

    assert processor.registry[registry] == expected


@pytest.mark.parametrize(
    "registry_x, registry_y, height, x, y, index_registry, memory, pixels, expected, carry",
    [
        (
            0x4,
            0x5,
            0x3,
            0x1,
            0x1,
            1,
            [0x00, 0x3C, 0xC3, 0xFF, 0xFF],
            [list(0 for _ in range(10)) for _ in range(6)],
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            0,
        ),
        (
            4,
            5,
            3,
            0x1,
            0x1,
            1,
            [0x00, 0x3C, 0xC3, 0xFF, 0xFF],
            # For the current state of the pixels, we expect a collision.
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            1,
        ),
    ],
)
def test_opcode_DXYN(
    processor,
    registry_x,
    registry_y,
    height,
    x,
    y,
    index_registry,
    memory,
    pixels,
    expected,
    carry,
):
    processor.program_counter = 0x110
    processor.registry[registry_x] = x
    processor.registry[registry_y] = y
    processor.index_registry = index_registry
    processor.memory.memory = memory
    processor.graphics.pixels = pixels
    processor.opcode_DXYN(int(f"0xD{registry_x}{registry_y}{height}", 16))

    assert processor.graphics.pixels == expected
    assert processor.carry_flag == carry
    assert processor.program_counter == 0x112


@pytest.mark.parametrize(
    "registry_x, program_counter, x_value, key_pressed, expected",
    [
        (1, 0x110, 0x1, 0x1, 0x114),
        (1, 0x110, 0x1, 0x6, 0x112),
    ],
)
def test_opcode_EX9E(
    processor, registry_x, program_counter, x_value, key_pressed, expected
):
    processor.program_counter = program_counter
    processor.registry[registry_x] = x_value
    processor.keypad.press_key(key_pressed)
    processor.opcode_EX9E(int(f"0xE{registry_x}9E", 16))

    assert processor.program_counter == expected


@pytest.mark.parametrize(
    "registry_x, program_counter, x_value, key_pressed, expected",
    [
        (1, 0x110, 0x1, 0x1, 0x112),
        (1, 0x110, 0x1, 0x6, 0x114),
    ],
)
def test_opcode_EXA1(
    processor, registry_x, program_counter, x_value, key_pressed, expected
):
    processor.program_counter = program_counter
    processor.registry[registry_x] = x_value
    processor.keypad.press_key(key_pressed)
    processor.opcode_EXA1(int(f"0xE{registry_x}A1", 16))

    assert processor.program_counter == expected


@pytest.mark.parametrize(
    "program_counter, registry_x, delay, expected_pc",
    [
        (0x110, 0x3, 0x22, 0x112),
        (0x110, 0x3, 0x00, 0x112),
    ],
)
def test_opcode_FX07(processor, program_counter, registry_x, delay, expected_pc):
    processor.program_counter = program_counter
    processor.delay_timer = delay
    processor.opcode_FX07(int(f"0xF{registry_x}07", 16))

    assert processor.registry[registry_x] == delay
    assert processor.program_counter == expected_pc


@pytest.mark.parametrize(
    "registry_x, value, expected_delay_timer, expected_program_counter",
    [
        (3, 0x22, 0x22, 0x112),
        (5, 0x00, 0x00, 0x112),
    ],
)
def test_opcode_FX15(
    processor, registry_x, value, expected_delay_timer, expected_program_counter
):
    processor.registry[registry_x] = value
    processor.program_counter = 0x110
    processor.opcode_FX15(int(f"0xF{registry_x}15", 16))

    assert processor.delay_timer == expected_delay_timer
    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize(
    "registry_x, value, expected_sound_timer, expected_program_counter",
    [
        (3, 0x22, 0x22, 0x112),
        (5, 0x00, 0x00, 0x112),
    ],
)
def test_opcode_FX18(
    processor, registry_x, value, expected_sound_timer, expected_program_counter
):
    processor.registry[registry_x] = value
    processor.program_counter = 0x110
    processor.opcode_FX18(int(f"0xF{registry_x}18", 16))

    assert processor.sound_timer == expected_sound_timer
    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize(
    "registry_x, value, initial_index, expected_index, pc, expected_pc",
    [
        (3, 0x22, 0x100, 0x122, 0x110, 0x112),
        (5, 0x10, 0x200, 0x210, 0x110, 0x112),
    ],
)
def test_opcode_FX1E(
    processor,
    registry_x,
    value,
    initial_index,
    expected_index,
    pc,
    expected_pc,
):
    processor.registry[registry_x] = value
    processor.index_registry = initial_index
    processor.program_counter = pc
    processor.opcode_FX1E(int(f"0xF{registry_x}1E", 16))

    assert processor.index_registry == expected_index
    assert processor.program_counter == expected_pc


@pytest.mark.parametrize(
    "registry_x, value, expected_index_registry, expected_program_counter",
    [
        (3, 0x0, 0x050, 0x112),
        (5, 0x1, 0x055, 0x112),
    ],
)
def test_opcode_FX29(
    processor, registry_x, value, expected_index_registry, expected_program_counter
):
    processor.registry[registry_x] = value
    processor.program_counter = 0x110
    processor.opcode_FX29(int(f"0xF{registry_x}29", 16))

    assert processor.index_registry == expected_index_registry
    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize(
    "registry_x, value, expected_memory, expected_program_counter",
    [
        (3, 0x9C, [1, 5, 6], 0x112),
        (5, 255, [2, 5, 5], 0x112),
        (7, 123, [1, 2, 3], 0x112),
        (9, 0, [0, 0, 0], 0x112),
    ],
)
def test_opcode_FX33(
    processor, registry_x, value, expected_memory, expected_program_counter
):
    processor.registry[registry_x] = value
    processor.index_registry = 0x300
    processor.program_counter = 0x110
    processor.opcode_FX33(int(f"0xF{registry_x}33", 16))

    assert processor.memory[processor.index_registry] == expected_memory[0]
    assert processor.memory[processor.index_registry + 1] == expected_memory[1]
    assert processor.memory[processor.index_registry + 2] == expected_memory[2]
    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize(
    "registry_x, registry_values, index_registry, expected_memory, pc, expected_program_counter",
    [
        (
            3,
            [0x01, 0x02, 0x03, 0x04],
            0x200,
            [0x01, 0x02, 0x03, 0x04],
            0x200,
            0x202,
        ),
        (
            5,
            [0x01, 0x02, 0x03, 0x04, 0x05, 0x06],
            0x300,
            [0x01, 0x02, 0x03, 0x04, 0x05, 0x06],
            0x200,
            0x202,
        ),
    ],
)
def test_opcode_FX55(
    processor,
    registry_x,
    registry_values,
    index_registry,
    expected_memory,
    pc,
    expected_program_counter,
):
    for i, value in enumerate(registry_values):
        processor.registry[i] = value
    processor.index_registry = index_registry
    processor.program_counter = pc

    processor.opcode_FX55(int(f"0xF{registry_x}55", 16))

    for i in range(registry_x + 1):
        assert processor.memory[processor.index_registry + i] == expected_memory[i]

    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize(
    "index_registry, memory_values, registry_x, expected_registry_values",
    [
        (0x300, [0x12, 0x34, 0x56, 0x78, 0x9A], 4, [0x12, 0x34, 0x56, 0x78, 0x9A]),
        (0x200, [0x01, 0x02, 0x03], 2, [0x01, 0x02, 0x03]),
        (0x100, [0xFF, 0xEE, 0xDD, 0xCC], 3, [0xFF, 0xEE, 0xDD, 0xCC]),
    ],
)
def test_opcode_FX65(
    processor, index_registry, memory_values, registry_x, expected_registry_values
):
    processor.index_registry = index_registry
    for i, value in enumerate(memory_values):
        processor.memory[index_registry + i] = value
    processor.program_counter = 0x200
    processor.opcode_FX65(int(f"0xF{registry_x}65", 16))

    for i in range(registry_x + 1):
        assert processor.registry[i] == expected_registry_values[i]
    assert processor.program_counter == 0x202
