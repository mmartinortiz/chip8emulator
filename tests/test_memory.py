import pytest

from chip8emulator.memory import Memory


def test_validate_address():
    size = 4096
    memory = Memory(size=size)
    with pytest.raises(ValueError):
        memory._validate_address(address=size + 1)

    assert memory._validate_address(address=0)
    assert memory._validate_address(address=size)


@pytest.mark.parametrize(
    "size, address, value",
    [
        (4096, 80, b"\x77"),
        (4096, 80, 0x77),
        (4096, 160, 0x0A),
    ],
)
def test_get_set_item(size, address, value):
    memory = Memory(size=size)

    memory[address] = value
    assert memory[address] == value


@pytest.mark.parametrize("value", [0x100, b"\x00\x01"])
def test_set_exception(value):
    memory = Memory()
    with pytest.raises(ValueError):
        memory[0] = value
