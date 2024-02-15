import enum
import time
import typing
from .regs.msm7200 import *
from .common_nandregs import O1N_REGS, O1N_NANDOPS

_DEBUG_CONTROLLER = False


class NANDException(Exception):
    pass


class _BaseQCOMNANDController():
    def __init__(self, read32_func, write32_func, read8_func, write8_func, base: int = 0, page_size: int = -1):
        self._cmd_read = read32_func
        self._cmd_write = write32_func
        self._mem_read = read8_func
        self._mem_write = write8_func

        self._nfi_base = base
        self._page_size = page_size

        self._idcode = 0
        self.ecc_enabled = True

        self._prev_cfg1 = 0
        self._prev_cfg2 = 0
        self._d2_prev_cfg1 = 0
        self._d2_prev_cfg2 = 0
        self._prev_common_cfg = 0

    def read(self, page: int):
        raise NotImplementedError()

    def write(self, page: int, data: typing.Union[bytes, bytearray]):
        raise NotImplementedError()

    def erase(self, page: int):
        raise NotImplementedError()


def get_bit(ctrl: _BaseQCOMNANDController, addr: int, bits: enum.Enum):
    if _DEBUG_CONTROLLER:
        print(
            f"GB: (*({hex(addr)}) >> {bits.value[0]}) & {hex(bits.value[1])}")
    return (ctrl._cmd_read(addr) >> bits.value[0]) & bits.value[1]


def set_bit(ctrl: _BaseQCOMNANDController, addr: int, bits: enum.Enum, value: int):
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


class MSM6250_6800_NANDOPS(enum.Enum):
    RESET = 0
    PAGE_READ = 1
    FLAG_READ = 2
    PAGE_WRITE = 3
    BLOCK_ERASE = 4
    ID_FETCH = 5
    STATUS_CHECK = 6
    RESET_NAND = 7


class MSM6250_NANDREGS(enum.Enum):
    FLASH_BUFFER = 0x0
    FLASH_CMD = 0x300
    FLASH_ADDR = 0x304
    FLASH_STATUS = 0x308
    FLASH_CFG1 = 0x31C
    FLASH_SPARE_DATA = 0x320


class MSM6550_NANDREGS(enum.Enum):
    FLASH_BUFFER = 0x0
    FLASH_CMD = 0x300
    FLASH_ADDR = 0x304
    FLASH_STATUS = 0x308
    FLASH_CFG1 = 0x31C
    FLASH_CFG2 = 0x320
    FLASH_SPARE_DATA = 0x324


class MSM6250_MSM6800_NANDADDR_BITS_MASK(enum.Enum):
    SPARE_AREA_BYTE_ADDRESS = (0, 0x3f)
    FLASH_PAGE_ADDRESS = (9, 0x7fffff)


class MSM6250_MSM6800_NANDCMD_BITS_MASK(enum.Enum):
    OP_CMD = (0, 0x7)
    SW_CMD_EN = (3, 0x1)
    SW_CMD_VAL = (4, 0xff)
    SW_CMD_ADDR_SEL = (12, 0x1)
    SW_CMD1_REPLACE = (13, 0x1)
    SW_CMD2_REPLACE = (14, 0x1)


class MSM6250_NANDSTATUS_BITS_MASK(enum.Enum):
    OP_STATUS = (0, 0x7)
    OP_ERR = (3, 0x1)
    CORRECTABLE_ERROR = (4, 0x1)
    READY_BUSY_N = (5, 0x1)
    ECC_SELF_ERR = (6, 0x1)
    WRITE_OP_RESULT = (7, 0x1)
    OP_FAILURE = (0, 0x88)
    READY_BUSY_N_STATUS = (13, 0x1)
    WRITE_PROTECT = (14, 0x1)
    NAND_DEVID = (15, 0xff)
    NAND_MFRID = (23, 0xff)
    READ_ERROR = (31, 0x1)


class MSM6250_NANDCFG_BITS_MASK(enum.Enum):
    ECC_DISABLED = (0, 0x1)
    BUSFREE_SUPPORT_SELECT = (1, 0x1)
    ECC_HALT_DIS = (2, 0x1)
    CLK_HALT_DIS = (3, 0x1)
    WIDE_NAND = (5, 0x1)
    BUFFER_MEM_WRITE_WAIT = (6, 0x1)
    ECC_ERR_SELF_DETECT = (7, 0x1)
    NAND_RECOVERY_CYCLE = (8, 0x7)


class MSM6550_NANDCFG2_BITS_MASK(enum.Enum):
    ID_RD_SETUP = (0, 0x1f)
    RD_SETUP = (5, 0x1f)
    RD_ACTIVE = (10, 0x1f)
    WR_HOLD = (15, 0x1f)
    WR_ACTIVE = (20, 0x1f)
    WR_SETUP = (25, 0x1f)


class MSM6250NANDController(_BaseQCOMNANDController):
    def __init__(self, read32_func, write32_func, read8_func, write8_func, base: int = 0x64000000, page_size: int = 0, nand_int_clr_addr: int = 0x8400024c, nand_int_addr: int = 0x84000244, nand_op_reset_flag: int = 6, skip_init: bool = False, msm6550_discrepancy: bool = False):
        if page_size != 0:
            raise ValueError(
                "MSM6100/6125/6250/6300/6500/6550 only supports small block NAND")
        super().__init__(read32_func, write32_func, read8_func, write8_func, base, page_size)
        self._nand_int_clr_addr = nand_int_clr_addr
        self._nand_int_addr = nand_int_addr
        self._nand_reset_op = nand_op_reset_flag
        self._skip_reg_init = skip_init
        self._msm6500_discrepancy = msm6550_discrepancy

        if not self._skip_reg_init:
            self._cmd_write(0x84000174, 0)
            self._cmd_write(0x84000178, 0x7e)
            self._cmd_write(0x8400017c, 0x1fff)
            self._cmd_write(0x84000180, 0)

        self._prev_cfg1 = self._cmd_read(
            self._nfi_base + MSM6250_NANDREGS.FLASH_CFG1.value)

        if not self._skip_reg_init:
            self._cmd_write(self._nfi_base +
                            MSM6250_NANDREGS.FLASH_CFG1.value, 0x253)
        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD.value,
                        MSM6250_6800_NANDOPS.RESET_NAND.value)

        while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS.value, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD.value,
                        MSM6250_6800_NANDOPS.ID_FETCH.value)

        while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS.value, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD.value,
                        MSM6250_6800_NANDOPS.STATUS_CHECK.value)

        while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS.value, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._idcode = (get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS.value, MSM6250_NANDSTATUS_BITS_MASK.NAND_MFRID)
                        << 24) | (get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS.value, MSM6250_NANDSTATUS_BITS_MASK.NAND_DEVID) << 16)

        self._page_width = 0
        self._reset_first = False

    def read(self, page: int):
        if not self._reset_first:
            self._reset_first = True
            if not self._skip_reg_init:
                self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD.value,
                                MSM6250_6800_NANDOPS.RESET.value)

                while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS.value, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
                    time.sleep(0.05)

            self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD.value,
                            MSM6250_6800_NANDOPS.RESET_NAND.value)

            while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS.value, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
                time.sleep(0.05)

            if not self._skip_reg_init:
                self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CFG1.value,
                                0x25a | (0 if self.ecc_enabled else 1) | (self._page_width << MSM6250_NANDCFG_BITS_MASK.WIDE_NAND.value[0]))
            else:
                set_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_CFG1.value,
                        MSM6250_NANDCFG_BITS_MASK.ECC_DISABLED, (0 if self.ecc_enabled else 1))

                set_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_CFG1.value,
                        MSM6250_NANDCFG_BITS_MASK.WIDE_NAND, self._page_width)

        set_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_ADDR.value,
                MSM6250_MSM6800_NANDADDR_BITS_MASK.FLASH_PAGE_ADDRESS, page)

        if self._nand_int_clr_addr != -1 and self._nand_int_addr != -1:
            self._cmd_write(self._nand_int_clr_addr, self._nand_reset_op)
            while (self._cmd_read(self._nand_int_addr) & self._nand_reset_op) != 0:
                pass

        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD.value,
                        MSM6250_6800_NANDOPS.PAGE_READ.value)

        while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS.value, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            pass

        if self._msm6500_discrepancy:
            if self._page_width == 1:
                return self._mem_read(self._nfi_base + MSM6250_NANDREGS.FLASH_BUFFER.value + 2, 0x200), self._mem_read(self._nfi_base + MSM6250_NANDREGS.FLASH_BUFFER.value + 0x202, 0xe) + b"\xff\xff", self._mem_read(self._nfi_base + MSM6250_NANDREGS.FLASH_BUFFER.value, 0x2)

            else:
                return self._mem_read(self._nfi_base + MSM6250_NANDREGS.FLASH_BUFFER.value + 1, 0x200), self._mem_read(self._nfi_base + MSM6250_NANDREGS.FLASH_BUFFER.value + 0x201, 0xf) + b"\xff", self._mem_read(self._nfi_base + MSM6250_NANDREGS.FLASH_BUFFER.value, 0x1)

        else:
            return self._mem_read(self._nfi_base + MSM6250_NANDREGS.FLASH_BUFFER.value, 0x200), self._mem_read(self._nfi_base + MSM6250_NANDREGS.FLASH_BUFFER.value + 0x200, 0x10), b""


class MSM6800_NANDREGS(enum.Enum):
    FLASH_BUFFER = 0x0
    FLASH_ADDR = 0x300
    FLASH_CMD = 0x304
    FLASH_STATUS = 0x308
    FLASH_COMMON_CFG = 0x31C
    FLASH_ID_DATA = 0x320
    FLASH_SPARE_DATA = 0x324
    FLASH_CFG1_FLASH1 = 0x328
    FLASH_CFG1_FLASH2 = 0x32c
    FLASH_CFG2_FLASH1 = 0x330
    FLASH_CFG2_FLASH2 = 0x334


class MSM6800_NANDSTATUS_BITS_MASK(enum.Enum):
    OP_STATUS = (0, 0x7)
    OP_ERR = (3, 0x1)
    CORRECTABLE_ERROR = (4, 0x1)
    READY_BUSY_N = (5, 0x1)
    ECC_SELF_ERR = (6, 0x1)
    WRITE_OP_RESULT = (7, 0x1)
    OP_FAILURE = (0, 0x88)
    READY_BUSY_N_STATUS = (13, 0x1)
    WRITE_PROTECT = (14, 0x1)
    NAND_AUTOPROBE_DONE = (15, 0x1)
    NAND_AUTOPROBE_ISLARGE = (16, 0x1)
    NAND_AUTOPROBE_IS16BIT = (17, 0x1)
    READ_ERROR = (31, 0x1)


class MSM6800_NANDCOMMONCFG_BITS_MASK(enum.Enum):
    BUFFER_MEM_WRITE_WAIT = (0, 0x1)
    ECC_ERR_SELF_DETECT = (1, 0x1)
    ECC_HALT_DIS = (2, 0x1)
    CLK_HALT_DIS = (3, 0x1)
    NAND_SEL = (4, 0x1)
    DM_EN = (5, 0x1)
    NAND_AUTOPROBE = (6, 0x1)


class NAND_EXTID_BITS():
    NAND_PAGESIZE = (0, 0x7)
    NAND_BLOCKSIZE = (4, 0x7)


class MSM6800_NANDFLASHID_BITS_MASK(enum.Enum):
    NAND_DEVID = (0, 0xff)
    NAND_MFRID = (8, 0xff)
    NAND_EXTID = (16, 0xff)


class MSM6800_NANDCFG1_BITS_MASK(enum.Enum):
    ECC_DISABLED = (0, 0x1)
    BUSFREE_SUPPORT_SELECT = (1, 0x1)
    NAND_SIZE = (2, 0xf)
    PAGE_IS_2KB = (6, 0x1)
    WIDE_NAND = (7, 0x1)
    NAND_RECOVERY_CYCLE = (8, 0x7)


class MSM6800_NANDCFG2_BITS_MASK(enum.Enum):
    ID_RD_HOLD = (0, 0x1f)
    RD_HOLD = (5, 0x1f)
    RD_SETUP = (10, 0x1f)
    WR_HOLD = (15, 0x1f)
    WR_SETUP = (20, 0x1f)
    WR_CS_SETUP = (25, 0x1f)


class MSM6800NANDController(_BaseQCOMNANDController):
    def __init__(self, read32_func, write32_func, read8_func, write8_func, base: int = 0x60000000, page_size: int = -1, skip_init: bool = False, skip_gpio_init: bool = False, devid: int = 0, nand_int_clr_addr: int = 0x80000414, nand_int_addr: int = 0x80000488, nand_op_reset_flag: int = 2, custom_cfg1: int = -1, custom_cfg2: int = -1, custom_common_cfg: int = -1, force_autoprobe: bool = False):
        super().__init__(read32_func, write32_func, read8_func, write8_func, base, page_size)

        self._nand_int_clr_addr = nand_int_clr_addr
        self._nand_int_addr = nand_int_addr
        self._nand_reset_op = nand_op_reset_flag
        self._skip_reg_init = skip_init
        self._skip_gpio_init = skip_gpio_init
        self._device_id = devid

        if not self._skip_gpio_init:
            for i in range(8):
                self._cmd_write(0x80000900 + (i * 4), 0xffffffff)

        self._prev_cfg1 = self._cmd_read(
            self._nfi_base + MSM6800_NANDREGS.FLASH_CFG1_FLASH1.value)

        self._prev_cfg2 = self._cmd_read(
            self._nfi_base + MSM6800_NANDREGS.FLASH_CFG2_FLASH1.value)

        self._d2_prev_cfg1 = self._cmd_read(
            self._nfi_base + MSM6800_NANDREGS.FLASH_CFG1_FLASH2.value)

        self._d2_prev_cfg2 = self._cmd_read(
            self._nfi_base + MSM6800_NANDREGS.FLASH_CFG2_FLASH2.value)

        self._prev_common_cfg = self._cmd_read(
            self._nfi_base + MSM6800_NANDREGS.FLASH_COMMON_CFG.value)

        if not self._skip_reg_init:
            self._cmd_write(self._nfi_base +
                            MSM6800_NANDREGS.FLASH_CFG1_FLASH1.value, 0xa2)

            self._cmd_write(self._nfi_base +
                            MSM6800_NANDREGS.FLASH_CFG1_FLASH2.value, 0x22)

        self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD.value,
                        MSM6250_6800_NANDOPS.RESET_NAND.value)

        while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS.value, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD.value,
                        MSM6250_6800_NANDOPS.ID_FETCH.value)

        while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS.value, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD.value,
                        MSM6250_6800_NANDOPS.STATUS_CHECK.value)

        while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS.value, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._idcode = (get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_ID_DATA.value, MSM6800_NANDFLASHID_BITS_MASK.NAND_MFRID) << 24) | (get_bit(self, self._nfi_base +
                                                                                                                                                         MSM6800_NANDREGS.FLASH_ID_DATA.value, MSM6800_NANDFLASHID_BITS_MASK.NAND_DEVID) << 16) | get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_ID_DATA.value, MSM6800_NANDFLASHID_BITS_MASK.NAND_EXTID)
        if get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS.value, MSM6800_NANDSTATUS_BITS_MASK.NAND_AUTOPROBE_DONE) != 0 or force_autoprobe:
            self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_COMMON_CFG.value,
                            1 << MSM6800_NANDCOMMONCFG_BITS_MASK.NAND_AUTOPROBE.value[0])
            self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD.value,
                            MSM6250_6800_NANDOPS.PAGE_READ.value)

            while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS.value, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
                time.sleep(0.05)

        if self._page_size == -1:
            self._page_size = get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS.value,
                                      MSM6800_NANDSTATUS_BITS_MASK.NAND_AUTOPROBE_ISLARGE)

        self._page_width = get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS.value,
                                   MSM6800_NANDSTATUS_BITS_MASK.NAND_AUTOPROBE_IS16BIT)

        self._set_common_cfg = custom_common_cfg if custom_common_cfg != -1 else 0x3
        self._set_cfg2 = custom_cfg2 if custom_cfg2 != -1 else 0x4219442
        self._set_cfg1 = custom_cfg1 if custom_cfg1 != -1 else (0xa | (self._page_size << MSM6800_NANDCFG1_BITS_MASK.PAGE_IS_2KB.value[0]) | (
            self._page_width << MSM6800_NANDCFG1_BITS_MASK.WIDE_NAND.value[0]) | (get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS.value, MSM6800_NANDSTATUS_BITS_MASK.NAND_AUTOPROBE_DONE) << 31))

        if self._skip_reg_init:
            self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_COMMON_CFG.value,
                            self._prev_common_cfg)

        self._reset_first = False

    def read(self, page: int):
        if not self._reset_first:
            self._reset_first = True
            if not self._skip_reg_init:
                self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD.value,
                                MSM6250_6800_NANDOPS.RESET.value)

                while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS.value, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
                    time.sleep(0.05)

            self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD.value,
                            MSM6250_6800_NANDOPS.RESET_NAND.value)

            while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS.value, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
                time.sleep(0.05)

            if not self._skip_reg_init:
                self._cmd_write(
                    self._nfi_base + MSM6800_NANDREGS.FLASH_COMMON_CFG.value, self._set_common_cfg)
                self._cmd_write(self._nfi_base +
                                MSM6800_NANDREGS.FLASH_CFG1_FLASH1.value, self._set_cfg1)
                self._cmd_write(self._nfi_base +
                                MSM6800_NANDREGS.FLASH_CFG1_FLASH2.value, self._set_cfg1)
                self._cmd_write(self._nfi_base +
                                MSM6800_NANDREGS.FLASH_CFG2_FLASH1.value, self._set_cfg2)
                self._cmd_write(self._nfi_base +
                                MSM6800_NANDREGS.FLASH_CFG2_FLASH2.value, self._set_cfg2)

            set_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_CFG1_FLASH1.value,
                    MSM6800_NANDCFG1_BITS_MASK.ECC_DISABLED, (0 if self.ecc_enabled else 1))

            set_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_CFG1_FLASH2.value,
                    MSM6800_NANDCFG1_BITS_MASK.ECC_DISABLED, (0 if self.ecc_enabled else 1))

        set_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_ADDR.value,
                MSM6250_MSM6800_NANDADDR_BITS_MASK.FLASH_PAGE_ADDRESS, page)

        self._cmd_write(self._nand_int_clr_addr, self._nand_reset_op)
        while (self._cmd_read(self._nand_int_addr) & self._nand_reset_op) != 0:
            pass

        tempbuf = bytearray()
        tempbuf_spare = bytearray()

        for _ in range(4 if self._page_size == 1 else 1):
            self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD.value,
                            MSM6250_6800_NANDOPS.PAGE_READ.value)

            while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS.value, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
                pass

            tempbuf += self._mem_read(self._nfi_base +
                                      MSM6800_NANDREGS.FLASH_BUFFER.value, 0x200)
            tempbuf_spare += self._mem_read(self._nfi_base +
                                            MSM6800_NANDREGS.FLASH_BUFFER.value + 0x200, 0x10)

        return bytes(tempbuf), bytes(tempbuf_spare), b""


class MSM7200_JTAGTAPCONTROL_BITS_MASK(enum.Enum):
    MODE = (0, 0xf)


class MSM7200_JTAGTAPCONTROL_VALUES(enum.Enum):
    ARM9 = 0
    ARM9_11 = 1
    ARM11 = 4
    ARM9_11_RTCK = 9


class MSM7200_JTAGNANDMPU_BITS_MASK(enum.Enum):
    ENABLE_NAND_MPU = (0, 0x1)


class MSM7200_JTAGNANDMPU_VALUES(enum.Enum):
    DISABLE_NAND_MPU = 0
    ENABLE_NAND_MPU = 1


class MSM7200_NANDREGS(enum.Enum):
    FLASH_CMD = 0x0000
    ADDR0 = 0x0004
    ADDR1 = 0x0008
    FLASH_CHIP_SELECT = 0x000C
    EXEC_CMD = 0x0010
    FLASH_STATUS = 0x0014
    BUFFER_STATUS = 0x0018
    SFLASHC_STATUS = 0x001C
    DEV0_CFG0 = 0x0020
    DEV0_CFG1 = 0x0024
    DEV0_ECC_CFG = 0x0028
    DEV1_ECC_CFG = 0x002C
    DEV1_CFG0 = 0x0030
    DEV1_CFG1 = 0x0034
    SFLASHC_CMD = 0x0038
    SFLASHC_EXEC_CMD = 0x003C
    READ_ID = 0x0040
    READ_STATUS = 0x0044
    CONFIG_DATA = 0x0050
    CONFIG = 0x0054
    CONFIG_MODE = 0x0058
    CONFIG_STATUS = 0x0060
    MACRO1_REG = 0x0064
    XFR_STEP1 = 0x0070
    XFR_STEP2 = 0x0074
    XFR_STEP3 = 0x0078
    XFR_STEP4 = 0x007C
    XFR_STEP5 = 0x0080
    XFR_STEP6 = 0x0084
    XFR_STEP7 = 0x0088
    GENP_REG0 = 0x0090
    GENP_REG1 = 0x0094
    GENP_REG2 = 0x0098
    GENP_REG3 = 0x009C
    DEV_CMD0 = 0x00A0
    DEV_CMD1 = 0x00A4
    DEV_CMD2 = 0x00A8
    DEV_CMD_VLD = 0x00AC
    EBI2_MISR_SIG_REG = 0x00B0
    ADDR2 = 0x00C0
    ADDR3 = 0x00C4
    ADDR4 = 0x00C8
    ADDR5 = 0x00CC
    DEV_CMD3 = 0x00D0
    DEV_CMD4 = 0x00D4
    DEV_CMD5 = 0x00D8
    DEV_CMD6 = 0x00DC
    SFLASHC_BURST_CFG = 0x00E0
    ADDR6 = 0x00E4
    EBI2_ECC_BUF_CFG = 0x00F0
    HW_INFO = 0x00FC
    FLASH_BUFFER = 0x0100
    NAND_MPU_ENABLE = 0x100000


class MSM7200_NANDOPS(enum.Enum):
    RESET = 0x01
    PAGE_READ = 0x32
    PAGE_READ_ECC = 0x33
    PAGE_READ_ALL = 0x34
    SEQ_PAGE_READ = 0x15
    PRG_PAGE = 0x36
    PRG_PAGE_ECC = 0x37
    PRG_PAGE_ALL = 0x39
    BLOCK_ERASE = 0x3A
    FETCH_ID = 0x0B
    STATUS = 0x0C
    RESET_NAND = 0x0D


class MSM7200NANDController(_BaseQCOMNANDController):
    def __init__(self, read32_func, write32_func, read8_func, write8_func, base: int = 0xa0a00000, page_size: int = -1, devid: int = 0, skip_init: bool = False, custom_cfg1: int = -1, custom_cfg2: int = -1, bb_in_data: bool = False, raise_on_autoprobe_fail: bool = True):
        super().__init__(read32_func, write32_func, read8_func, write8_func, base, page_size)
        self._skip_reg_init = skip_init
        self._bb_in_data = bb_in_data
        self._cfg1 = custom_cfg1
        self._cfg2 = custom_cfg2
        self._device_id = devid

        self._prev_cfg1 = self._cmd_read(
            self._nfi_base + MSM7200_NANDREGS.DEV0_CFG0.value)

        self._prev_cfg2 = self._cmd_read(
            self._nfi_base + MSM7200_NANDREGS.DEV0_CFG1.value)

        self._d2_prev_cfg1 = self._cmd_read(
            self._nfi_base + MSM7200_NANDREGS.DEV1_CFG0.value)

        self._d2_prev_cfg2 = self._cmd_read(
            self._nfi_base + MSM7200_NANDREGS.DEV1_CFG1.value)

        if not self._skip_reg_init:
            self._cmd_write(
                self._nfi_base + MSM7200_NANDREGS.DEV0_CFG0.value, 0xaad400da)  # Reset 1
            self._cmd_write(
                self._nfi_base + MSM7200_NANDREGS.DEV0_CFG1.value, 0x44747c)  # Reset 2
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.DEV_CMD_VLD.value, 0xd)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.DEV_CMD0.value, 0x1080d060)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.DEV_CMD1.value, 0xf00f3000)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.DEV_CMD2.value, 0xf0ff7090)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.DEV_CMD3.value, 0xf0ff7090)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.DEV_CMD4.value, 0x800000)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.DEV_CMD5.value, 0xf30094)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.DEV_CMD6.value, 0x40e0)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.FLASH_CHIP_SELECT.value, devid)

        self._send_cmd(MSM7200_NANDOPS.RESET.value)
        self._send_cmd(MSM7200_NANDOPS.RESET_NAND.value)

        self._cmd_write(self._nfi_base + MSM7200_NANDREGS.ADDR0.value, 0x0)
        self._cmd_write(self._nfi_base + MSM7200_NANDREGS.ADDR1.value, 0x0)

        self._send_cmd((4 << MSM7200_NAND_FLASH_CMD_BITS_MASK.AUTO_DETECT_DATA_XFR_SIZE.value[0]) | (1 << MSM7200_NAND_FLASH_CMD_BITS_MASK.AUTO_DETECT.value[0]) | (1 << MSM7200_NAND_FLASH_CMD_BITS_MASK.LAST_PAGE.value[0]) | (
            1 << MSM7200_NAND_FLASH_CMD_BITS_MASK.PAGE_ACC.value[0]) | (MSM7200_NAND_FLASH_CMD_OP_CMD_VALUES.PAGE_READ.value << MSM7200_NAND_FLASH_CMD_BITS_MASK.OP_CMD.value[0]))

        if get_bit(self, self._nfi_base + MSM7200_NANDREGS.FLASH_STATUS.value, MSM7200_NAND_FLASH_STATUS_BITS_MASK.OP_ERR) or not get_bit(self, self._nfi_base + MSM7200_NANDREGS.FLASH_STATUS.value, MSM7200_NAND_FLASH_STATUS_BITS_MASK.AUTO_DETECT_DONE):
            if raise_on_autoprobe_fail:
                raise NANDException("NAND autoprobe failed")

        if self._page_size == -1:
            self._page_size = get_bit(self, self._nfi_base + MSM7200_NANDREGS.FLASH_STATUS.value,
                                      MSM7200_NAND_FLASH_STATUS_BITS_MASK.FIELD_2KBYTE_DEVICE)

        self._send_cmd(MSM7200_NANDOPS.FETCH_ID.value)
        self._page_width = 0
        tempIDCode = self._cmd_read(
            self._nfi_base + MSM7200_NANDREGS.READ_ID.value)

        self._idcode = 0
        for i in range(4):
            self._idcode <<= 8
            self._idcode |= ((tempIDCode >> (i * 8)) & 0xff)

        self._isFirst = False
        self._reset_first = False

    def _send_cmd(self, cmd_no: int):
        self._cmd_write(self._nfi_base +
                        MSM7200_NANDREGS.FLASH_CMD.value, cmd_no)
        self._cmd_write(self._nfi_base + MSM7200_NANDREGS.EXEC_CMD.value, 1)
        while get_bit(self, self._nfi_base + MSM7200_NANDREGS.FLASH_STATUS.value, MSM7200_NAND_FLASH_STATUS_BITS_MASK.OPER_STATUS) != 0:
            pass

    def read(self, page: int):
        if not self._isFirst:
            self._isFirst = True
            if self._cfg1 == -1 or self._cfg2 == -1:
                self._cfg1 = 0xaad400da
                self._cfg2 = 0x44747c

                self._cfg2 = set_bit_var(self._cfg2,
                                         MSM7200_NAND_DEV_CFG1_BITS_MASK.WIDE_FLASH, self._page_width)
                self._cfg1 = set_bit_var(self._cfg1,
                                         MSM7200_NAND_DEV_CFG0_BITS_MASK.CW_PER_PAGE, 3 if self._page_size == 1 else 0)
                if self._bb_in_data:
                    self._cfg2 = set_bit_var(self._cfg2,
                                             MSM7200_NAND_DEV_CFG1_BITS_MASK.BAD_BLOCK_BYTE_NUM, 0x1d1)
                    self._cfg2 = set_bit_var(self._cfg2,
                                             MSM7200_NAND_DEV_CFG1_BITS_MASK.BAD_BLOCK_IN_SPARE_AREA, 0x0)
                elif not self._bb_in_data and self._page_width == 0:
                    self._cfg2 = set_bit_var(self._cfg2,
                                             MSM7200_NAND_DEV_CFG1_BITS_MASK.BAD_BLOCK_BYTE_NUM, 0x6)
                    self._cfg2 = set_bit_var(self._cfg2,
                                             MSM7200_NAND_DEV_CFG1_BITS_MASK.BAD_BLOCK_IN_SPARE_AREA, 0x1)
                elif not self._bb_in_data and self._page_width == 1:
                    self._cfg2 = set_bit_var(self._cfg2,
                                             MSM7200_NAND_DEV_CFG1_BITS_MASK.BAD_BLOCK_BYTE_NUM, 0x1)
                    self._cfg2 = set_bit_var(self._cfg2,
                                             MSM7200_NAND_DEV_CFG1_BITS_MASK.BAD_BLOCK_IN_SPARE_AREA, 0x1)

                if _DEBUG_CONTROLLER:
                    print(f":-CFG1: {hex(self._cfg1)}")
                    print(f":-CFG2: {hex(self._cfg2)}")

        if not self._reset_first:
            self._reset_first = True

            if not self._skip_reg_init:
                self._send_cmd(MSM7200_NANDOPS.RESET.value)
            self._send_cmd(MSM7200_NANDOPS.RESET_NAND.value)

            if not self._skip_reg_init:
                self._cmd_write(self._nfi_base +
                                MSM7200_NANDREGS.DEV0_CFG0.value, self._cfg1)
                self._cmd_write(self._nfi_base +
                                MSM7200_NANDREGS.DEV0_CFG1.value, self._cfg2)
                self._cmd_write(self._nfi_base +
                                MSM7200_NANDREGS.DEV1_CFG0.value, self._cfg1)
                self._cmd_write(self._nfi_base +
                                MSM7200_NANDREGS.DEV1_CFG1.value, self._cfg2)
                self._cmd_write(self._nfi_base +
                                MSM7200_NANDREGS.DEV_CMD_VLD.value, 0xd)

            set_bit(self, self._nfi_base + MSM7200_NANDREGS.DEV0_CFG1.value,
                    MSM7200_NAND_DEV_CFG1_BITS_MASK.ECC_DISABLE, (0 if self.ecc_enabled else 1))
            set_bit(self, self._nfi_base + MSM7200_NANDREGS.DEV1_CFG1.value,
                    MSM7200_NAND_DEV_CFG1_BITS_MASK.ECC_DISABLE, (0 if self.ecc_enabled else 1))

        temp_addr = page << (16 if self._page_size == 1 else 8)
        self._cmd_write(self._nfi_base +
                        MSM7200_NANDREGS.ADDR0.value, temp_addr & 0xffffffff)
        self._cmd_write(self._nfi_base + MSM7200_NANDREGS.ADDR1.value,
                        (temp_addr >> 32) & 0xffffffff)

        self._cmd_write(self._nfi_base +
                        MSM7200_NANDREGS.FLASH_CMD.value, MSM7200_NANDOPS.PAGE_READ_ALL.value)

        tempbuf = bytearray()
        tempbuf_spare = bytearray()
        tempbuf_bbm = bytearray()

        for _ in range(4 if self._page_size == 1 else 1):
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.EXEC_CMD.value, 1)
            while get_bit(self, self._nfi_base + MSM7200_NANDREGS.FLASH_STATUS.value, MSM7200_NAND_FLASH_STATUS_BITS_MASK.OPER_STATUS) != 0:
                pass

            temp_mem = self._mem_read(self._nfi_base +
                                      MSM7200_NANDREGS.FLASH_BUFFER.value, 0x210)

            if self._bb_in_data:
                tempbuf += temp_mem[:0x1d0] + temp_mem[0x1d2:0x202]
                tempbuf_bbm += temp_mem[0x1d0:0x1d2]
                tempbuf_spare += temp_mem[0x202:] + b"\xff\xff"

            else:
                tempbuf += temp_mem[:0x200]
                tempbuf_spare += temp_mem[0x200:]

        return bytes(tempbuf), bytes(tempbuf_spare), bytes(tempbuf_bbm)


class MSM7200OneNANDController(_BaseQCOMNANDController):
    def __init__(self, read32_func, write32_func, read8_func, write8_func, base: int = 0xa0a00000, page_size: int = 0, skip_init: bool = False, custom_cfg1: int = -1, custom_cfg2: int = -1):
        super().__init__(read32_func, write32_func, read8_func, write8_func, base, page_size)

        self._skip_reg_init = skip_init
        self._cfg1 = custom_cfg1
        self._cfg2 = custom_cfg2

        self._prev_cfg1 = self._cmd_read(
            self._nfi_base + MSM7200_NANDREGS.DEV0_CFG0.value)

        self._prev_cfg2 = self._cmd_read(
            self._nfi_base + MSM7200_NANDREGS.DEV0_CFG1.value)

        self._d2_prev_cfg1 = self._cmd_read(
            self._nfi_base + MSM7200_NANDREGS.DEV1_CFG0.value)

        self._d2_prev_cfg2 = self._cmd_read(
            self._nfi_base + MSM7200_NANDREGS.DEV1_CFG1.value)

        if not self._skip_reg_init:
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.DEV0_CFG0.value, 0xaad4001a)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.DEV0_CFG1.value, 0x2101bd)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.DEV_CMD_VLD.value, 0xd)
            self._cmd_write(
                self._nfi_base + MSM7200_NANDREGS.SFLASHC_BURST_CFG.value, 0x20100327)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.XFR_STEP1.value, 0x47804780)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.XFR_STEP2.value, 0x39003a0)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.XFR_STEP3.value, 0x3b008a8)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.XFR_STEP4.value, 0x9b488a0)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.XFR_STEP5.value, 0x89a2c420)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.XFR_STEP6.value, 0xc420c020)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.XFR_STEP7.value, 0xc020c020)
            self._cmd_write(self._nfi_base +
                            MSM7200_NANDREGS.FLASH_CHIP_SELECT.value, 0x0)

        self._regwrite(O1N_REGS.REG_SYS_CFG1, 0x40c0)
        self._regwrite(O1N_REGS.REG_START_ADDRESS1, 0x0)
        self._regwrite(O1N_REGS.REG_START_ADDRESS2, 0x0)
        self._regwrite(O1N_REGS.REG_INTERRUPT, 0x0)

        self._regwrite(O1N_REGS.REG_COMMAND, O1N_NANDOPS.HOT_RESET.value)
        while (self._regread(O1N_REGS.REG_INTERRUPT) & 0x8000) != 0x8000:
            time.sleep(0.1)

        self._idcode = (self._regread(O1N_REGS.REG_MANUFACTURER_ID)
                        << 24) | (self._regread(O1N_REGS.REG_DEVICE_ID) << 16)
        self._ddp = bool(self._regread(O1N_REGS.REG_DEVICE_ID) & 8)

        density_raw = (self._regread(O1N_REGS.REG_DEVICE_ID) >> 4) & 0xf

        self._density = 2 << ((5 if self._ddp else 6) + density_raw)

    def _cmdexec(self):
        while self._cmd_read(self._nfi_base + MSM7200_NANDREGS.SFLASHC_EXEC_CMD.value) & 0x1:
            pass

        self._cmd_write(self._nfi_base +
                        MSM7200_NANDREGS.SFLASHC_EXEC_CMD.value, 1)

        while self._cmd_read(self._nfi_base + MSM7200_NANDREGS.SFLASHC_EXEC_CMD.value) & 0x1:
            pass

    def _regwrite(self, offset: O1N_REGS, reg: int):
        self._cmd_write(self._nfi_base +
                        MSM7200_NANDREGS.ADDR0.value, (offset.value) >> 1)
        self._cmd_write(self._nfi_base + MSM7200_NANDREGS.GENP_REG0.value, reg)

        self._cmd_write(
            self._nfi_base + MSM7200_NANDREGS.SFLASHC_CMD.value, 3 | (1 << 20) | 0x30)
        self._cmdexec()

        while get_bit(self, self._nfi_base + MSM7200_NANDREGS.SFLASHC_STATUS.value, MSM7200_NAND_FLASH_STATUS_BITS_MASK.OPER_STATUS) != 0:
            pass

    def _regread(self, offset: O1N_REGS):
        self._cmd_write(self._nfi_base +
                        MSM7200_NANDREGS.ADDR0.value, (offset.value) >> 1)

        self._cmd_write(
            self._nfi_base + MSM7200_NANDREGS.SFLASHC_CMD.value, 2 | (1 << 20) | 0x10)
        self._cmdexec()

        while get_bit(self, self._nfi_base + MSM7200_NANDREGS.SFLASHC_STATUS.value, MSM7200_NAND_FLASH_STATUS_BITS_MASK.OPER_STATUS) != 0:
            pass

        return self._cmd_read(self._nfi_base + MSM7200_NANDREGS.GENP_REG0.value)

    def _nandtobuf(self, offset: O1N_REGS, size: int):
        temp = bytearray()
        curOffset = offset.value

        assert (size & 1) == 0
        assert (offset.value & 1) == 0

        while size > 0:
            readSize = min(512, size)

            self._cmd_write(self._nfi_base + MSM7200_NANDREGS.MACRO1_REG.value, curOffset >> 1)
            self._cmd_write(
                self._nfi_base + MSM7200_NANDREGS.SFLASHC_CMD.value, 6 | ((readSize >> 1) << 20) | 0x10)
            self._cmdexec()

            while get_bit(self, self._nfi_base + MSM7200_NANDREGS.SFLASHC_STATUS.value, MSM7200_NAND_FLASH_STATUS_BITS_MASK.OPER_STATUS) != 0:
                pass

            temp += self._mem_read(self._nfi_base + MSM7200_NANDREGS.FLASH_BUFFER.value, readSize)

            curOffset += readSize
            size -= readSize

        return bytes(temp)

    def read(self, page: int):
        if self._ecc_enabled:
            self._regwrite(O1N_REGS.REG_SYS_CFG1,
                           self._regread(O1N_REGS.REG_SYS_CFG1) & ~0x100)
        else:
            self._regwrite(O1N_REGS.REG_SYS_CFG1,
                           self._regread(O1N_REGS.REG_SYS_CFG1) | 0x100)

        self._regwrite(O1N_REGS.REG_INTERRUPT, 0x0)
        self._regwrite(O1N_REGS.REG_ECC_STATUS, 0x0)
        self._regwrite(O1N_REGS.REG_START_BUFFER, 0x800)

        UPPER_BANK = 0x8000 if self._ddp and (
            page >> 6) >= self._density else 0x0

        self._regwrite(O1N_REGS.REG_START_ADDRESS1,
                       UPPER_BANK | ((page >> 6) & (self._density - 1)))
        self._regwrite(O1N_REGS.REG_START_ADDRESS2, UPPER_BANK)

        self._regwrite(O1N_REGS.REG_START_ADDRESS8, (page & 63) << 2)
        self._regwrite(O1N_REGS.REG_COMMAND, O1N_NANDOPS.READ.value)

        while (self._regread(O1N_REGS.REG_INTERRUPT) & 0x8080) != 0x8080:
            pass

        return self._nandtobuf(O1N_REGS.DATARAM, 0x800 if self._page_size == 0 else 0x1000), self._nandtobuf(O1N_REGS.SPARERAM, 0x40 if self._page_size == 0 else 0x80), b""


def _moduletest():
    global _DEBUG_CONTROLLER
    _DEBUG_CONTROLLER = True

    def dummy_cmd_read(offset):
        print(f"CMD READ {hex(offset)}")
        return 0x0

    def dummy_cmd_write(offset, value):
        print(f"CMD WRITE {hex(offset)} {hex(value)} {bin(value)}")

    def dummy_mem_read(offset, size):
        print(f"MEM READ {hex(offset)} {hex(size)}")
        return b"\xff"*size

    def dummy_mem_write(offset, data):
        print(f"MEM WRITE {hex(offset)} {data}")
        pass

    print("6250")
    test = MSM6250NANDController(
        dummy_cmd_read, dummy_cmd_write, dummy_mem_read, dummy_mem_write)
    print("-READ")
    print(test.read(8))

    print("6275")
    test = MSM6800NANDController(
        dummy_cmd_read, dummy_cmd_write, dummy_mem_read, dummy_mem_write, force_autoprobe=True)
    print("-READ")
    print(test.read(8))

    print("7200")
    test = MSM7200NANDController(
        dummy_cmd_read, dummy_cmd_write, dummy_mem_read, dummy_mem_write, raise_on_autoprobe_fail=False)
    print("-READ")
    print(test.read(8))

    print("7200_BBM")
    test = MSM7200NANDController(
        dummy_cmd_read, dummy_cmd_write, dummy_mem_read, dummy_mem_write, raise_on_autoprobe_fail=False, bb_in_data=True)
    print("-READ")
    print(test.read(8))

    print("7200_O1N")
    test = MSM7200OneNANDController(
        dummy_cmd_read, dummy_cmd_write, dummy_mem_read, dummy_mem_write)
    print("-READ_BUF")
    print(test._nandtobuf(O1N_REGS.DATARAM, 0x800))
