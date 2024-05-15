import pytest

from chip8emulator.types import Word


def test_word_get_high_byte():
    word = Word(0xABCD)
    assert word.get_high_byte() == 0xAB


def test_word_get_low_byte():
    word = Word(0xABCD)
    assert word.get_low_byte() == 0xCD


def test_word_get_first_nibble():
    word = Word(0xABCD)
    assert word.get_first_nibble() == 0xA


def test_word_get_second_nibble():
    word = Word(0xABCD)
    assert word.get_second_nibble() == 0xB


def test_word_get_third_nibble():
    word = Word(0xABCD)
    assert word.get_third_nibble() == 0xC


def test_word_get_fourth_nibble():
    word = Word(0xABCD)
    assert word.get_fourth_nibble() == 0xD


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Word(0x1234), Word(0x5678), Word(0x68AC)),
        (Word(0xFFFF), Word(0x0001), Word(0x0000)),
        (Word(0x1234), 1, Word(0x1235)),
        (1, Word(0x1234), Word(0x1235)),
    ],
)
def test_word_add(a, b, expected):
    result = a + b
    assert result == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Word(0x1234), Word(0x5678), Word(0x4444)),
        (Word(0xFFFF), Word(0x0001), Word(0xFFFE)),
        (Word(0xFFFF), 1, Word(0xFFFE)),
        (1, Word(0xFFFF), Word(0xFFFE)),
    ],
)
def test_word_sub(a, b, expected):
    result = a - b
    assert result == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Word(0x1234), Word(0x5678), True),
        (Word(0x5678), Word(0x1234), False),
        (Word(4), 5, True),
        (Word(0x1234), 5, False),
    ],
)
def test_word_lt(a, b, expected):
    result = a < b
    assert result == expected
