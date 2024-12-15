import pytest
from bitarray import bitarray
from bitarray.util import ba2int

from chip8emulator.graphics import Graphics


def test_graphics_clear():
    graphics = Graphics()
    graphics.clear()

    assert all(ba2int(line) == 0 for line in graphics.pixels)


@pytest.mark.parametrize(
    "pixels, x, y, expected",
    [
        ([bitarray("1000"), bitarray("0000")], 0, 0, 1),
        ([bitarray("0001"), bitarray("0000")], 3, 0, 1),
        ([bitarray("0000"), bitarray("1000")], 0, 1, 1),
        ([bitarray("0000"), bitarray("0001")], 3, 1, 1),
    ],
)
def test_graphics_get(pixels, x, y, expected):
    graphics = Graphics(width=4, height=2)
    graphics.pixels = pixels

    assert graphics.get(x, y) == expected


@pytest.mark.parametrize(
    "pixels",
    [
        [
            bitarray("0000 0001 0010 0011"),
            bitarray("0100 0101 0110 0111"),
            bitarray("1000 1001 1010 1011"),
            bitarray("1100 1101 1110 1111"),
        ],
    ],
)
@pytest.mark.parametrize(
    "x, y, expected",
    [
        (0, 0, ba2int(bitarray("0000 0001"))),
        (12, 0, ba2int(bitarray("0011 0000"))),
        (0, 3, ba2int(bitarray("1100 1101"))),
        (12, 3, ba2int(bitarray("1111 1100"))),
        (15, 3, ba2int(bitarray("1110 0110"))),
    ],
)
def test_graphics_get_byte(pixels, x, y, expected):
    graphics = Graphics(16, 4)
    graphics.pixels = pixels

    assert graphics.get_byte(x, y) == expected


@pytest.mark.parametrize(
    "x, y, value, expected",
    [
        (0, 0, 1, [bitarray("1000"), bitarray("0000")]),
        (3, 0, 1, [bitarray("0001"), bitarray("0000")]),
        (0, 1, 1, [bitarray("0000"), bitarray("1000")]),
        (3, 1, 1, [bitarray("0000"), bitarray("0001")]),
    ],
)
def test_graphics_set(x, y, value, expected):
    graphics = Graphics(4, 2)

    graphics.set(x, y, value)
    assert graphics.pixels == expected


@pytest.mark.parametrize(
    "x, y, value, expected",
    [
        (
            0,
            0,
            0xFF,
            [
                bitarray("1111 1111 0000 0000"),
                bitarray("0" * 16),
                bitarray("0" * 16),
                bitarray("0" * 16),
            ],
        ),
        (
            12,
            0,
            0xAB,
            [
                bitarray("1011 0000 0000 1010"),
                bitarray("0" * 16),
                bitarray("0" * 16),
                bitarray("0" * 16),
            ],
        ),
        (
            4,
            1,
            0xFF,
            [
                bitarray("0" * 16),
                bitarray("0000 1111 1111 0000"),
                bitarray("0" * 16),
                bitarray("0" * 16),
            ],
        ),
        (
            14,
            3,
            0xAB,
            [
                bitarray("0" * 16),
                bitarray("0" * 16),
                bitarray("0" * 16),
                bitarray("1010 1100 0000 0010"),
            ],
        ),
    ],
)
def test_graphics_set_byte(x, y, value, expected):
    graphics = Graphics(width=16, height=4)

    graphics.set_byte(x, y, value)
    assert graphics.pixels == expected


def test_assert_raises():
    graphics = Graphics(4, 2)

    with pytest.raises(IndexError):
        graphics.set(4, 2, 1)
        graphics.set_byte(4, 2, 1)
        graphics.get(4, 2)
        graphics.get_byte(4, 2)

    with pytest.raises(ValueError):
        graphics.set_byte(0, 0, 200)
        graphics.set(0, 0, 2)


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
        (
            [
                bitarray("10100101"),
                bitarray("11110000"),
            ],
            "\n".join(
                [
                    "X.X..X.X",
                    "XXXX....",
                ]
            ),
        ),
    ],
)
def test_print(pixels, expected):
    graphics = Graphics(4, 2)
    graphics.pixels = pixels

    assert str(graphics) == expected
