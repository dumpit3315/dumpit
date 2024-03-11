import enum


class PNXNANDREGS(enum.Enum):
    DATA = 0x0
    ADDR = 0x4
    CMD = 0x8
    STOP = 0xC
    CTRL = 0x10
    CONFIG = 0x14
    STAT = 0x18
    INT_STAT = 0x1C
    IEN = 0x20
    ISR = 0x24
    ICR = 0x28
    TAC = 0x2C
    TC = 0x30
    ECC = 0x34
    DMA_DATA = 0x38
    PAGE_SIZE = 0x3C
    READY = 0x40
    TAC_READ = 0x44


class PNXNAND_CTRL_BITS_MASK(enum.Enum):
    SW_RESET = (2, 0x1)
    ECC_CLEAR = (1, 0x1)
    DMA_START = (0, 0x1)


class PNXNAND_CTRL_VALUES(enum.Enum):
    SW_RESET_0 = 0x0
    SW_RESET_1 = 0x1
    ECC_CLEAR_0 = 0x0
    ECC_CLEAR_1 = 0x1
    DMA_START_0 = 0x0
    DMA_START_1 = 0x1


class PNXNAND_CFG_BITS_MASK(enum.Enum):
    CMD_UNDER_BUSY = (7, 0x1)
    TAC_MODE = (6, 0x1)
    CE_LOW = (5, 0x1)
    DMA_ECC = (4, 0x1)
    ECC = (3, 0x1)
    DMA_BURST = (2, 0x1)
    DMA_DIR = (1, 0x1)
    WIDTH = (0, 0x1)


class PNXNAND_CFG_VALUES(enum.Enum):
    CMD_UNDER_BUSY_DISABLE = 0x0
    CMD_UNDER_BUSY_ENABLE = 0x1
    TAC_MODE_0 = 0x0
    TAC_MODE_NFI_TAC = 0x1
    CE_LOW_0 = 0x0
    CE_LOW_ALWAYS = 0x1
    DMA_ECC_0 = 0x0
    DMA_ECC_ENABLE = 0x1
    ECC_DISABLE = 0x0
    ECC_ENABLE = 0x1
    DMA_BURST_DISABLE = 0x0
    DMA_BURST_ENABLE = 0x1
    DMA_DIR_WRITE = 0x0
    DMA_DIR_READ = 0x1
    WIDTH_8_BIT = 0x0
    WIDTH_16_BIT = 0x1


class PNXNAND_STAT_BITS_MASK(enum.Enum):
    DMA_READY = (4, 1)
    IF_READY = (3, 1)
    DMA_ACTIVE = (2, 1)
    IF_ACTIVE = (1, 1)
    RDY = (0, 1)


class PNXNAND_STAT_VALUES(enum.Enum):
    DMA_READY_READY = 0x0
    DMA_READY_NOT_READY = 0x1
    IF_READY_READY = 0x0
    IF_READY_NOT_READY = 0x1
    DMA_ACTIVE_NOT_ACTIVE = 0x0
    DMA_ACTIVE_ACTIVE = 0x1
    IF_ACTIVE_NOT_ACTIVE = 0x0
    IF_ACTIVE_ACTIVE = 0x1
    RDY_NOT_READY = 0x0
    RDY_READY = 0x1


class PNXNAND_INTERRUPT_BITS_MASK(enum.Enum):
    TCZINT = (1, 0x1)
    RDYINT = (0, 0x1)


class PNXNAND_TAC_BITS_MASK(enum.Enum):  # Those were multipled by 10
    BUSY = (12, 0xF)  # WE to Busy (0xf means 0x100)
    WI = (8, 0xF)  # WE/RE Pulse Width (usually 25us)
    HO = (4, 0xF)  # Data Hold
    SU = (0, 0xF)  # Data Setup

# A210
# 0401
