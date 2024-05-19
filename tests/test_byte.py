import pytest

from chip8emulator.types import Byte, Nibble


def test_byte_get_high_nibble():
    byte = Byte(0xAB)
    nibble = byte.get_high_nibble()

    assert nibble == 0xA
    assert isinstance(nibble, Nibble)


def test_byte_get_low_nibble():
    byte = Byte(0xAB)
    nibble = byte.get_low_nibble()

    assert nibble == 0xB
    assert isinstance(nibble, Nibble)


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Byte(0x10), Byte(0x20), Byte(0x30)),
        (Byte(0xAA), Byte(0x60), Byte(0x0A)),
        (Byte(0x10), 1, Byte(0x11)),
        (1, Byte(0x10), Byte(0x11)),
    ],
)
def test_byte_add(a, b, expected):
    assert a + b == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Byte(0x10), Byte(0x10), Byte(0x00)),
        (Byte(0x20), Byte(0x10), Byte(0x10)),
        (Byte(0x30), Byte(0x40), Byte(0x10)),
        (Byte(0x10), 1, Byte(0x0F)),
        (1, Byte(0x10), Byte(0x0F)),
    ],
)
def test_byte_sub(a, b, expected):
    assert a - b == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Byte(0x10), Byte(0x20), True),
        (Byte(0x20), Byte(0x10), False),
    ],
)
def test_lt_byte(a, b, expected):
    assert (a < b) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0x00, 0x00),
        (0xFF, 0xFF),
    ],
)
def test_byte_abs(value, expected):
    byte = Byte(value)
    abs_byte = abs(byte)

    assert abs_byte == expected
    assert isinstance(abs_byte, Byte)


@pytest.mark.parametrize(
    "value, expected",
    [
        (0x12, 0x12),
        (128, 0x80),
        (255, 0xFF),
        (256, 0x00),
    ],
)
def test_byte_init(value, expected):
    byte = Byte(value)
    assert byte.value == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Byte(0x10), Byte(0x20), Byte(0x00)),
        (Byte(0xAA), Byte(0x60), Byte(0x20)),
        (Byte(0x10), 1, Byte(0x00)),
        (1, Byte(0x10), Byte(0x00)),
    ],
)
def test_byte_and(a, b, expected):
    assert (a & b) == expected
