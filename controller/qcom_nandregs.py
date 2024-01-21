import enum
import time


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
        self._prev_common_cfg = 0

    def read(self, offset: int, size: int):
        raise NotImplementedError()

    def write(self, offset: int, size: int):
        raise NotImplementedError()

    def erase(self, offset: int, size: int):
        raise NotImplementedError()


def get_bit(ctrl: _BaseQCOMNANDController, addr: int, bits):
    return (ctrl._cmd_read(addr) >> bits[0]) & bits[1]


def set_bit(ctrl: _BaseQCOMNANDController, addr: int, bits, value: int):
    bitMask = bits[1] << bits[0]
    ctrl._cmd_write((ctrl._cmd_read(addr) & ~bitMask) | value & bits[1])


class MSM6250_6800_NANDOPS(enum.Enum):
    RESET = 0,
    PAGE_READ = 1,
    FLAG_READ = 2,
    PAGE_WRITE = 3,
    BLOCK_ERASE = 4,
    ID_FETCH = 5,
    STATUS_CHECK = 6,
    RESET_NAND = 7


class MSM6250_NANDREGS(enum.Enum):
    FLASH_BUFFER = 0x0,
    FLASH_CMD = 0x300,
    FLASH_ADDR = 0x304,
    FLASH_STATUS = 0x308,
    FLASH_CFG1 = 0x31C,
    FLASH_SPARE_DATA = 0x320


class MSM6550_NANDREGS(enum.Enum):
    FLASH_BUFFER = 0x0,
    FLASH_CMD = 0x300,
    FLASH_ADDR = 0x304,
    FLASH_STATUS = 0x308,
    FLASH_CFG1 = 0x31C,
    FLASH_CFG2 = 0x320,
    FLASH_SPARE_DATA = 0x324


class MSM6250_MSM6800_NANDADDR_BITS_MASK(enum.Enum):
    SPARE_AREA_BYTE_ADDRESS = (0, 0x3f),
    FLASH_PAGE_ADDRESS = (9, 0x7fffff)


class MSM6250_MSM6800_NANDCMD_BITS_MASK(enum.Enum):
    OP_CMD = (0, 0x7),
    SW_CMD_EN = (3, 0x1),
    SW_CMD_VAL = (4, 0x8),
    SW_CMD_ADDR_SEL = (12, 0x1),
    SW_CMD1_REPLACE = (13, 0x1),
    SW_CMD2_REPLACE = (14, 0x1)


class MSM6250_NANDSTATUS_BITS_MASK(enum.Enum):
    OP_STATUS = (0, 0x7),
    OP_ERR = (3, 0x1),
    CORRECTABLE_ERROR = (4, 0x1),
    READY_BUSY_N = (5, 0x1),
    ECC_SELF_ERR = (6, 0x1),
    WRITE_OP_RESULT = (7, 0x1),
    OP_FAILURE = (0, 0x88),
    READY_BUSY_N_STATUS = (13, 0x1),
    WRITE_PROTECT = (14, 0x1),
    NAND_DEVID = (15, 0x8),
    NAND_MFRID = (23, 0x8),
    READ_ERROR = (31, 0x1)


class MSM6250_NANDCFG_BITS_MASK(enum.Enum):
    ECC_DISABLED = (0, 0x1),
    BUSFREE_SUPPORT_SELECT = (1, 0x1),
    ECC_HALT_DIS = (2, 0x1),
    CLK_HALT_DIS = (3, 0x1),
    WIDE_NAND = (5, 0x1),
    BUFFER_MEM_WRITE_WAIT = (6, 0x1),
    ECC_ERR_SELF_DETECT = (7, 0x1),
    NAND_RECOVERY_CYCLE = (8, 0x7)


class MSM6250NANDController(_BaseQCOMNANDController):
    def __init__(self, read32_func, write32_func, read8_func, write8_func, base: int = 0x64000000, page_size: int = 0, nand_int_clr_addr: int = 0x8400024c, nand_int_addr: int = 0x84000244, nand_op_reset_flag: int = 6):
        if page_size != 0:
            raise ValueError(
                "MSM6100/6125/6250/6300/6500/6550 only supports small block NAND")
        super().__init__(read32_func, write32_func, read8_func, write8_func, base, page_size)
        self._nand_int_clr_addr = nand_int_clr_addr
        self._nand_int_addr = nand_int_addr
        self._nand_reset_op = nand_op_reset_flag

        self._cmd_write(0x84000174, 0)
        self._cmd_write(0x84000178, 0x7e)
        self._cmd_write(0x8400017c, 0x1fff)
        self._cmd_write(0x84000180, 0)

        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CFG1, 0x253)
        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD,
                        MSM6250_6800_NANDOPS.RESET_NAND)

        while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD,
                        MSM6250_6800_NANDOPS.ID_FETCH)

        while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD,
                        MSM6250_6800_NANDOPS.STATUS_CHECK)

        while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._idcode = (get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS, MSM6250_NANDSTATUS_BITS_MASK.NAND_MFRID)
                        << 24) | (get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS, MSM6250_NANDSTATUS_BITS_MASK.NAND_DEVID) << 16)

    def read(self, offset: int, size: int):
        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD,
                        MSM6250_6800_NANDOPS.RESET)

        while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD,
                        MSM6250_6800_NANDOPS.RESET_NAND)

        while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CFG1,
                        0x25a | (0 if self.ecc_enabled else 1))
        set_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_ADDR,
                MSM6250_MSM6800_NANDADDR_BITS_MASK.FLASH_PAGE_ADDRESS, offset >> 9)

        self._cmd_write(self._nand_int_clr_addr, self._nand_reset_op)
        while (self._cmd_read(self._nand_int_addr) & self._nand_reset_op) != 0:
            time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD,
                        MSM6250_6800_NANDOPS.PAGE_READ)

        while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        return self._mem_read(self._nfi_base + MSM6250_NANDREGS.FLASH_BUFFER), self._mem_read(self._nfi_base + MSM6250_NANDREGS.FLASH_BUFFER + 0x210)

    def write(self, offset: int, size: int):
        raise NotImplementedError()

    def erase(self, offset: int, size: int):
        raise NotImplementedError()

class MSM6800_NANDSTATUS_BITS_MASK(enum.Enum):
    OP_STATUS = (0, 0x7),
    OP_ERR = (3, 0x1),
    CORRECTABLE_ERROR = (4, 0x1),
    READY_BUSY_N = (5, 0x1),
    ECC_SELF_ERR = (6, 0x1),
    WRITE_OP_RESULT = (7, 0x1),
    OP_FAILURE = (0, 0x88),
    READY_BUSY_N_STATUS = (13, 0x1),
    WRITE_PROTECT = (14, 0x1),
    NAND_AUTOPROBE_MUSTBE0 = (15, 0x1),
    NAND_AUTORPOBE_ISLARGE = (16, 0x1),
    NAND_AUTOPROBE_IS16BIT = (17, 0x1),
    READ_ERROR = (31, 0x1)
