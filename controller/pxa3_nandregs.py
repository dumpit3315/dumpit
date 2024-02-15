import typing
import enum

_DEBUG_CONTROLLER = False

class PXA3NANDController():
    def __init__(self, u32_read, u32_write, arbiter: bool=False, page_size: int=-1, devid: int=0):
        self._cmd_read = u32_read
        self._cmd_write = u32_write
        self._arbiter = arbiter

        ndcr = 0
        #ndcr |= 


    def read(self, page: int):
        raise NotImplementedError()

    def write(self, page: int, data: typing.Union[bytes, bytearray]):
        raise NotImplementedError()

    def erase(self, page: int):
        raise NotImplementedError()

def get_bit(ctrl: PXA3NANDController, addr: int, bits: enum.Enum):
    if _DEBUG_CONTROLLER:
        print(
            f"GB: (*({hex(addr)}) >> {bits.value[0]}) & {hex(bits.value[1])}")
    return (ctrl._cmd_read(addr) >> bits.value[0]) & bits.value[1]


def set_bit(ctrl: PXA3NANDController, addr: int, bits: enum.Enum, value: int):
    bitMask = bits.value[1] << bits.value[0]
    if _DEBUG_CONTROLLER:
        print(
            f"SB: (*({hex(addr)}) & ~{hex(bitMask)}) | (({hex(value)} & {hex(bits.value[1])}) << {bits.value[0]})")
    ctrl._cmd_write(addr, (ctrl._cmd_read(addr) & ~bitMask)
                    | ((value & bits.value[1]) << bits.value[0]))