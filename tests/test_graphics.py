import pytest
from bitarray import bitarray

from chip8emulator.graphics import Graphics


def test_graphics_clear():
    graphics = Graphics()
    graphics.clear()

    assert all(pixel == 0x00 for pixel in graphics.pixels)


@pytest.mark.parametrize(
    "pixels, x, y, expected",
    [
        (bitarray("10100101"), 0, 0, 1),
        (bitarray("10100101"), 3, 0, 0),
        (bitarray("10100101"), 0, 1, 0),
        (bitarray("10100101"), 3, 1, 1),
    ],
)
def test_graphics_get(pixels, x, y, expected):
    graphics = Graphics(width=4, height=2)
    graphics.pixels = pixels

    assert graphics.get(x, y) == expected


@pytest.mark.parametrize(
    "pixels, x, y, value, expected",
    [
        (bitarray(4 * 2), 0, 0, 1, "10000000"),
        (bitarray(4 * 2), 3, 0, 1, "00010000"),
        (bitarray(4 * 2), 0, 1, 1, "00001000"),
        (bitarray(4 * 2), 3, 1, 1, "00000001"),
    ],
)
def test_graphics_set(pixels, x, y, value, expected):
    graphics = Graphics(4, 2)
    graphics.pixels = pixels

    graphics.set(x, y, value)
    graphics.pixels == expected


@pytest.mark.parametrize(
    "pixels, expected",
    [
        (bitarray("1010101001010101"), [0xAA, 0x55]),
    ],
)
def test_as_list_of_integers(pixels, expected):
    graphics = Graphics(8, 2)
    graphics.pixels = pixels

    assert graphics.as_list_of_integers() == expected


@pytest.mark.parametrize(
    "pixels, expected",
    [
        (bitarray("10100101"), "X.X.\n.X.X"),
    ],
)
def test_print(pixels, expected):
    graphics = Graphics(4, 2)
    graphics.pixels = pixels

    assert str(graphics) == expected
