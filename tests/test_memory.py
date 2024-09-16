import pytest

from chip8emulator.memory import Memory


def test_validate_address():
    size = 4096
    memory = Memory()
    with pytest.raises(ValueError):
        memory._validate_address(address=size + 1)

    assert memory._validate_address(address=0)
    assert memory._validate_address(address=size)


@pytest.mark.parametrize(
    "address, value, expected",
    [
        (80, b"\x77", int.from_bytes(b"\x77", byteorder="big")),
        (80, 0x77, 0x77),
        (160, 0x0A, 0x0A),
    ],
)
def test_get_set_item(address, value, expected):
    memory = Memory()

    memory[address] = value
    assert memory[address] == expected
