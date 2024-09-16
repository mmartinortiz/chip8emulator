from collections import UserDict


class Memory(UserDict):
    def __init__(self):
        self.size = 4096
        self.memory = [0x0] * self.size

    def _validate_address(self, address: int) -> bool:
        if 0 < address > self.size:
            raise ValueError(f"Memory address {address} is not valid")

        return True

    def __getitem__(self, address: int) -> int:
        self._validate_address(address)

        return self.memory[address]

    def __setitem__(self, address: int, value: bytes | int) -> int:
        self._validate_address(address)

        if isinstance(value, int) and value.bit_length() > 8:
            raise ValueError(f"Value too large: {value.bit_length()} bits")

        if isinstance(value, bytes):
            value = int.from_bytes(value, byteorder="big")

        self.memory[address] = value

        return self.memory[address]
