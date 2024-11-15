from collections import UserList


class Memory(UserList):
    def __init__(self, data: list[int] = None):
        if data:
            self.data = data
        else:
            self.data = [0x0] * 4096

    def _validate_address(self, address: int) -> bool:
        if 0 < address > len(self.data):
            raise ValueError(f"Memory address {address} is not valid")

        return True

    def __getitem__(self, address: int | slice) -> int:
        if isinstance(address, slice):
            self._validate_address(address.start)
            self._validate_address(address.stop)
        else:
            self._validate_address(address)

        return self.data[address]

    def __setitem__(self, address: int, value: bytes | int) -> int:
        self._validate_address(address)

        if isinstance(value, int) and value.bit_length() > 8:
            raise ValueError(f"Value too large: {value.bit_length()} bits")

        if isinstance(value, bytes):
            value = int.from_bytes(value, byteorder="big")

        self.data[address] = value

        return self.data[address]
