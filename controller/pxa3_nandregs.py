import typing
import enum
from .regs import pxa3

_DEBUG_CONTROLLER = False


class PXA3NANDController():
    def __init__(self, u32_read, u32_write, arbiter: bool = False, page_size: int = -1, page_width: int = -1, devid: int = 0):
        self._cmd_read = u32_read
        self._cmd_write = u32_write
        self._arbiter = arbiter
        self.ecc_enabled = True

        self._page_width = page_width
        self._page_size = page_size

        prev_ndcr = self._cmd_read(0x43100000 + pxa3.PXA3NANDREGS.NDCR.value)

        ndcr = (prev_ndcr & ~0x70000000) | (
            1 << pxa3.PXA3NDCR_BITS_MASK.NDCR_SPARE_EN.value[0])

        ndcr = set_bit_var(
            ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_RD_ID_CNT, 4 if self._page_size in [-1, 1] else 2)
        ndcr = set_bit_var(
            ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_ND_ARB_EN, int(self._arbiter))

        ndcr = set_bit_var(
            ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_RA_START, 1 if self._page_size in [-1, 1] else 0)
        ndcr = set_bit_var(
            ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_PG_PER_BLK, 1 if self._page_size == 1 else 0)

        ndcr = set_bit_var(
            ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_PAGE_SZ, 1 if self._page_size in [-1, 1] else 0)

        ndcr = set_bit_var(
            ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_DWIDTH_C, 1 if self._page_width == 1 else 0)
        ndcr = set_bit_var(
            ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_DWIDTH_M, 1 if self._page_width == 1 else 0)

        self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDCR.value, ndcr)

        self._pxa_reset()
        self._idcode = self._pxa_read_id()

        self._reset_first = False

    def _pxa_start(self):
        self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDSR.value, 0xfff)
        set_bit(self, 0x43100000 + pxa3.PXA3NANDREGS.NDCR.value,
                pxa3.PXA3NDCR_BITS_MASK.NDCR_ECC_EN, int(self.ecc_enabled))
        set_bit(self, 0x43100000 + pxa3.PXA3NANDREGS.NDCR.value,
                pxa3.PXA3NDCR_BITS_MASK.NDCR_ND_RUN, 1)

        while get_bit(self, 0x43100000 + pxa3.PXA3NANDREGS.NDSR.value, pxa3.PXA3NDSR_BITS_MASK.NDSR_WRCMDREQ) == 0:
            pass

    def _pxa_end(self):
        set_bit(self, 0x43100000 + pxa3.PXA3NANDREGS.NDCR.value,
                pxa3.PXA3NDCR_BITS_MASK.NDCR_ND_RUN, 0)

    def _pxa_reset(self):
        self._pxa_start()

        self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDCB0.value,
                        0xff | (5 << pxa3.PXA3NDCB_BITS_MASK.NDCB0_CMD_TYPE.value[0]))
        self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDCB1.value, 0x00)
        self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDCB2.value, 0x00)

        while get_bit(self, 0x43100000 + pxa3.PXA3NANDREGS.NDSR.value, pxa3.PXA3NDSR_BITS_MASK.NDSR_CS0_CMDD) == 0:
            pass

        for _ in range(0x4000):
            if get_bit(self, 0x43100000 + pxa3.PXA3NANDREGS.NDSR.value, pxa3.PXA3NDSR_BITS_MASK.NDSR_RDY) != 0:
                break

        self._pxa_end()

    def _pxa_read_id(self):
        self._pxa_start()

        self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDCB0.value,
                        0x90 | (3 << pxa3.PXA3NDCB_BITS_MASK.NDCB0_CMD_TYPE.value[0]))
        self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDCB1.value, 0x00)
        self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDCB2.value, 0x00)

        while get_bit(self, 0x43100000 + pxa3.PXA3NANDREGS.NDSR.value, pxa3.PXA3NDSR_BITS_MASK.NDSR_RDDREQ) == 0:
            pass

        idcode = 0
        for _ in range(4):
            idcode <<= 8
            idcode |= self._cmd_read(
                0x43100000 + pxa3.PXA3NANDREGS.NDDB.value) & 0xff

        self._pxa_end()

        return idcode

    def _pxa_read_start(self, page: int):
        self._pxa_start()

        if self._page_size == 1:
            temp_addr = page << 16

            self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDCB0.value, 0x3000 | (
                5 << pxa3.PXA3NDCB_BITS_MASK.NDCB0_ADDR_CYC.value[0]) | (1 << pxa3.PXA3NDCB_BITS_MASK.NDCB0_DBC.value[0]))
            self._cmd_write(
                0x43100000 + pxa3.PXA3NANDREGS.NDCB1.value, temp_addr & 0xffffffff)
            self._cmd_write(
                0x43100000 + pxa3.PXA3NANDREGS.NDCB2.value, (temp_addr >> 32) & 0xff)

        else:
            self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDCB0.value,
                            0x00 | (4 << pxa3.PXA3NDCB_BITS_MASK.NDCB0_ADDR_CYC.value[0]))
            self._cmd_write(
                0x43100000 + pxa3.PXA3NANDREGS.NDCB1.value, (page << 8) & 0xffffffff)
            self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDCB2.value, 0x00)

        while get_bit(self, 0x43100000 + pxa3.PXA3NANDREGS.NDSR.value, pxa3.PXA3NDSR_BITS_MASK.NDSR_RDDREQ) == 0:
            pass

    def read(self, page: int):
        if not self._reset_first:
            self._reset_first = True

            prev_ndcr = self._cmd_read(
                0x43100000 + pxa3.PXA3NANDREGS.NDCR.value)
            ndcr = (prev_ndcr & ~0x70000000) | (
                1 << pxa3.PXA3NDCR_BITS_MASK.NDCR_SPARE_EN.value[0])

            ndcr = set_bit_var(
                ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_RD_ID_CNT, 4 if self._page_size == 1 else 2)
            ndcr = set_bit_var(
                ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_ND_ARB_EN, int(self._arbiter))

            ndcr = set_bit_var(
                ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_RA_START, self._page_size)
            ndcr = set_bit_var(
                ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_PG_PER_BLK, self._page_size)

            ndcr = set_bit_var(
                ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_PAGE_SZ, self._page_size)

            ndcr = set_bit_var(
                ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_DWIDTH_C, self._page_width)
            ndcr = set_bit_var(
                ndcr, pxa3.PXA3NDCR_BITS_MASK.NDCR_DWIDTH_M, self._page_width)

            self._cmd_write(0x43100000 + pxa3.PXA3NANDREGS.NDCR.value, ndcr)

            self._pxa_reset()

        self._pxa_read_start(page)

        tempBuf = bytearray()
        tempSpare = bytearray()

        if self._page_size == 1:
            for _ in range(0x200):
                temp = self._cmd_read(0x43100000 + pxa3.PXA3NANDREGS.NDDB.value[0])
                for _ in range(4):
                    tempBuf.append(temp & 0xff)
                    temp >>= 8

            for _ in range(0x10):
                temp = self._cmd_read(0x43100000 + pxa3.PXA3NANDREGS.NDDB.value[0])
                for _ in range(4):
                    tempSpare.append(temp & 0xff)
                    temp >>= 8

        else:
            for _ in range(0x80):
                temp = self._cmd_read(0x43100000 + pxa3.PXA3NANDREGS.NDDB.value[0])
                for _ in range(4):
                    tempBuf.append(temp & 0xff)
                    temp >>= 8

            for _ in range(0x4):
                temp = self._cmd_read(0x43100000 + pxa3.PXA3NANDREGS.NDDB.value[0])
                for _ in range(4):
                    tempSpare.append(temp & 0xff)
                    temp >>= 8

        self._pxa_end()

        return tempBuf, tempSpare, b""

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
