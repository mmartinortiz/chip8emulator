import pytest

from chip8emulator.keypad import Keypad


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


@pytest.mark.skip(reason="Keypad not impelemented yet")
@pytest.mark.parametrize(
    "key, expected",
    [
        (0x1, "1"),
        (0xA, "A"),
    ],
)
def test_press_key_with_valid_nibble(keypad, key, expected):
    keypad.press_key(key)
    assert keypad.get_pressed_key() == expected
