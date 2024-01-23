import enum
import time
import typing


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

    def read(self, offset: int, size: int):
        raise NotImplementedError()

    def write(self, offset: int, size: int, data: typing.Union[bytes, bytearray]):
        raise NotImplementedError()

    def erase(self, offset: int, size: int):
        raise NotImplementedError()


def get_bit(ctrl: _BaseQCOMNANDController, addr: int, bits):
    return (ctrl._cmd_read(addr) >> bits[0]) & bits[1]


def set_bit(ctrl: _BaseQCOMNANDController, addr: int, bits, value: int):
    bitMask = bits[1] << bits[0]
    ctrl._cmd_write((ctrl._cmd_read(addr) & ~bitMask) | value & bits[1])


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
    SW_CMD_VAL = (4, 0x8)
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
    NAND_DEVID = (15, 0x8)
    NAND_MFRID = (23, 0x8)
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
    def __init__(self, read32_func, write32_func, read8_func, write8_func, base: int = 0x64000000, page_size: int = 0, nand_int_clr_addr: int = 0x8400024c, nand_int_addr: int = 0x84000244, nand_op_reset_flag: int = 6, skip_init: bool = False):
        if page_size != 0:
            raise ValueError(
                "MSM6100/6125/6250/6300/6500/6550 only supports small block NAND")
        super().__init__(read32_func, write32_func, read8_func, write8_func, base, page_size)
        self._nand_int_clr_addr = nand_int_clr_addr
        self._nand_int_addr = nand_int_addr
        self._nand_reset_op = nand_op_reset_flag
        self._skip_reg_init = skip_init

        if not self._skip_reg_init:
            self._cmd_write(0x84000174, 0)
            self._cmd_write(0x84000178, 0x7e)
            self._cmd_write(0x8400017c, 0x1fff)
            self._cmd_write(0x84000180, 0)

        self._prev_cfg1 = self._cmd_read(
            self._nfi_base + MSM6250_NANDREGS.FLASH_CFG1)

        if not self._skip_reg_init:
            self._cmd_write(self._nfi_base +
                            MSM6250_NANDREGS.FLASH_CFG1, 0x253)
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
        if not self._skip_reg_init:
            self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD,
                            MSM6250_6800_NANDOPS.RESET)

            while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
                time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CMD,
                        MSM6250_6800_NANDOPS.RESET_NAND)

        while get_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_STATUS, MSM6250_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        if not self._skip_reg_init:
            self._cmd_write(self._nfi_base + MSM6250_NANDREGS.FLASH_CFG1,
                            0x25a | (0 if self.ecc_enabled else 1))
        else:
            set_bit(self, self._nfi_base + MSM6250_NANDREGS.FLASH_CFG1,
                    MSM6250_NANDCFG_BITS_MASK.ECC_DISABLED, (0 if self.ecc_enabled else 1))

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
    NAND_PAGESIZE = (0, 0x3)
    NAND_BLOCKSIZE = (4, 0x3)


class MSM6800_NANDFLASHID_BITS_MASK(enum.Enum):
    NAND_DEVID = (0, 0x8)
    NAND_MFRID = (8, 0x8)
    NAND_EXTID = (16, 0x8)


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
    def __init__(self, read32_func, write32_func, read8_func, write8_func, base: int = 0x60000000, page_size: int = -1, skip_init: bool = False, skip_gpio_init: bool = False, devid: int = 0, nand_int_clr_addr: int = 0x80000414, nand_int_addr: int = 0x80000488, nand_op_reset_flag: int = 2, custom_cfg1: int = -1, custom_cfg2: int = -1, custom_common_cfg: int = -1):
        super().__init__(read32_func, write32_func, read8_func, write8_func, base, page_size)

        self._nand_int_clr_addr = nand_int_clr_addr
        self._nand_int_addr = nand_int_addr
        self._nand_reset_op = nand_op_reset_flag
        self._skip_reg_init = skip_init
        self._skip_gpio_init = skip_gpio_init
        self._device_id = devid
        self._page_size = page_size

        if not self._skip_gpio_init:
            for i in range(8):
                self._cmd_write(0x80000900 + (i * 4), 0xffffffff)

        self._prev_cfg1 = self._cmd_read(
            self._nfi_base + MSM6800_NANDREGS.FLASH_CFG1_FLASH1)

        self._prev_cfg2 = self._cmd_read(
            self._nfi_base + MSM6800_NANDREGS.FLASH_CFG2_FLASH1)

        self._d2_prev_cfg1 = self._cmd_read(
            self._nfi_base + MSM6800_NANDREGS.FLASH_CFG1_FLASH2)

        self._d2_prev_cfg2 = self._cmd_read(
            self._nfi_base + MSM6800_NANDREGS.FLASH_CFG1_FLASH2)

        self._prev_common_cfg = self._cmd_read(
            self._nfi_base + MSM6800_NANDREGS.FLASH_COMMON_CFG)

        if not self._skip_reg_init:
            self._cmd_write(self._nfi_base +
                            MSM6800_NANDREGS.FLASH_CFG1_FLASH1, 0xa2)

            self._cmd_write(self._nfi_base +
                            MSM6800_NANDREGS.FLASH_CFG1_FLASH2, 0x22)

        self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD,
                        MSM6250_6800_NANDOPS.RESET_NAND)

        while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD,
                        MSM6250_6800_NANDOPS.RESET_NAND)

        while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        self._idcode = (get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_ID_DATA, MSM6800_NANDFLASHID_BITS_MASK.NAND_MFRID) << 24) | (get_bit(self, self._nfi_base +
                                                                                                                                                   MSM6800_NANDREGS.FLASH_ID_DATA, MSM6800_NANDFLASHID_BITS_MASK.NAND_DEVID) << 16) | get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_ID_DATA, MSM6800_NANDFLASHID_BITS_MASK.NAND_EXTID)
        if get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS, MSM6800_NANDSTATUS_BITS_MASK.NAND_AUTOPROBE_DONE) != 0:
            self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_COMMON_CFG,
                            1 << MSM6800_NANDCOMMONCFG_BITS_MASK.NAND_AUTOPROBE[0])
            self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD,
                            MSM6250_6800_NANDOPS.PAGE_READ)

            while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
                time.sleep(0.05)

        if self._page_size == -1:
            self._page_size = get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS,
                                      MSM6800_NANDSTATUS_BITS_MASK.NAND_AUTOPROBE_ISLARGE)

        self._page_width = get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS,
                                   MSM6800_NANDSTATUS_BITS_MASK.NAND_AUTOPROBE_IS16BIT)

        self._set_common_cfg = custom_common_cfg if custom_common_cfg != -1 else 0x3
        self._set_cfg2 = custom_cfg2 if custom_cfg2 != -1 else 0x4219442
        self._set_cfg1 = custom_cfg1 if custom_cfg1 != -1 else (0xa | (self._page_size << MSM6800_NANDCFG1_BITS_MASK.PAGE_IS_2KB[0]) | (
            self._page_width << MSM6800_NANDCFG1_BITS_MASK.WIDE_NAND[0]) | (get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS, MSM6800_NANDSTATUS_BITS_MASK.NAND_AUTOPROBE_DONE) << 31))

        if self._skip_reg_init:
            self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_COMMON_CFG,
                            self._prev_common_cfg)

    def read(self, offset: int, size: int):
        if not self._skip_reg_init:
            self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD,
                            MSM6250_6800_NANDOPS.RESET)

            while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
                time.sleep(0.05)

        self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD,
                        MSM6250_6800_NANDOPS.RESET_NAND)

        while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
            time.sleep(0.05)

        if not self._skip_reg_init:
            self._cmd_write(
                self._nfi_base + MSM6800_NANDREGS.FLASH_COMMON_CFG, self._set_common_cfg)
            self._cmd_write(self._nfi_base +
                            MSM6800_NANDREGS.FLASH_CFG1_FLASH1, self._set_cfg1)
            self._cmd_write(self._nfi_base +
                            MSM6800_NANDREGS.FLASH_CFG1_FLASH2, self._set_cfg1)
            self._cmd_write(self._nfi_base +
                            MSM6800_NANDREGS.FLASH_CFG2_FLASH1, self._set_cfg2)
            self._cmd_write(self._nfi_base +
                            MSM6800_NANDREGS.FLASH_CFG2_FLASH2, self._set_cfg2)

        set_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_CFG1_FLASH1,
                MSM6800_NANDCFG1_BITS_MASK.ECC_DISABLED, (0 if self.ecc_enabled else 1))

        set_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_CFG1_FLASH2,
                MSM6800_NANDCFG1_BITS_MASK.ECC_DISABLED, (0 if self.ecc_enabled else 1))

        set_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_ADDR,
                MSM6250_MSM6800_NANDADDR_BITS_MASK.FLASH_PAGE_ADDRESS, (offset >> 11) if self._page_size == 1 else (offset >> 9))

        self._cmd_write(self._nand_int_clr_addr, self._nand_reset_op)
        while (self._cmd_read(self._nand_int_addr) & self._nand_reset_op) != 0:
            time.sleep(0.05)

        tempbuf = bytearray()
        tempbuf_spare = bytearray()

        for _ in range(4 if self._page_size == 1 else 1):
            self._cmd_write(self._nfi_base + MSM6800_NANDREGS.FLASH_CMD,
                            MSM6250_6800_NANDOPS.PAGE_READ)

            while get_bit(self, self._nfi_base + MSM6800_NANDREGS.FLASH_STATUS, MSM6800_NANDSTATUS_BITS_MASK.OP_STATUS) != 0:
                time.sleep(0.05)

            tempbuf += self._mem_read(self._nfi_base +
                                      MSM6800_NANDREGS.FLASH_BUFFER)
            tempbuf_spare += self._mem_read(self._nfi_base +
                                            MSM6800_NANDREGS.FLASH_BUFFER + 0x210)

        return bytes(tempbuf), bytes(tempbuf_spare)


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


class MSM7200_NANDOPS_RAW(enum.Enum):
    RESET = 1
    PAGE_READ = 2
    PAGE_READ_ECC = 3
    PAGE_READ_ALL = 4
    SEQ_PAGE_READ = 5
    PRG_PAGE = 6
    PRG_PAGE_ECC = 7
    PRG_PAGE_ALL = 9
    BLOCK_ERASE = 10
    FETCH_ID = 11
    STATUS = 12
    RESET_NAND = 13


class MSM7200_NANDFLASHCMD_BITS_MASK(enum.Enum):
    OP_CMD = (0, 4)
    PAGE_ACC = (4, 1)
    LAST_PAGE = (5, 1)
    AUTO_DETECT = (6, 1)
    AUTO_DETECT_DATA_XFR_SIZE = (7, 0x3ff)


class MSM7200NANDController(_BaseQCOMNANDController):
    def __init__(self, read32_func, write32_func, read8_func, write8_func, base: int = 0xa0a00000, page_size: int = -1, skip_init: bool = False, devid: int = 0, custom_cfg1: int = -1, custom_cfg2: int = -1, is_qsc6270: bool = False):
        super().__init__(read32_func, write32_func, read8_func, write8_func, base, page_size)

    def read(self, offset: int, size: int):
        pass
