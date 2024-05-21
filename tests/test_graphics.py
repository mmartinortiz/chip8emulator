import pytest

from chip8emulator.graphics import Graphics


def test_graphics_clear():
    graphics = Graphics()
    graphics.pixels = [[1] * 64 for _ in range(32)]

    graphics.clear()

    assert all(pixel == 0 for row in graphics.pixels for pixel in row)


@pytest.mark.parametrize(
    "pixels, x, y, expected",
    [
        ([list("abcd"), list("efgh"), list("ijkl"), list("mnop")], 0, 0, "a"),
        ([list("abcd"), list("efgh"), list("ijkl"), list("mnop")], 1, 0, "b"),
        ([list("abcd"), list("efgh"), list("ijkl"), list("mnop")], 0, 1, "e"),
        ([list("abcd"), list("efgh"), list("ijkl"), list("mnop")], 1, 1, "f"),
    ],
)
def test_graphics_get(pixels, x, y, expected):
    graphics = Graphics()
    graphics.pixels = pixels

    assert graphics.get(x, y) == expected


@pytest.mark.parametrize(
    "pixels, x, y, value, expected",
    [
        (
            [list("abcd"), list("efgh"), list("ijkl"), list("mnop")],
            0,
            0,
            1,
            [[1, "b"], ["e", "f"], ["i", "j"], ["m", "n"]],
        ),
        (
            [list("abcd"), list("efgh"), list("ijkl"), list("mnop")],
            1,
            0,
            1,
            [["a", 1], ["e", "f"], ["i", "j"], ["m", "n"]],
        ),
        (
            [list("abcd"), list("efgh"), list("ijkl"), list("mnop")],
            0,
            1,
            1,
            [["a", "b"], [1, "f"], ["i", "j"], ["m", "n"]],
        ),
        (
            [list("abcd"), list("efgh"), list("ijkl"), list("mnop")],
            1,
            1,
            1,
            [["a", "b"], ["e", 1], ["i", "j"], ["m", "n"]],
        ),
    ],
)
def test_graphics_set(pixels, x, y, value, expected):
    graphics = Graphics()
    graphics.pixels = pixels

    graphics.set(x, y, value)
    graphics.pixels == expected
