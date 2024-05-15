import pytest

from chip8emulator.types.nibble import Nibble


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0"),
        (1, "1"),
        (7, "7"),
        (15, "F"),
    ],
)
def test_nibble_str(value, expected):
    nibble = Nibble(value)
    assert str(nibble) == expected


@pytest.mark.parametrize(
    "value_1, value_2, expected",
    [
        (Nibble(0), Nibble(0), Nibble(0)),
        (Nibble(1), Nibble(2), Nibble(3)),
        (Nibble(7), Nibble(8), Nibble(15)),
        (Nibble(15), Nibble(1), 0),
        (1, Nibble(1), 2),
        (Nibble(1), 1, 2),
    ],
)
def test_nibble_add(value_1, value_2, expected):
    result = value_1 + value_2

    assert result.value == expected


@pytest.mark.parametrize(
    "value_1, value_2, expected",
    [
        (Nibble(0), Nibble(0), Nibble(0)),
        (Nibble(1), Nibble(2), Nibble(1)),
        (Nibble(2), Nibble(1), Nibble(1)),
        (2, Nibble(1), 1),
        (Nibble(2), 1, 1),
    ],
)
def test_nibble_sub(value_1, value_2, expected):
    result = value_1 - value_2

    assert result.value == expected


@pytest.mark.parametrize(
    "value_1, value_2, expected",
    [
        (Nibble(0), Nibble(0), True),
        (Nibble(15), Nibble(0), False),
        (Nibble(0), 0, True),
        (Nibble(0), 4, False),
        (0, Nibble(0), True),
        (15, Nibble(0), False),
    ],
)
def test_nibble_eq(value_1, value_2, expected):
    assert (value_1 == value_2) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0x0, 0x0),
        (0xA, 0xA),
        (15, 0xF),
        (16, 0x0),
    ],
)
def test_nibble_init(value, expected):
    nibble = Nibble(value)
    assert nibble.value == expected
