from collections import UserDict

from chip8emulator.types import Word


class Memory(UserDict):
    def __init__(self, size: int = 4096):
        self.size = size
        self.memory = [0] * size

    def _validate_address(self, address: int) -> bool:
        if 0x0000 < address > self.size:
            raise ValueError(f"Memory address {address} is not valid")

        return True

    def __getitem__(self, address: int | Word) -> int:
        if isinstance(address, Word):
            address = address.value

        self._validate_address(address)

        return self.memory[address]

    def __setitem__(self, address: int, value: bytes | int) -> int:
        self._validate_address(address)

        if isinstance(value, bytes) and len(value) > 1:
            raise ValueError(f"Value too large: {len(value)} bytes")

        if isinstance(value, int) and value.bit_length() > 8:
            raise ValueError(f"Value too large: {value.bit_length()} bits")

        self.memory[address] = value

        return self.memory[address]
