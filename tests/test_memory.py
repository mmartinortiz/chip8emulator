import pytest

from chip8emulator.memory import Memory


def test_validate_address():
    size = 4096
    memory = Memory(size=size)
    with pytest.raises(ValueError):
        memory._validate_address(address=size + 1)

    assert memory._validate_address(address=0)
    assert memory._validate_address(address=size)


def test_get_set_item():
    size = 4096
    address = 80
    memory = Memory(size=size)

    value = 0x77

    memory[address] = value
    assert memory[address] == value
