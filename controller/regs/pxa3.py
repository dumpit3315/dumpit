import enum


class PXA3NANDREGS(enum.Enum):
    NDCR = 0x00
    NDTR0CS0 = 0x04
    NDTR1CS0 = 0x0C
    NDSR = 0x14
    NDPCR = 0x18
    NDBDR0 = 0x1C
    NDBDR1 = 0x20
    NDECCCTRL = 0x28
    NDDB = 0x40
    NDCB0 = 0x48
    NDCB1 = 0x4C
    NDCB2 = 0x50


class PXA3NDCR_BITS_MASK(enum.Enum):
    NDCR_SPARE_EN = (31, 0x1)
    NDCR_ECC_EN = (30, 0x1)
    NDCR_DMA_EN = (29, 0x1)
    NDCR_ND_RUN = (28, 0x1)
    NDCR_DWIDTH_C = (27, 0x1)
    NDCR_DWIDTH_M = (26, 0x1)
    NDCR_PAGE_SZ = (24, 0x1)
    NDCR_NCSX = (23, 0x1)
    NDCR_CLR_PG_CNT = (20, 0x1)
    NDCR_STOP_ON_UNCOR = (19, 0x1)
    NDCR_RD_ID_CNT = (16, 0x7)
    NDCR_RA_START = (15, 0x1)
    NDCR_PG_PER_BLK = (14, 0x1)
    NDCR_ND_ARB_EN = (12, 0x1)
    NDCR_INTERRUPT = (0, 0xfff)


class PXA3NDSR_BITS_MASK(enum.Enum):
    NDSR_MASK = (0, 0xfff)
    NDSR_RDY = (12, 0x1)
    NDSR_FLASH_RDY = (11, 0x1)
    NDSR_CS0_PAGED = (10, 0x1)
    NDSR_CS1_PAGED = (9, 0x1)
    NDSR_CS0_CMDD = (8, 0x1)
    NDSR_CS1_CMDD = (7, 0x1)
    NDSR_CS0_BBD = (6, 0x1)
    NDSR_CS1_BBD = (5, 0x1)
    NDSR_UNCORERR = (4, 0x1)
    NDSR_CORERR = (3, 0x1)
    NDSR_WRDREQ = (2, 0x1)
    NDSR_RDDREQ = (1, 0x1)
    NDSR_WRCMDREQ = (0, 0x1)


class PXA3NDCB_BITS_MASK(enum.Enum):
    NDCB0_LEN_OVRD = (28, 0x1)
    NDCB0_ST_ROW_EN = (26, 0x1)
    NDCB0_AUTO_RS = (25, 0x1)
    NDCB0_CSEL = (24, 0x1)
    NDCB0_EXT_CMD_TYPE = (29, 0x7)
    NDCB0_CMD_TYPE = (21, 0x7)
    NDCB0_NC = (20, 0x1)
    NDCB0_DBC = (19, 0x1)
    NDCB0_ADDR_CYC = (16, 0x7)
    NDCB0_CMD2 = (8, 0xff)
    NDCB0_CMD1 = (0, 0xff)
