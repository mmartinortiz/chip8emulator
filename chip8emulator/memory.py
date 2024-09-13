from collections import UserDict

from chip8emulator.types import Byte, Word


class Memory(UserDict):
    def __init__(self):
        self.size = 4096
        self.memory = [Byte(0)] * self.size

    def _validate_address(self, address: int | Word) -> bool:
        if 0x0000 < address > self.size:
            raise ValueError(f"Memory address {address} is not valid")

        return True

    def __getitem__(self, address: int | Word) -> int:
        if isinstance(address, Word):
            address = address.value

        self._validate_address(address)

        return self.memory[address]

    def __setitem__(self, address: int | Word, value: bytes | int) -> Byte:
        self._validate_address(address)

        if isinstance(value, bytes) and len(value) > 1:
            raise ValueError(f"Value too large: {len(value)} bytes")

        if isinstance(value, int) and value.bit_length() > 8:
            raise ValueError(f"Value too large: {value.bit_length()} bits")

        if isinstance(value, bytes):
            value = int.from_bytes(value, byteorder="big")

        self.memory[address] = Byte(int(value))

        return self.memory[address]
