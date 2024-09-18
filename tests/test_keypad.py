import pytest

from chip8emulator.keypad import Keypad, NoKeyAvailable


@pytest.fixture
def keypad():
    return Keypad()


def test_press_key_valid_key(keypad):
    keypad.press_key(0x1)
    assert keypad.pressed_keys == [0x1]


def test_press_key_invalid_key(keypad):
    with pytest.raises(ValueError, match="Invalid key: 0x10"):
        keypad.press_key(0x10)


def test_press_key_non_integer(keypad):
    with pytest.raises(ValueError, match="Invalid key: a"):
        keypad.press_key("a")


def test_get_pressed_key_with_keys(keypad):
    keypad.press_key(0x1)
    keypad.press_key(0x2)
    assert keypad.get_pressed_key() == 0x1
    assert keypad.get_pressed_key() == 0x2
    assert len(keypad.pressed_keys) == 0
    with pytest.raises(NoKeyAvailable):
        keypad.get_pressed_key()


def test_is_key_available_with_keys(keypad):
    keypad.press_key(0x1)
    assert keypad.is_key_available() is True


def test_is_key_available_without_keys(keypad):
    while len(keypad.pressed_keys) > 0:
        _ = keypad.get_pressed_key()

    assert keypad.is_key_available() is False
