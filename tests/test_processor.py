import tempfile
from pathlib import Path

import pytest

from chip8emulator.memory import Memory
from chip8emulator.processor import Processor


@pytest.fixture
def processor():
    return Processor(memory=Memory(), graphics=None, keypad=None)


@pytest.mark.parametrize(
    "memory_content, program_counter, expected_opcode",
    [
        ([0xA1, 0x23], 0, 0xA123),
        ([0xA1, 0x23, 0x56, 0x78], 0, 0xA123),
        ([0xA1, 0x23, 0x56, 0x78], 1, 0x2356),
        ([0xA1, 0x23, 0x56, 0x78], 2, 0x5678),
    ],
)
def test_fetch_opcode(memory_content, program_counter, expected_opcode, processor):
    # Set up a test case with a specific opcode
    processor.memory = memory_content
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
            assert processor.memory[0x000 + i] == byte.to_bytes()


@pytest.mark.parametrize("opcode, expected_registers", [(0xA333, 0x0333)])
def test_opcode_annnn(opcode, expected_registers, processor):
    processor.opcode_ANNN(opcode)

    assert processor.index_registry == expected_registers


def test_opcode_000E(processor):
    processor.stack_pointer = 2
    processor.stack = [0x0000, 0x0001, 0x0002] + [0] * 13
    processor.program_counter = 0x111
    processor.opcode_000E()

    # The stack pointer has been decreased
    assert processor.stack_pointer == 1

    # The program counter contains the next instruction
    assert processor.program_counter == 0x0002 + 2


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
    assert processor.stack == [0, 0x111] + [0] * 14

    # The program counter contains the new address
    assert processor.program_counter == 0x0333


@pytest.mark.parametrize(
    "registry, registry_value, program_counter, opcode, expected_program_counter",
    [
        # Registry value equal to opcode NN, program counter increased by 4
        ("V7", 0x33, 0x0110, 0x3733, 0x0114),
        # Registry value not equal to opcode NN, program counter not modified
        ("VA", 0x22, 0x0110, 0x3A33, 0x0110),
    ],
)
def test_opcode_3NNN(
    processor,
    registry,
    registry_value,
    program_counter,
    opcode,
    expected_program_counter,
):
    processor.registry[registry] = registry_value
    processor.program_counter = program_counter
    processor.opcode_3NNN(opcode)

    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize(
    "registry, registry_value, program_counter, opcode, expected_program_counter",
    [
        # Registry value equal to opcode NN, program counter not modified
        ("V7", 0x33, 0x0110, 0x3733, 0x0110),
        # Registry value not equal to opcode NN, program counter increased by 4
        ("VA", 0x22, 0x0110, 0x3A33, 0x0114),
    ],
)
def test_opcode_4NNN(
    processor,
    registry,
    registry_value,
    program_counter,
    opcode,
    expected_program_counter,
):
    processor.registry[registry] = registry_value
    processor.program_counter = program_counter
    processor.opcode_4NNN(opcode)

    assert processor.program_counter == expected_program_counter


@pytest.mark.parametrize(
    "registry_x, registry_x_value, registry_y, registry_y_value, program_counter, opcode, expected_program_counter",
    [
        # Registry X equal to registry Y, program counter increased by 4
        ("V7", 0x33, "VA", 0x33, 0x0110, 0x57A0, 0x0114),
        # Registry X not equal to registry Y, program counter not modified
        ("V7", 0x33, "VA", 0x22, 0x0110, 0x57A0, 0x0110),
    ],
)
def test_opcode_5NNN(
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

    assert processor.registry["V3"] == 0x33
    assert processor.program_counter == 0x112


def test_opcode_7XNN(processor):
    processor.program_counter = 0x110
    processor.registry["V3"] = 0x22
    processor.opcode_7XNN(0x7301)

    assert processor.registry["V3"] == 0x23
    assert processor.program_counter == 0x112


def test_opcode_8XY0(processor):
    processor.registry["V3"] = 0x33
    processor.registry["V4"] = 0x22
    processor.program_counter = 0x110
    processor.opcode_8XY0(0x8340)

    assert processor.registry["V3"] == 0x22
    assert processor.program_counter == 0x112


def test_opcode_8XY1(processor):
    processor.registry["V3"] = 0b1010
    processor.registry["V4"] = 0b1100
    processor.program_counter = 0x110
    processor.opcode_8XY1(0x8341)

    assert processor.registry["V3"] == 0b1110
    assert processor.program_counter == 0x112


def test_opcode_8XY2(processor):
    processor.registry["V3"] = 0b1010
    processor.registry["V4"] = 0b1100
    processor.program_counter = 0x110
    processor.opcode_8XY2(0x8342)

    assert processor.registry["V3"] == 0b1000
    assert processor.program_counter == 0x112


def test_opcode_8XY3(processor):
    processor.registry["V3"] = 0b1010
    processor.registry["V4"] = 0b1100
    processor.program_counter = 0x110
    processor.opcode_8XY3(0x8343)

    assert processor.registry["V3"] == 0b0110
    assert processor.program_counter == 0x112


@pytest.mark.parametrize(
    "registry_x, registry_y, value_x, value_y, expected, overflow",
    [
        ("V3", "V4", 0x33, 0x22, 0x55, 0b0),
        ("V3", "V4", 0xFF, 0x01, 0x00, 0b1),
        ("V3", "V4", 0x11, 0xFF, 0x10, 0b1),
        ("V3", "V4", 0x01, 0x01, 0x02, 0b0),
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
        (3, 4, 0x33, 0x22, 0x11, 0b1),
        (3, 4, 0x11, 0x22, 0x11, 0b0),
        (3, 4, 0xAA, 0xEE, 0x44, 0b0),
        (3, 4, 0x01, 0x01, 0x00, 0b1),
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
