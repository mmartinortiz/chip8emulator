import pytest

from chip8emulator.keypad import Keypad
from chip8emulator.types import Nibble


@pytest.fixture
def keypad():
    return Keypad()


@pytest.mark.parametrize(
    "key, expected",
    [
        ("1", "1"),
        ("A", "A"),
    ],
)
def test_press_key_with_valid_string(keypad, key, expected):
    keypad.press_key(key)
    assert keypad.get_pressed_key() == expected


def test_press_key_with_invalid_string(keypad):
    with pytest.raises(ValueError):
        keypad.press_key("G")


@pytest.mark.parametrize(
    "key, expected",
    [
        (Nibble(0x1), "1"),
        (Nibble(0xA), "A"),
    ],
)
def test_press_key_with_valid_nibble(keypad, key, expected):
    keypad.press_key(key)
    assert keypad.get_pressed_key() == expected


@pytest.mark.parametrize(
    "key, expected",
    [
        ("1", Nibble(0x1)),
        ("A", Nibble(0xA)),
    ],
)
def test_get_pressed_key_as_nibble_with_valid_string(keypad, key, expected):
    keypad.press_key(key)
    assert keypad.get_pressed_key_as_nibble() == expected


@pytest.mark.parametrize(
    "key, expected",
    [
        (Nibble(0x1), Nibble(0x1)),
        (Nibble(0xA), Nibble(0xA)),
    ],
)
def test_get_pressed_key_as_nibble_with_valid_nibble(keypad, key, expected):
    keypad.press_key(key)
    assert keypad.get_pressed_key_as_nibble() == expected
