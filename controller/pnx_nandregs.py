import typing
import enum
from .regs import pnx

_DEBUG_CONTROLLER = False


class PNX6NANDController():
    def __init__(self, u32_read, u32_write, base_offset: int = 0xc1300000, page_size: int = 0, page_width: int = 0):
        self._cmd_read = u32_read
        self._cmd_write = u32_write

        self._page_size = page_size
        self._page_width = page_width

        self._idcode = 0
        self.ecc_enabled = True

        self._base_offset = base_offset

        '''
        prev_cfg = self._cmd_read(
            self._base_offset + pnx.PNXNANDREGS.CONFIG.value)

        cfg = prev_cfg | (self._page_width << pnx.PNXNAND_CFG_BITS_MASK.WIDTH.value[0]) | (
            int(self.ecc_enabled) << pnx.PNXNAND_CFG_BITS_MASK.ECC.value[0])
        self._cmd_write(self._base_offset + pnx.PNXNANDREGS.CONFIG.value, cfg)
        '''

        set_bit(self, self._base_offset + pnx.PNXNANDREGS.CONFIG.value,
                pnx.PNXNAND_CFG_BITS_MASK.WIDTH, self._page_width)
        set_bit(self, self._base_offset + pnx.PNXNANDREGS.CONFIG.value,
                pnx.PNXNAND_CFG_BITS_MASK.ECC, self.ecc_enabled)

        self._cmd_write(self._base_offset + pnx.PNXNANDREGS.CMD.value, 0xff)
        self._cmd_write(self._base_offset + pnx.PNXNANDREGS.CMD.value, 0x90)
        self._cmd_write(self._base_offset + pnx.PNXNANDREGS.ADDR.value, 0x0)

        self._isFirst = True
        self._idcode = 0

        for _ in range(4):
            self._idcode <<= 8
            self._idcode |= (self._cmd_read(
                self._base_offset + pnx.PNXNANDREGS.DATA.value) & 0xff)

        self._cmd_write(self._base_offset + pnx.PNXNANDREGS.CMD.value, 0xff)

    def read(self, page: int):
        tempData = bytearray()
        tempSpare = bytearray()

        if self._isFirst:
            self._isFirst = False
            set_bit(self, self._base_offset + pnx.PNXNANDREGS.CONFIG.value,
                    pnx.PNXNAND_CFG_BITS_MASK.WIDTH, self._page_width)
            set_bit(self, self._base_offset + pnx.PNXNANDREGS.CONFIG.value,
                    pnx.PNXNAND_CFG_BITS_MASK.ECC, self.ecc_enabled)

        if self._page_size == 0:
            if self._page_width == 0:
                ''' First read '''
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.CMD.value, 0x00)

                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, 0x00)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, page & 0xff)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, (page >> 8) & 0xff)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, (page >> 16) & 0xff)

                if not _DEBUG_CONTROLLER:
                    while get_bit(self, self._base_offset + pnx.PNXNANDREGS.STAT.value, pnx.PNXNAND_STAT_BITS_MASK.RDY) == pnx.PNXNAND_STAT_VALUES.RDY_NOT_READY:
                        pass

                for _ in range(0x100):
                    tempData.append(self._cmd_read(
                        self._base_offset + pnx.PNXNANDREGS.DATA.value))

                ''' Second read '''
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.CMD.value, 0x01)

                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, 0x00)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, page & 0xff)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, (page >> 8) & 0xff)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, (page >> 16) & 0xff)

                if not _DEBUG_CONTROLLER:
                    pass  # Wait placeholder

                for _ in range(0x100):
                    tempData.append(self._cmd_read(
                        self._base_offset + pnx.PNXNANDREGS.DATA.value))

                ''' Spare read '''
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.CMD.value, 0x50)

                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, 0x00)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, page & 0xff)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, (page >> 8) & 0xff)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, (page >> 16) & 0xff)

                if not _DEBUG_CONTROLLER:
                    pass  # Wait placeholder

                for _ in range(0x10):
                    tempSpare.append(self._cmd_read(
                        self._base_offset + pnx.PNXNANDREGS.DATA.value))

            else:
                ''' First read '''
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.CMD.value, 0x00)

                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, 0x00)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, page & 0xff)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, (page >> 8) & 0xff)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, (page >> 16) & 0xff)

                if not _DEBUG_CONTROLLER:
                    while get_bit(self, self._base_offset + pnx.PNXNANDREGS.STAT.value, pnx.PNXNAND_STAT_BITS_MASK.RDY) == pnx.PNXNAND_STAT_VALUES.RDY_NOT_READY:
                        pass

                for _ in range(0x100):
                    tempData += self._cmd_read(self._base_offset +
                                               pnx.PNXNANDREGS.DATA.value).to_bytes(2, "little")

                ''' Spare read '''
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.CMD.value, 0x50)

                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, 0x00)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, page & 0xff)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, (page >> 8) & 0xff)
                self._cmd_write(self._base_offset +
                                pnx.PNXNANDREGS.ADDR.value, (page >> 16) & 0xff)

                if not _DEBUG_CONTROLLER:
                    pass  # Wait placeholder

                for _ in range(0x8):
                    tempSpare += self._cmd_read(self._base_offset +
                                                pnx.PNXNANDREGS.DATA.value).to_bytes(2, "little")

        else:
            self._cmd_write(self._base_offset +
                            pnx.PNXNANDREGS.CMD.value, 0x00)

            self._cmd_write(self._base_offset +
                            pnx.PNXNANDREGS.ADDR.value, 0x00)
            self._cmd_write(self._base_offset +
                            pnx.PNXNANDREGS.ADDR.value, 0x00)
            self._cmd_write(self._base_offset +
                            pnx.PNXNANDREGS.ADDR.value, page & 0xff)
            self._cmd_write(self._base_offset +
                            pnx.PNXNANDREGS.ADDR.value, (page >> 8) & 0xff)
            self._cmd_write(self._base_offset +
                            pnx.PNXNANDREGS.ADDR.value, (page >> 16) & 0xff)

            self._cmd_write(self._base_offset +
                            pnx.PNXNANDREGS.CMD.value, 0x30)

            if not _DEBUG_CONTROLLER:
                while get_bit(self, self._base_offset + pnx.PNXNANDREGS.STAT.value, pnx.PNXNAND_STAT_BITS_MASK.RDY) == pnx.PNXNAND_STAT_VALUES.RDY_NOT_READY:
                    pass

            if self._page_width == 0:
                for _ in range(0x800):
                    tempData.append(self._cmd_read(
                        self._base_offset + pnx.PNXNANDREGS.DATA.value))

                for _ in range(0x40):
                    tempSpare.append(self._cmd_read(
                        self._base_offset + pnx.PNXNANDREGS.DATA.value))

            else:
                for _ in range(0x400):
                    tempData += self._cmd_read(self._base_offset +
                                               pnx.PNXNANDREGS.DATA.value).to_bytes(2, "little")

                for _ in range(0x20):
                    tempSpare += self._cmd_read(self._base_offset +
                                                pnx.PNXNANDREGS.DATA.value).to_bytes(2, "little")

        return bytes(tempData), bytes(tempSpare), b""


def get_bit(ctrl: PNX6NANDController, addr: int, bits: enum.Enum):
    if _DEBUG_CONTROLLER:
        print(
            f"GB: (*({hex(addr)}) >> {bits.value[0]}) & {hex(bits.value[1])}")
    return (ctrl._cmd_read(addr) >> bits.value[0]) & bits.value[1]


def set_bit(ctrl: PNX6NANDController, addr: int, bits: enum.Enum, value: int):
    bitMask = bits.value[1] << bits.value[0]
    if _DEBUG_CONTROLLER:
        print(
            f"SB: (*({hex(addr)}) & ~{hex(bitMask)}) | (({hex(value)} & {hex(bits.value[1])}) << {bits.value[0]})")
    ctrl._cmd_write(addr, (ctrl._cmd_read(addr) & ~bitMask)
                    | ((value & bits.value[1]) << bits.value[0]))


'''
def get_bit_var(var: int, bits: enum.Enum):
    if _DEBUG_CONTROLLER:
        print(f"GBV: ({hex(var)} >> {bits.value[0]}) & {hex(bits.value[1])}")
    return (var >> bits.value[0]) & bits.value[1]


def set_bit_var(var: int, bits: enum.Enum, value: int):
    bitMask = bits.value[1] << bits.value[0]
    if _DEBUG_CONTROLLER:
        print(
            f"SBV: ({hex(var)} & ~{hex(bitMask)}) | (({hex(value)} & {hex(bits.value[1])}) << {bits.value[0]})")
    return (var & ~bitMask) | ((value & bits.value[1]) << bits.value[0])
'''


def _moduletest():
    global _DEBUG_CONTROLLER
    _DEBUG_CONTROLLER = True

    def dummy_cmd_read(offset):
        print(f"CMD READ {hex(offset)}")
        return 0x0

    def dummy_cmd_write(offset, value):
        print(f"CMD WRITE {hex(offset)} {hex(value)} {bin(value)}")

    print("-PNX 512-")
    test = PNX6NANDController(
        dummy_cmd_read, dummy_cmd_write, 0xc1300000, 0, 0)
    print("-READ-")
    print(test.read(0))

    print("-PNX 2048-")
    test = PNX6NANDController(
        dummy_cmd_read, dummy_cmd_write, 0xc1300000, 1, 0)
    print("-READ-")
    print(test.read(0))
