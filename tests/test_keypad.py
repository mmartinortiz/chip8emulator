import pytest

from chip8emulator.keypad import Keypad


@pytest.fixture
def keypad():
    return Keypad()


def test_is_key_available(keypad):
    assert keypad.is_key_available() is False
    keypad.press_key(0x1)
    keypad.release_key(0x1)
    assert keypad.is_key_available() is True


def is_key_pressed(keypad):
    assert keypad.is_key_pressed(0x1) is False
    keypad.press_key(0x1)
    assert keypad.is_key_pressed(0x1) is True
    keypad.release_key(0x1)
    assert keypad.is_key_pressed(0x1) is False


def test_get_pressed_key(keypad):
    assert keypad.get_pressed_key() == -1
    keypad.press_key(0x1)
    keypad.release_key(0x1)
    assert keypad.get_pressed_key() == 0x1
    assert keypad.get_pressed_key() == -1


def test_press_key(keypad):
    assert keypad.is_key_pressed(0x1) is False
    keypad.press_key(0x1)
    assert keypad.is_key_pressed(0x1) is True
    keypad.release_key(0x1)
    assert keypad.is_key_pressed(0x1) is False


def test_release_key(keypad):
    assert keypad.is_key_pressed(0x1) is False
    keypad.press_key(0x1)
    assert keypad.is_key_pressed(0x1) is True
    keypad.release_key(0x1)
    assert keypad.is_key_pressed(0x1) is False
    assert keypad.accumulator == 0x1
