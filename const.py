DUMPIT_VERSION = "0.9"

_interfaces = [
    (
        "FT232R",
        "adapter driver ft232r; ft232r vid_pid (FT232R_VID) (FT232R_PID); ft232r restore_serial (FT232R_RESTORE_SERIAL); (FT232R_PINS);",
    ),
    (
        "FT232H",
        "adapter driver ftdi; ftdi vid_pid (FT232H_VID) (FT232H_PID); ftdi layout_init (FT232H_PINS) (FT232H_DIR); (FT232H_LAYOUT_SIGNAL); ftdi channel (FT232H_CHANNEL); ftdi tdo_sample_edge (FT232H_EDGE);",
    ),
    ("J-LINK", "adapter driver jlink;"),
    (
        "Linux GPIO",
        "adapter driver linuxgpiod; adapter gpio srst (GPIOD_SRST_PIN) -chip (GPIOD_CHIP); adapter gpio tdo (GPIOD_TDO_PIN) -chip (GPIOD_CHIP); adapter gpio tck (GPIOD_TCK_PIN) -chip (GPIOD_CHIP); adapter gpio swclk (GPIOD_TCK_PIN) -chip (GPIOD_CHIP); adapter gpio tms (GPIOD_TMS_PIN) -chip (GPIOD_CHIP); adapter gpio swdio (GPIOD_TMS_PIN) -chip (GPIOD_CHIP); adapter gpio tdi (GPIOD_TDI_PIN) -chip (GPIOD_CHIP); adapter gpio trst (GPIOD_TRST_PIN) -chip (GPIOD_CHIP);",
    ),
    (
        "Parallel Port",
        "adapter driver parport; parport cable (PARPORT_CABLE); parport port (PARPORT_PORT);",
    ),
    (
        "Remote Bitbang",
        "adapter driver remote_bitbang; remote_bitbang host (REMOTE_BITBANG_HOST); remote_bitbang port (REMOTE_BITBANG_PORT);",
    ),
    ("NULL", "adapter driver dummy;"),
]
_targets = [
    "arm7tdmi",
    "arm9tdmi",
    "arm920t",
    "arm720t",
    "arm966e",
    "arm946e",
    "arm926ejs",
    "xscale",
    "cortex_m",
    "cortex_a",
    "cortex_r4",
    "arm11",
    "aarch64",
]
_force_ir = {
    4: [
        "arm7tdmi",
        "arm9tdmi",
        "arm920t",
        "arm720t",
        "arm966e",
        "arm946e",
        "arm926ejs",
        "xscale",
    ],
    5: ["arm11"],
}
_dap_required = ["cortex_m", "cortex_a", "cortex_r4", "aarch64"]
_init_normal = "jtag newtap target cpu -irlen (IR)(XPARAM); target create target.cpu (TYPE) -endian (ENDIAN) -chain-position target.cpu; "
_init_dap = "jtag newtap target cpu -irlen (IR)(XPARAM); dap create target.dap -chain-position target.cpu; target create target.cpu (TYPE) -endian (ENDIAN) -dap target.dap; "
_reset_type = [
    ("None", "none"),
    ("TRST only", "trst_only"),
    ("SRST only", "srst_only"),
    ("TRST and SRST", "trst_and_srst"),
    ("TRST and SRST: SRST pulls TRST", "trst_and_srst srst_pulls_trst"),
    ("TRST and SRST: TRST pulls SRST", "trst_and_srst trst_pulls_srst"),
    ("TRST and SRST: Combined", "trst_and_srst combined"),
    ("TRST and SRST: Seperate", "trst_and_srst seperate"),
]
_reset_delays = [0, 5, 10, 25, 50, 75, 100]
_ft232h_adapters = [
    ("Custom", ""),
    ("Bus Blaster", "source [find interface/ftdi/dp_busblaster.cfg];"),
    (
        "Bus Blaster (KT-Link)",
        "source [find interface/ftdi/dp_busblaster_kt-link.cfg];",
    ),
    ("JTAGKey", "source [find interface/ftdi/jtagkey.cfg];"),
    ("JTAGKey2", "source [find interface/ftdi/jtagkey2.cfg];"),
    ("JTAGKey2P", "source [find interface/ftdi/jtagkey2p.cfg];"),
    ("KT-Link", "source [find interface/ftdi/kt-link.cfg];"),
    ("OpenDous", "source [find interface/ftdi/opendous_ftdi.cfg];"),
    (
        "JTAG Lock-Pick Tiny 2",
        "source [find interface/ftdi/jtag-lock-pick_tiny_2.cfg];",
    ),
]

# _ft232h_default_data = 0xfff8 # [1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0] = 0 = Low, 1 = High
# _ft232h_default_dir = 0xfffb # [1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1] = 0 = In, 1 = Out

# UM232H        FT232H    JTAG
# Name  Pin     Name      Func
# AD0   J2-6    ADBUS0    TCK
# AD1   J2-7    ADBUS1    TDI
# AD2   J2-8    ADBUS2    TDO
# AD3   J2-9    ADBUS3    TMS
# AD4   J2-10   ADBUS4    nTRST
# AD5   J2-11   ADBUS5    nSRST
# AD6   J2-12   ADBUS6    (GPIOL2)
# AD7   J2-13   ADBUS7    (GPIOL3)
# AD0   J1-14   ACBUS0    (GPIOH0)
# AD1   J1-13   ACBUS1    (GPIOH1)
# AD2   J1-12   ACBUS2    (GPIOH2)
# AD3   J1-11   ACBUS3    (GPIOH3)
# AD4   J1-10   ACBUS4    (GPIOH4)
# AD5   J1-9    ACBUS5    (GPIOH5)
# AD6   J1-8    ACBUS6    (GPIOH6)
# AD7   J1-7    ACBUS7    (GPIOH7)

_ft232h_default_jtag_tck = 0  # LOW, OUT
_ft232h_default_jtag_tdi = 1  # LOW, OUT
_ft232h_default_jtag_tdo = 2  # IN
_ft232h_default_jtag_tms = 3  # HIGH, OUT
_ft232h_default_jtag_trst = 4  # HIGH, OUT
_ft232h_default_jtag_srst = 5  # HIGH, OUT

_ft232r_bit_tx = 0
_ft232r_bit_rx = 1
_ft232r_bit_rts = 2
_ft232r_bit_cts = 3
_ft232r_bit_dtr = 4
_ft232r_bit_dsr = 5
_ft232r_bit_dcd = 6
_ft232r_bit_ri = 7

_ft232h_boards = [
    ("CJMCU", "pinouts/opt/ft232h_cjmcu_pinout.png", True),
    ("Adafruit", "pinouts/opt/ft232h_adafruit_pinout.png", False),
    ("UM232H", "pinouts/opt/ft232h_um232h_pinout.png", False),
]

_ft232r_boards = [
    ("AliExpress", "pinouts/opt/ft232r_aliexpress_pinout.png"),
    ("Sparkfun FT231X", "pinouts/opt/ft231x_sparkfun_pinout.png"),
]

_jtag_sleep_delay = 4000
_jtag_init_delay = 50000

_platforms_a = [
    {
        "name": "NOR-memory based",
        "mode": 4,
        "chip_width": 2,
        "bus_width": 2,
        "init": [],
    },
    {
        "name": "NOR-memory based (Type B)",
        "mode": 4,
        "chip_width": 2,
        "bus_width": 4,
        "init": [],
    },
    {
        "name": "MSM5100/MSM5500/MSM6000",
        "mode": 4,
        "chip_width": 2,
        "bus_width": 2,
        "init": [
            {"address": "03000674", "type": 2, "value": "0x00000002"},
            {"address": "03000664", "type": 2, "value": "0x00000002"},
            {"address": "03000660", "type": 2, "value": "0x00000800"},
            {"address": "03000670", "type": 2, "value": "0x00004800"},
            {"address": "03000720", "type": 2, "value": "0x00000E00"},
            {"address": "0300072C", "type": 2, "value": "0x00000E00"},
            {"address": "048000A4", "type": 2, "value": "0x00000001"},
            {"address": "04800070", "type": 2, "value": "0x00000004"},
            {"address": "0480008C", "type": 2, "value": "0x00000000"},
            {"address": "04800080", "type": 2, "value": "0x00002033"},
            {"address": "03000674", "type": 2, "value": "0x00000002"},
            {"address": "03000664", "type": 2, "value": "0x00000002"},
            {"address": "04800080", "type": 4, "value": "0x00002033"},
            {"address": "04800084", "type": 4, "value": "0x00000433"},
            {"address": "04800088", "type": 4, "value": "0x00000421"},
            {"address": "0480008C", "type": 4, "value": "0x00000000"},
            {"address": "04800090", "type": 4, "value": "0x00001603"},
            {"address": "04800094", "type": 4, "value": "0x00000000"},
            {"address": "04800098", "type": 4, "value": "0x00000000"},
            {"address": "048000A0", "type": 4, "value": "0x00000007"},
            {"address": "04800000", "type": 4, "value": "0x00000004"},
            {"address": "04800004", "type": 4, "value": "0x00000000"},
            {"address": "0480009C", "type": 4, "value": "0x00000513"},
            {"address": "03000760", "type": 4, "value": "0x00000000"},
            {"address": "03000768", "type": 4, "value": "0x00000000"},
            {"address": "03000738", "type": 4, "value": "0x00000010"},
        ],
    },
    {
        "name": "MSM5100/MSM5500 (NAND)",
        "mode": 5,
        "flash_buffer": 0x01800000,
        "flash_cmd": 0x01a00000,
        "flash_addr": 0x01900000,
        "flash_wait": -1,        
        "reg_width": 1,
        "wait_mask": 0,
        "init": [],
    },
    {
        "name": "MSM5100/MSM5500 (NAND, Type B)",
        "mode": 5,
        "flash_buffer": 0x02800000,
        "flash_cmd": 0x02a00000,
        "flash_addr": 0x02900000,
        "flash_wait": -1,        
        "reg_width": 1,
        "wait_mask": 0,
        "init": [],
    },    
    {
        "name": "Megachips (Samsung Z107)",
        "mode": 5,
        "flash_buffer": 0x04000000,
        "flash_cmd": 0x04200000,
        "flash_addr": 0x04100000,
        "flash_wait": 0xff00030c,
        "reg_width": 2,
        "wait_mask": 8,
        "init": [],
    },
    {
        "name": "Sysol (Samsung, Type 1)",
        "mode": 5,
        "flash_buffer": 0x04000000,
        "flash_cmd": 0x04000004,
        "flash_addr": 0x04000008,
        "flash_wait": None,
        "reg_width": 2,
        "wait_mask": 0,
        "init": [],
    },
    {
        "name": "Sysol (Samsung, Type 2)",
        "mode": 5,
        "flash_buffer": 0x01800000,
        "flash_cmd": 0x01800004,
        "flash_addr": 0x01800008,
        "flash_wait": None,
        "reg_width": 2,
        "wait_mask": 0,
        "init": [],
    },
    {
        "name": "SEMC (PNX5230)",
        "mode": 5,
        "flash_buffer": 0x40000000,
        "flash_cmd": 0x40400000,
        "flash_addr": 0x40800000,
        "flash_wait": 0x50304000,
        "reg_width": 0,
        "wait_mask": 0x10,
        "init": [],
    },
    {
        "name": "PNX67xx (WIP)",
        "mode": 5,
        "flash_buffer": 0xC1300000,
        "flash_cmd": 0xC1300004,
        "flash_addr": 0xC1300008,
        "flash_wait": 0xC1300018,
        "reg_width": 4,
        "wait_mask": 0x1,
        "init": [
            {"address": "C1300004", "type": 4, "value": "0xFF", "delay_after": 600},
            {"address": "C1300010", "type": 4, "value": "0x4"},
            {"address": "C1300020", "type": 4, "value": "0x0"},
            {"address": "C1300014", "type": 4, "value": "0x5A"},
            {"address": "C130002C", "type": 4, "value": "0x0A020100"},
            {
                "address": "C1300044",
                "type": 4,
                "value": "0x00040201",
                "delay_after": 400,
            },
        ],
    },
    {"name": "SEMC (DB2xxx, WIP)", "mode": 6, "flash_base": 0x24000000, "init": []},
    {
        "name": "SEMC (DB3xxx)",
        "mode": 5,
        "flash_buffer": 0x80000000,
        "flash_cmd": 0x80010000,
        "flash_addr": 0x80020000,
        "flash_wait": 0x9F8000C8,
        "reg_width": 0,
        "wait_mask": 2,
        "init": [],
    },
    {"name": "OneNAND (Generic)", "mode": 7, "init": []},
]

# _platforms_b = [{"name": "MSM6025/MSM6050", "mode": 4, "chip_width": 2, "bus_width": 2, "init": [{"name": "SLEEP_CTL_WB", "address": "30006d0", "type": 4, "value": "0x1"}]}, {"name": "MSM6025/MSM6050 (+NOR Init)", "mode": 4, "chip_width": 2, "bus_width": 2, "init": [{"name": "SLEEP_CTL_WB", "address": "30006d0", "type": 4, "value": "0x1"}, {"address": "03000674", "type": 2, "value": "0x00000002"}, {"address": "03000664", "type": 2, "value": "0x00000002"}, {"address": "03000660", "type": 2, "value": "0x00000800"}, {"address": "03000670", "type": 2, "value": "0x00004800"}, {"address": "03000720", "type": 2, "value": "0x00000E00"}, {"address": "0300072C", "type": 2, "value": "0x00000E00"}, {"address": "048000A4", "type": 2, "value": "0x00000001"}, {"address": "04800070", "type": 2, "value": "0x00000004"}, {"address": "0480008C", "type": 2, "value": "0x00000000"}, {"address": "04800080", "type": 2, "value": "0x00002033"}, {"address": "03000674", "type": 2, "value": "0x00000002"}, {"address": "03000664", "type": 2, "value": "0x00000002"}, {"address": "04800080", "type": 4, "value": "0x00002033"}, {"address": "04800084", "type": 4, "value": "0x00000433"}, {"address": "04800088", "type": 4, "value": "0x00000421"}, {"address": "0480008C", "type": 4, "value": "0x00000000"}, {"address": "04800090", "type": 4, "value": "0x00001603"}, {"address": "04800094", "type": 4, "value": "0x00000000"}, {"address": "04800098", "type": 4, "value": "0x00000000"}, {"address": "048000A0", "type": 4, "value": "0x00000007"}, {"address": "04800000", "type": 4, "value": "0x00000004"}, {"address": "04800004", "type": 4, "value": "0x00000000"}, {"address": "0480009C", "type": 4, "value": "0x00000513"}, {"address": "03000760", "type": 4, "value": "0x00000000"}, {"address": "03000768", "type": 4, "value": "0x00000000"}, {"address": "03000738", "type": 4, "value": "0x00000010"}]}, {"name": "MSM6250/MSM6250A/MSM6225", "mode": 2, "flash_buffer": "64000000", "flash_cmd": "64000300", "flash_addr": "64000304", "flash_status": "64000308", "flash_wait_status": "84000244", "flash_cfg": "6400031C", "init": [{"name": "MSM_CLK_ENA0", "address": "84001400", "type": 4, "value": "0x3FFFFFFF"}, {"name": "MSM_CLK_ENA1", "address": "84001404", "type": 4, "value": "0x0000000F"}, {"name": "EBI1_CFG", "address": "600000A0", "type": 2, "value": "0x200"}, {"name": "EBI1_MPMC_STDY_SEL", "address": "600000A8", "type": 1, "value": "0x0"}, {"name": "EBI1_PSRAM_CRE", "address": "600000AC", "type": 1, "value": "0x1"}, {"name": "EBI1_CS0_CFG0", "address": "600000B0", "type": 4, "value": "0x0033FC00"}, {"name": "EBI1_CS0_CFG1", "address": "600000B4", "type": 1, "value": "0x0"}, {"name": "EBI1_CS1_CFG0", "address": "600000B8", "type": 4, "value": "0x0033FC00"}, {"name": "EBI1_CS1_CFG1", "address": "600000BC", "type": 1, "value": "0x0"}, {"name": "EBI1_CS2_CFG0", "address": "600000C0", "type": 4, "value": "0x0033FC00"}, {"name": "EBI1_CS2_CFG1", "address": "600000C4", "type": 1, "value": "0x0"}, {"name": "EBI1_CS3_CFG0", "address": "600000C8", "type": 4, "value": "0x0033FC00"}, {"name": "EBI1_CS3_CFG1", "address": "600000CC", "type": 1, "value": "0x0"}, {"name": "EBI1_MEM_CTLR_SEL_CM", "address": "600000D0", "type": 1, "value": "0x0"}, {"name": "EBI2_CFG", "address": "600000E0", "type": 4, "value": "0x2"}, {"name": "GP0_CFG0", "address": "600000E4", "type": 4, "value": "0x03111122"}, {"name": "GP0_CFG1", "address": "600000E8", "type": 1, "value": "0x0"}, {"name": "GP1_CFG0", "address": "600000EC", "type": 4, "value": "0x03111122"}, {"name": "GP1_CFG1", "address": "600000F0", "type": 1, "value": "0x0"}, {"name": "RAM2_CFG0", "address": "600000F4", "type": 4, "value": "0x03111122"}, {"name": "RAM2_CFG1", "address": "600000F8", "type": 1, "value": "0x0"}, {"name": "ROM2_CFG0", "address": "600000FC", "type": 4, "value": "0x03111122"}, {"name": "ROM2_CFG", "address": "60000100", "type": 1, "value": "0x0"}, {"name": "LCD_CFG0", "address": "60000104", "type": 4, "value": "0x77770807"}, {"name": "LCD_CFG1", "address": "60000108", "type": 4, "value": "0x0"}, {"name": "SLEEP_CTL_WB", "address": "80003404", "type": 4, "value": "0x1"}, {"name": "GPIO_OE_0", "address": "84000150", "type": 4, "value": "0x8"}]}, {"name": "QSC6010/QSC6020/QSC6030", "mode": 2, "flash_buffer": "64000100", "flash_cmd": "64000004", "flash_addr": "64000000", "flash_status": "64000008", "flash_wait_status": None, "flash_cfg": "64000028", "init": []}, {"name": "MSM6100/MSM6300", "mode": 1, "flash_buffer": "64000000", "flash_cmd": "64000300", "flash_addr": "64000304", "flash_status": "64000308", "flash_wait_status": "80000C84", "flash_cfg": "6400031C", "init": [{"name": "", "address": "80001200", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80001204", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80001208", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "8000120C", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80001210", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80001214", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80001218", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "8000121C", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80001220", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80001224", "type": 4, "value": "0xFFFFFFFF"}]}, {"name": "MSM6500/MSM6125", "mode": 1, "flash_buffer": "64000000", "flash_cmd": "64000300", "flash_addr": "64000304", "flash_status": "64000308", "flash_wait_status": "80000950", "flash_cfg": "6400031C", "init": [{"name": "", "address": "80002200", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80002204", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80002208", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "8000220C", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80002210", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80002214", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80002218", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "8000221C", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80002220", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80002224", "type": 4, "value": "0xFFFFFFFF"}]}, {"name": "MSM6275/MSM6800", "mode": 2, "flash_buffer": "60000000", "flash_cmd": "60000304", "flash_addr": "60000300", "flash_status": "60000308", "flash_wait_status": "80000488", "flash_cfg": "60000328", "init": [{"name": "", "address": "80000904", "type": 4, "value": "0xFFFFFFFF"}, {"name": "", "address": "80000914", "type": 4, "value": "0xFFFFFFFF"}]}, {"name": "MSM6275/MSM6800 16 bit", "mode": 2, "flash_buffer": "60000000", "flash_cmd": "60000304", "flash_addr": "60000300", "flash_status": "60000308", "flash_wait_status": "80000488", "flash_cfg": "60000328", "init": [{"name": "", "address": "84004408", "type": 4, "value": "0x8"}, {"name": "", "address": "84004400", "type": 4, "value": "0x8"}, {"name": "MSM_CLK_HALTA", "address": "80000000", "type": 4, "value": "0x0"}, {"name": "MSM_CLK_HALTB", "address": "80000004", "type": 4, "value": "0x0"}, {"name": "EBI1_CFG", "address": "80000300", "type": 4, "value": "0x22A0000"}, {"name": "PAD_HDRIVE_SEL_0", "address": "80000A1C", "type": 4, "value": "0x400"}, {"name": "GPIO_PAD_HDRIVE_SEL_2", "address": "80000A2C", "type": 4, "value": "0x0"}, {"name": "EBI1_STDY_SEL", "address": "80000304", "type": 4, "value": "0x1"}, {"name": "MPMC_CONTROL", "address": "80001000", "type": 4, "value": "0x9"}, {"name": "MPMC_CONFIG", "address": "80001008", "type": 4, "value": "0x0"}, {"name": "EBI_MEM_CTLR_mode", "address": "8000032C", "type": 4, "value": "0x1"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4C"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4D"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4F"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "MPMC_DY_TRD_CFG", "address": "80001028", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_TRD_TRP", "address": "80001030", "type": 4, "value": "0x3"}, {"name": "MPMC_DY_TRD_TRAS", "address": "80001034", "type": 4, "value": "0x5"}, {"name": "MPMC_DY_TRD_TSREX", "address": "80001038", "type": 4, "value": "0x7"}, {"name": "MPMC_DY_TRD_TAPR", "address": "8000103c", "type": 4, "value": "0x6"}, {"name": "MPMC_DY_TRD_TDAL", "address": "80001040", "type": 4, "value": "0x5"}, {"name": "MPMC_DY_TRD_TWR", "address": "80001044", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_TRD_TRC", "address": "80001048", "type": 4, "value": "0x7"}, {"name": "MPMC_DY_TRD_TRFC", "address": "8000104c", "type": 4, "value": "0x8"}, {"name": "MPMC_DY_TRD_TXSR", "address": "80001050", "type": 4, "value": "0x8"}, {"name": "MPMC_DY_TRD_TRRD", "address": "80001054", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_TRD_TMRD", "address": "80001058", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_CNTL", "address": "80001020", "type": 4, "value": "0x183"}, {"name": "MPMC_DY_CNTL", "address": "80001020", "type": 4, "value": "0x103"}, {"name": "MPMC_DY_REF", "address": "80001024", "type": 4, "value": "0x1D"}, {"name": "MPMC_DY_RAS_CAS0", "address": "80001104", "type": 4, "value": "0x303"}, {"name": "MPMC_DY_CONFIG0", "address": "80001100", "type": 4, "value": "0x1688"}, {"name": "MPMC_DY_CTNL", "address": "80001020", "type": 4, "value": "0x83"}, {"name": "MPMC_DY_CONFIG0", "address": "80001100", "type": 4, "value": "0x81688"}]}, {"name": "MSM6275/MSM6800 32 bit 512MB", "mode": 2, "flash_buffer": "60000000", "flash_cmd": "60000304", "flash_addr": "60000300", "flash_status": "60000308", "flash_wait_status": "80000488", "flash_cfg": "60000328", "init": [{"name": "", "address": "84004408", "type": 4, "value": "0x8"}, {"name": "", "address": "84004400", "type": 4, "value": "0x8"}, {"name": "MSM_CLK_HALTA", "address": "80000000", "type": 4, "value": "0x0"}, {"name": "MSM_CLK_HALTB", "address": "80000004", "type": 4, "value": "0x0"}, {"name": "EBI1_CFG", "address": "80000300", "type": 4, "value": "0x22A0000"}, {"name": "PAD_HDRIVE_SEL_0", "address": "80000A1C", "type": 4, "value": "0x400"}, {"name": "GPIO_PAD_HDRIVE_SEL_2", "address": "80000A2C", "type": 4, "value": "0x0"}, {"name": "EBI1_STDY_SEL", "address": "80000304", "type": 4, "value": "0x1"}, {"name": "MPMC_CONTROL", "address": "80001000", "type": 4, "value": "0x9"}, {"name": "MPMC_CONFIG", "address": "80001008", "type": 4, "value": "0x0"}, {"name": "EBI_MEM_CTLR_mode", "address": "8000032C", "type": 4, "value": "0x1"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4C"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4D"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4F"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x43"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x44"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x45"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x46"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x47"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x48"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x49"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4A"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4B"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "MPMC_DY_TRD_CFG", "address": "80001028", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_TRD_TRP", "address": "80001030", "type": 4, "value": "0x3"}, {"name": "MPMC_DY_TRD_TRAS", "address": "80001034", "type": 4, "value": "0x5"}, {"name": "MPMC_DY_TRD_TSREX", "address": "80001038", "type": 4, "value": "0x7"}, {"name": "MPMC_DY_TRD_TAPR", "address": "8000103c", "type": 4, "value": "0x6"}, {"name": "MPMC_DY_TRD_TDAL", "address": "80001040", "type": 4, "value": "0x5"}, {"name": "MPMC_DY_TRD_TWR", "address": "80001044", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_TRD_TRC", "address": "80001048", "type": 4, "value": "0x7"}, {"name": "MPMC_DY_TRD_TRFC", "address": "8000104c", "type": 4, "value": "0x8"}, {"name": "MPMC_DY_TRD_TXSR", "address": "80001050", "type": 4, "value": "0x8"}, {"name": "MPMC_DY_TRD_TRRD", "address": "80001054", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_TRD_TMRD", "address": "80001058", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_CNTL", "address": "80001020", "type": 4, "value": "0x183"}, {"name": "MPMC_DY_CNTL", "address": "80001020", "type": 4, "value": "0x103"}, {"name": "MPMC_DY_REF", "address": "80001024", "type": 4, "value": "0x1D"}, {"name": "MPMC_DY_RAS_CAS0", "address": "80001104", "type": 4, "value": "0x303"}, {"name": "MPMC_DY_CONFIG0", "address": "80001100", "type": 4, "value": "0x5688"}, {"name": "MPMC_DY_CTNL", "address": "80001020", "type": 4, "value": "0x83"}, {"name": "MPMC_DY_CONFIG0", "address": "80001100", "type": 4, "value": "0x85688"}]}, {"name": "MSM6275/MSM6800 32 bit 1GB", "mode": 2, "flash_buffer": "60000000", "flash_cmd": "60000304", "flash_addr": "60000300", "flash_status": "60000308", "flash_wait_status": "80000488", "flash_cfg": "60000328", "init": [{"name": "", "address": "84004408", "type": 4, "value": "0x8"}, {"name": "", "address": "84004400", "type": 4, "value": "0x8"}, {"name": "MSM_CLK_HALTA", "address": "80000000", "type": 4, "value": "0x0"}, {"name": "MSM_CLK_HALTB", "address": "80000004", "type": 4, "value": "0x0"}, {"name": "EBI1_CFG", "address": "80000300", "type": 4, "value": "0x22A0000"}, {"name": "PAD_HDRIVE_SEL_0", "address": "80000A1C", "type": 4, "value": "0x400"}, {"name": "GPIO_PAD_HDRIVE_SEL_2", "address": "80000A2C", "type": 4, "value": "0x0"}, {"name": "EBI1_STDY_SEL", "address": "80000304", "type": 4, "value": "0x1"}, {"name": "MPMC_CONTROL", "address": "80001000", "type": 4, "value": "0x9"}, {"name": "MPMC_CONFIG", "address": "80001008", "type": 4, "value": "0x0"}, {"name": "EBI_MEM_CTLR_mode", "address": "8000032C", "type": 4, "value": "0x1"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4C"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4D"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4F"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x43"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x44"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x45"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x46"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x47"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x48"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x49"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4A"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "GPIO_PAGE", "address": "80000920", "type": 4, "value": "0x4B"}, {"name": "GPIO_CFG", "address": "80000924", "type": 4, "value": "0x4"}, {"name": "MPMC_DY_TRD_CFG", "address": "80001028", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_TRD_TRP", "address": "80001030", "type": 4, "value": "0x3"}, {"name": "MPMC_DY_TRD_TRAS", "address": "80001034", "type": 4, "value": "0x5"}, {"name": "MPMC_DY_TRD_TSREX", "address": "80001038", "type": 4, "value": "0x7"}, {"name": "MPMC_DY_TRD_TAPR", "address": "8000103c", "type": 4, "value": "0x6"}, {"name": "MPMC_DY_TRD_TDAL", "address": "80001040", "type": 4, "value": "0x5"}, {"name": "MPMC_DY_TRD_TWR", "address": "80001044", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_TRD_TRC", "address": "80001048", "type": 4, "value": "0x7"}, {"name": "MPMC_DY_TRD_TRFC", "address": "8000104c", "type": 4, "value": "0x8"}, {"name": "MPMC_DY_TRD_TXSR", "address": "80001050", "type": 4, "value": "0x8"}, {"name": "MPMC_DY_TRD_TRRD", "address": "80001054", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_TRD_TMRD", "address": "80001058", "type": 4, "value": "0x1"}, {"name": "MPMC_DY_CNTL", "address": "80001020", "type": 4, "value": "0x183"}, {"name": "MPMC_DY_CNTL", "address": "80001020", "type": 4, "value": "0x103"}, {"name": "MPMC_DY_REF", "address": "80001024", "type": 4, "value": "0x1D"}, {"name": "MPMC_DY_RAS_CAS0", "address": "80001104", "type": 4, "value": "0x303"}, {"name": "MPMC_DY_CONFIG0", "address": "80001100", "type": 4, "value": "0x5888"}, {"name": "MPMC_DY_CTNL", "address": "80001020", "type": 4, "value": "0x83"}, {"name": "MPMC_DY_CTNL", "address": "80001020", "type": 4, "value": "0x3"}, {"name": "MPMC_DY_CONFIG0", "address": "80001100", "type": 4, "value": "0x85888"}]}, {"name": "MSM6245/MSM6260(A)/ESM6235/MSM6801/MSM6246", "mode": 2, "flash_buffer": "60000000", "flash_cmd": "60000304", "flash_addr": "60000300", "flash_status": "60000308", "flash_wait_status": "80000488", "flash_cfg": "60000328", "init": []}, {"name": "MSM6550/MSM6150", "mode": 1, "flash_buffer": "60000000", "flash_cmd": "60000300", "flash_addr": "60000304", "flash_status": "60000308", "flash_wait_status": "80000958", "flash_cfg": "6000031C", "init": []}, {"name": "MSM6280/MSM6281", "mode": 2, "flash_buffer": "60000000", "flash_cmd": "60000304", "flash_addr": "60000300", "flash_status": "60000308", "flash_wait_status": "80000488", "flash_cfg": "60000328", "init": []}, {"name": "MSM7200/MSM7200A/MSM7201A/MSM7500/MSM7500A/MSM7501A/QSD8x50", "mode": 3, "flash_buffer": "A0A00100", "flash_cmd": "A0A00000", "flash_exec_cmd": "A0A00010", "flash_addr0": "A0A00004", "flash_addr1": "A0A00008", "flash_status": "A0A00014", "buffer_status": "A0A00018", "flash_read_status": "A0A00044", "flash_id": "A0A00040", "flash_chip": "A0A0000C", "flash_cfg0": "A0A00020", "flash_cfg1": "A0A00024", "flash_vld": "A0A000AC", "init": [{"name": "TLMM_INT_JTAG_CTL", "address": "A900026C", "type": 4, "value": "0x9"}, {"name": "DISABLE_NAND_MPU", "address": "A0B00000", "type": 4, "value": "0x0"}]}, {"name": "MSM72xx", "mode": 3, "flash_buffer": "A0A00100", "flash_cmd": "A0A00000", "flash_exec_cmd": "A0A00010", "flash_addr0": "A0A00004", "flash_addr1": "A0A00008", "flash_status": "A0A00014", "buffer_status": "A0A00018", "flash_read_status": "A0A00044", "flash_id": "A0A00040", "flash_chip": "A0A0000C", "flash_cfg0": "A0A00020", "flash_cfg1": "A0A00024", "flash_vld": "A0A000AC", "init": [{"name": "DISABLE_NAND_MPU", "address": "A0B00000", "type": 4, "value": "0x0"}]}, {"name": "MDM66xx", "mode": 3, "flash_buffer": "70000100", "flash_cmd": "70000000", "flash_exec_cmd": "70000010", "flash_addr0": "70000004", "flash_addr1": "70000008", "flash_status": "70000014", "buffer_status": "70000018", "flash_read_status": "70000044", "flash_id": "70000040", "flash_chip": "7000000C", "flash_cfg0": "70000020", "flash_cfg1": "70000024", "flash_vld": "700000AC", "init": [{"name": "DISABLE_NAND_MPU", "address": "70100000", "type": 4, "value": "0x0"}]}, {"name": "MSM7x30", "mode": 3, "flash_buffer": "A0200100", "flash_cmd": "A0200000", "flash_exec_cmd": "A0200010", "flash_addr0": "A0200004", "flash_addr1": "A0200008", "flash_status": "A0200014", "buffer_status": "A0200018", "flash_read_status": "A0200044", "flash_id": "A0200040", "flash_chip": "A020000C", "flash_cfg0": "A0200020", "flash_cfg1": "A0200024", "flash_vld": "A02000AC", "init": [{"name": "TLMM_INT_JTAG_CTL", "address": "ABE0026C", "type": 4, "value": "0x9"}, {"name": "DISABLE_NAND_MPU", "address": "A0300000", "type": 4, "value": "0x0"}]}, {"name": "MDM9600", "mode": 3, "flash_buffer": "81600100", "flash_cmd": "81600000", "flash_exec_cmd": "81600010", "flash_addr0": "81600004", "flash_addr1": "81600008", "flash_status": "81600014", "buffer_status": "81600018", "flash_read_status": "81600044", "flash_id": "81600040", "flash_chip": "8160000C", "flash_cfg0": "81600020", "flash_cfg1": "81600024", "flash_vld": "816000AC", "init": [{"name": "TLMM_INT_JTAG_CTL", "address": "9404026C", "type": 4, "value": "0x9"}, {"name": "DISABLE_NAND_MPU", "address": "81700000", "type": 4, "value": "0x0"}]}, {"name": "QSC6055/6065/6085/6270", "mode": 3, "flash_buffer": "60008100", "flash_cmd": "60008000", "flash_exec_cmd": "60008010", "flash_addr0": "60008004", "flash_addr1": "60008008", "flash_status": "60008014", "buffer_status": "60008018", "flash_read_status": "60008044", "flash_id": "60008040", "flash_chip": "6000800C", "flash_cfg0": "60008020", "flash_cfg1": "60008024", "flash_vld": "600080AC", "init": []}, {"name": "OneNAND 62xx", "mode": 7, "o1n_offset": "40000000", "init": []}, {"name": "OneNAND OMAP850", "mode": 7, "o1n_offset": "00", "init": []}, {"name": "OneNAND MSM7x00", "mode": 7, "o1n_offset": "A0A00000", "init": []}, {"name": "OneNAND MDM9600", "mode": 7, "o1n_offset": "81600000", "init": []}, {"name": "OneNAND MDM66xx", "mode": 7, "o1n_offset": "70000000", "init": []}]

_platforms_b = _platforms_b = [
    {
        "name": "MSM6025/MSM6050",
        "mode": 4,
        "chip_width": 2,
        "bus_width": 2,
        "init": [
        #    {"name": "SLEEP_CTL_WB", "address": "30006d0", "type": 4, "value": "0x1"}
        ],
    },
    {
        "name": "MSM6025/MSM6050 (NAND controller)",
        "mode": 1,
        "flash_regs": 0x0C000000,
        "flash_int_clear": -1,
        "flash_int": -1,
        "flash_nand_int": 0x6000,        
        "flash_has_header": False,
        "init": [
        #    {"name": "SLEEP_CTL_WB", "address": "30006d0", "type": 4, "value": "0x1"}
        ],
    },
    {
        "name": "MSM6250/MSM6250A/MSM6225",
        "mode": 1,
        "flash_regs": 0x64000000,
        "flash_int_clear": 0x8400024C,
        "flash_int": 0x84000244,
        "flash_nand_int": 0x6,        
        "flash_has_header": False,
        "init": [
            {
                "name": "MSM_CLK_ENA0",
                "address": "84001400",
                "type": 4,
                "value": "0x3FFFFFFF",
            },
            {
                "name": "MSM_CLK_ENA1",
                "address": "84001404",
                "type": 4,
                "value": "0x0000000F",
            },
            {"name": "EBI1_CFG", "address": "600000A0", "type": 2, "value": "0x200"},
            {
                "name": "EBI1_MPMC_STDY_SEL",
                "address": "600000A8",
                "type": 1,
                "value": "0x0",
            },
            {
                "name": "EBI1_PSRAM_CRE",
                "address": "600000AC",
                "type": 1,
                "value": "0x1",
            },
            {
                "name": "EBI1_CS0_CFG0",
                "address": "600000B0",
                "type": 4,
                "value": "0x0033FC00",
            },
            {"name": "EBI1_CS0_CFG1", "address": "600000B4", "type": 1, "value": "0x0"},
            {
                "name": "EBI1_CS1_CFG0",
                "address": "600000B8",
                "type": 4,
                "value": "0x0033FC00",
            },
            {"name": "EBI1_CS1_CFG1", "address": "600000BC", "type": 1, "value": "0x0"},
            {
                "name": "EBI1_CS2_CFG0",
                "address": "600000C0",
                "type": 4,
                "value": "0x0033FC00",
            },
            {"name": "EBI1_CS2_CFG1", "address": "600000C4", "type": 1, "value": "0x0"},
            {
                "name": "EBI1_CS3_CFG0",
                "address": "600000C8",
                "type": 4,
                "value": "0x0033FC00",
            },
            {"name": "EBI1_CS3_CFG1", "address": "600000CC", "type": 1, "value": "0x0"},
            {
                "name": "EBI1_MEM_CTLR_SEL_CM",
                "address": "600000D0",
                "type": 1,
                "value": "0x0",
            },
            {"name": "EBI2_CFG", "address": "600000E0", "type": 4, "value": "0x2"},
            {
                "name": "GP0_CFG0",
                "address": "600000E4",
                "type": 4,
                "value": "0x03111122",
            },
            {"name": "GP0_CFG1", "address": "600000E8", "type": 1, "value": "0x0"},
            {
                "name": "GP1_CFG0",
                "address": "600000EC",
                "type": 4,
                "value": "0x03111122",
            },
            {"name": "GP1_CFG1", "address": "600000F0", "type": 1, "value": "0x0"},
            {
                "name": "RAM2_CFG0",
                "address": "600000F4",
                "type": 4,
                "value": "0x03111122",
            },
            {"name": "RAM2_CFG1", "address": "600000F8", "type": 1, "value": "0x0"},
            {
                "name": "ROM2_CFG0",
                "address": "600000FC",
                "type": 4,
                "value": "0x03111122",
            },
            {"name": "ROM2_CFG", "address": "60000100", "type": 1, "value": "0x0"},
            {
                "name": "LCD_CFG0",
                "address": "60000104",
                "type": 4,
                "value": "0x77770807",
            },
            {"name": "LCD_CFG1", "address": "60000108", "type": 4, "value": "0x0"},
            {"name": "SLEEP_CTL_WB", "address": "80003404", "type": 4, "value": "0x1"},
            {"name": "GPIO_OE_0", "address": "84000150", "type": 4, "value": "0x8"},
        ],
    },    
    {
        "name": "MSM6100/MSM6300",
        "mode": 1,
        "flash_regs": 0x64000000,
        "flash_int_clear": 0x80000C84,
        "flash_int": 0x80000C84,
        "flash_nand_int": 0x6000,  
        "flash_has_header": False,      
        "init": [
            {"name": "", "address": "80001200", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80001204", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80001208", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "8000120C", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80001210", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80001214", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80001218", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "8000121C", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80001220", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80001224", "type": 4, "value": "0xFFFFFFFF"},
        ],
    },
    {
        "name": "MSM6500/MSM6125",
        "mode": 1,
        "flash_regs": 0x64000000,
        "flash_int_clear": 0x80000904,
        "flash_int": 0x80000950,
        "flash_nand_int": 0x6000,     
        "flash_has_header": False,   
        "init": [
            {"name": "", "address": "80002200", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80002204", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80002208", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "8000220C", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80002210", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80002214", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80002218", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "8000221C", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80002220", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80002224", "type": 4, "value": "0xFFFFFFFF"},
        ],
    },
    {
        "name": "MSM6550/MSM6150",
        "mode": 1,
        "flash_regs": 0x60000000,
        "flash_int_clear": 0x80000904,
        "flash_int": 0x80000958,
        "flash_nand_int": 0x6000,      
        "flash_has_header": True,  
        "init": [],
    },    
    {
        "name": "MSM6275/MSM6800",
        "mode": 2,
        "flash_regs": 0x60000000,
        "flash_int_clear": 0x80000414,
        "flash_int": 0x80000488,
        "flash_nand_int": 0x2,
        "init": [
            {"name": "", "address": "80000904", "type": 4, "value": "0xFFFFFFFF"},
            {"name": "", "address": "80000914", "type": 4, "value": "0xFFFFFFFF"},
        ],
    },
    {
        "name": "MSM6245/MSM6260(A)/ESM6235/MSM6801/MSM6246",
        "mode": 2,
        "flash_regs": 0x60000000,
        "flash_int_clear": 0x80000414,
        "flash_int": 0x80000488,
        "flash_nand_int": 0x2,
        "init": [],
    },
    {
        "name": "QSC60x0",
        "mode": 4,
        "chip_width": 2,
        "bus_width": 2,
        "init": [],
    },
    {
        "name": "QSC60x0 (NAND controller)",
        "mode": 2,
        "flash_regs": 0x64000000,
        "flash_int_clear": 0x80000C84,
        "flash_int": 0x80000C84,
        "flash_nand_int": 0x6000,
        "init": [],
    },    
    {
        "name": "MSM6280/MSM6281",
        "mode": 2,
        "flash_regs": 0x60000000,
        "flash_int_clear": 0x80000414,
        "flash_int": 0x80000488,
        "flash_nand_int": 0x2,
        "init": [],
    },
    {
        "name": "MSM7200/MSM7200A/MSM7201A/MSM7500/MSM7500A/MSM7501A/QSD8x50",
        "mode": 3,
        "flash_regs": 0xA0A00000,
        "jtag_ctl": 0xA900026C,
        "init": [
            {
                "name": "TLMM_INT_JTAG_CTL",
                "address": "A900026C",
                "type": 4,
                "value": "0x9",
            },
            {
                "name": "DISABLE_NAND_MPU",
                "address": "A0B00000",
                "type": 4,
                "value": "0x0",
            },
        ],
    },
    {
        "name": "MSM72xx",
        "mode": 3,
        "flash_regs": 0xA0A00000,
        "jtag_ctl": 0xA900026C,
        "init": [
            {
                "name": "DISABLE_NAND_MPU",
                "address": "A0B00000",
                "type": 4,
                "value": "0x0",
            }
        ],
    },
    {
        "name": "MDM66xx/QSC61xx",
        "mode": 3,
        "flash_regs": 0x70000000,
        "init": [
            {
                "name": "DISABLE_NAND_MPU",
                "address": "70100000",
                "type": 4,
                "value": "0x0",
            }
        ],
    },
    {
        "name": "MSM7x30",
        "mode": 3,
        "flash_regs": 0xA0200000,
        "jtag_ctl": 0xABE0026C,
        "init": [
            {
                "name": "TLMM_INT_JTAG_CTL",
                "address": "ABE0026C",
                "type": 4,
                "value": "0x9",
            },
            {
                "name": "DISABLE_NAND_MPU",
                "address": "A0300000",
                "type": 4,
                "value": "0x0",
            },
        ],
    },
    {
        "name": "MDM9600",
        "mode": 3,
        "flash_regs": 0x81200000,
        "jtag_ctl": 0x9404026C,
        "init": [
            {
                "name": "TLMM_INT_JTAG_CTL",
                "address": "9404026C",
                "type": 4,
                "value": "0x9",
            },
            {
                "name": "DISABLE_NAND_MPU",
                "address": "81700000",
                "type": 4,
                "value": "0x0",
            },
        ],
    },
    {
        "name": "QSC60x5/62x0",
        "mode": 3,
        "flash_regs": 0x60008000,
        "init": [],
    },        
]

# 0xf9800000

_platforms_c = [
    {
        "name": "OneNAND PCF5213 (Type A)",
        "mode": 7,
        "o1n_offset": 0x28000000,
        "init": [],
    },
    {
        "name": "OneNAND PCF5213 (Type B)",
        "mode": 7,
        "o1n_offset": 0x20000000,
        "init": [],
    },
    {"name": "OneNAND PNX5230", "mode": 7, "o1n_offset": 0x48000000, "init": []},
    {"name": "OneNAND BCM2133", "mode": 7, "o1n_offset": 0x4000000, "init": []},
    {"name": "OneNAND BCM215x", "mode": 7, "o1n_offset": 0x400000, "init": []},
    {"name": "OneNAND QSC62x0/QSC60x5", "mode": 7, "o1n_offset": 0x38000000, "init": []},
    {"name": "OneNAND MSM62xx", "mode": 7, "o1n_offset": 0x40000000, "init": []},
    {"name": "OneNAND OMAP850", "mode": 7, "o1n_offset": 0x0, "init": []},
    {"name": "OneNAND MSM72xx", "mode": 7, "o1n_offset": 0x30000000, "init": []},
    {"name": "NULL", "mode": -1, "init": []},
]

_platforms = _platforms_a + _platforms_b + _platforms_c
