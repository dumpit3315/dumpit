import enum
import time
import typing

_DEBUG_CONTROLLER = False


class NANDException(Exception):
    pass


class GenericNANDController():
    def __init__(self, cmd_write_func, data_read_func, data_write_func, endian, int_read=None, cle: int = 0, ale: int = 0, data: int = 0, nand_int: int = -1, nand_int_mask: int = -1, page_size: int = 0, page_width: int = 0, inverted_wait_mask: bool = False):
        self._cmd_write = cmd_write_func
        self._data_read = data_read_func
        self._data_write = data_write_func
        self._int_read = int_read
        self._endian = endian

        self._nfi_cle = cle
        self._nfi_ale = ale
        self._nfi_data = data

        self._page_size = page_size
        self._page_width = page_width

        self._nand_int = nand_int
        self._nand_int_mask = nand_int_mask
        
        self._wait_invert = inverted_wait_mask

        self._idcode = 0
        self.ecc_enabled = True

        self._cmd_write(self._nfi_cle, 0xff)
        self._cmd_write(self._nfi_cle, 0x90)
        self._cmd_write(self._nfi_ale, 0x0)

        self._idcode = 0

        for _ in range(4):
            self._idcode <<= 8
            self._idcode |= self._data_read(self._nfi_data)

        self._cmd_write(self._nfi_cle, 0xff)

    def read(self, page: int):
        tempData = bytearray()
        tempSpare = bytearray()

        if self._page_size == 0:
            if self._page_width == 0:
                ''' First read '''
                self._cmd_write(self._nfi_cle, 0x00)

                self._cmd_write(self._nfi_ale, 0x00)
                self._cmd_write(self._nfi_ale, page & 0xff)
                self._cmd_write(self._nfi_ale, (page >> 8) & 0xff)
                self._cmd_write(self._nfi_ale, (page >> 16) & 0xff)

                if self._int_read and self._nand_int != -1:
                    while ((self._int_read(self._nand_int) & self._nand_int_mask) == 0) if not self._wait_invert else ((self._int_read(self._nand_int) & self._nand_int_mask) != 0):
                        time.sleep(0.05)

                else:
                    time.sleep(0.1)

                for _ in range(0x100):
                    tempData.append(self._data_read(self._nfi_data))

                ''' Second read '''
                self._cmd_write(self._nfi_cle, 0x01)

                self._cmd_write(self._nfi_ale, 0x00)
                self._cmd_write(self._nfi_ale, page & 0xff)
                self._cmd_write(self._nfi_ale, (page >> 8) & 0xff)
                self._cmd_write(self._nfi_ale, (page >> 16) & 0xff)

                if self._int_read and self._nand_int != -1:
                    while ((self._int_read(self._nand_int) & self._nand_int_mask) == 0) if not self._wait_invert else ((self._int_read(self._nand_int) & self._nand_int_mask) != 0):
                        time.sleep(0.05)

                else:
                    time.sleep(0.1)

                for _ in range(0x100):
                    tempData.append(self._data_read(self._nfi_data))

                ''' Spare read '''
                self._cmd_write(self._nfi_cle, 0x50)

                self._cmd_write(self._nfi_ale, 0x00)
                self._cmd_write(self._nfi_ale, page & 0xff)
                self._cmd_write(self._nfi_ale, (page >> 8) & 0xff)
                self._cmd_write(self._nfi_ale, (page >> 16) & 0xff)

                if self._int_read and self._nand_int != -1:
                    while ((self._int_read(self._nand_int) & self._nand_int_mask) == 0) if not self._wait_invert else ((self._int_read(self._nand_int) & self._nand_int_mask) != 0):
                        time.sleep(0.05)

                else:
                    time.sleep(0.1)

                for _ in range(0x10):
                    tempSpare.append(self._data_read(self._nfi_data))

            else:
                ''' First read '''
                self._cmd_write(self._nfi_cle, 0x00)

                self._cmd_write(self._nfi_ale, 0x00)
                self._cmd_write(self._nfi_ale, page & 0xff)
                self._cmd_write(self._nfi_ale, (page >> 8) & 0xff)
                self._cmd_write(self._nfi_ale, (page >> 16) & 0xff)

                if self._int_read and self._nand_int != -1:
                    while ((self._int_read(self._nand_int) & self._nand_int_mask) == 0) if not self._wait_invert else ((self._int_read(self._nand_int) & self._nand_int_mask) != 0):
                        time.sleep(0.05)

                else:
                    time.sleep(0.1)

                for _ in range(0x100):
                    tempData += self._data_read(
                        self._nfi_data).to_bytes(2, self._endian)

                ''' Spare read '''
                self._cmd_write(self._nfi_cle, 0x50)

                self._cmd_write(self._nfi_ale, 0x00)
                self._cmd_write(self._nfi_ale, page & 0xff)
                self._cmd_write(self._nfi_ale, (page >> 8) & 0xff)
                self._cmd_write(self._nfi_ale, (page >> 16) & 0xff)

                if self._int_read and self._nand_int != -1:
                    while ((self._int_read(self._nand_int) & self._nand_int_mask) == 0) if not self._wait_invert else ((self._int_read(self._nand_int) & self._nand_int_mask) != 0):
                        time.sleep(0.05)

                else:
                    time.sleep(0.1)

                for _ in range(0x8):
                    tempSpare += self._data_read(
                        self._nfi_data).to_bytes(2, self._endian)

        else:
            self._cmd_write(self._nfi_cle, 0x00)

            self._cmd_write(self._nfi_ale, 0x00)
            self._cmd_write(self._nfi_ale, 0x00)
            self._cmd_write(self._nfi_ale, page & 0xff)
            self._cmd_write(self._nfi_ale, (page >> 8) & 0xff)
            self._cmd_write(self._nfi_ale, (page >> 16) & 0xff)

            self._cmd_write(self._nfi_cle, 0x30)

            if self._int_read and self._nand_int != -1:
                while ((self._int_read(self._nand_int) & self._nand_int_mask) == 0) if not self._wait_invert else ((self._int_read(self._nand_int) & self._nand_int_mask) != 0):
                    time.sleep(0.05)

            else:
                time.sleep(0.1)

            if self._page_width == 0:
                for _ in range(0x800):
                    tempData.append(self._data_read(self._nfi_data))

                for _ in range(0x40):
                    tempSpare.append(self._data_read(self._nfi_data))

            else:
                for _ in range(0x400):
                    tempData += self._data_read(
                        self._nfi_data).to_bytes(2, self._endian)

                for _ in range(0x20):
                    tempSpare += self._data_read(
                        self._nfi_data).to_bytes(2, self._endian)

        return bytes(tempData), bytes(tempSpare), b""

    def write(self, page: int, data: typing.Union[bytes, bytearray]):
        raise NotImplementedError()

    def erase(self, page: int):
        raise NotImplementedError()


class GenericNANDControllerGPIO():
    def __init__(self, gpio_read_func, gpio_write_func, data_read_func, data_write_func, endian, latch_addr, data, cle_mask: int = 1, ale_mask: int = 2, busy_addr: int = -1, read_busy_mask: int = 0, page_size: int = 0, page_width: int = 0, inverted_wait_mask: bool = False):
        self._gpio_read = gpio_read_func
        self._gpio_write = gpio_write_func
        self._data_read = data_read_func
        self._data_write = data_write_func
        self._endian = endian

        self._nfi_cle_mask = cle_mask
        self._nfi_ale_mask = ale_mask
        self._nfi_rb_mask = read_busy_mask
        self._nfi_latch = latch_addr
        self._nfi_busy = busy_addr
        self._nfi_data = data

        self._page_size = page_size
        self._page_width = page_width
        
        self._wait_invert = inverted_wait_mask

        self._idcode = 0
        self.ecc_enabled = True

        self._gpio_write(self._nfi_latch, self._gpio_read(
            self._nfi_latch) & ~(self._nfi_cle_mask | self._nfi_ale_mask))

        self._send_cmd(0xff)
        self._send_cmd(0x90, [0x00])

        self._idcode = 0

        for _ in range(4):
            self._idcode <<= 8
            self._idcode |= self._data_read(self._nfi_data)

        self._send_cmd(0xff)

    def _send_cmd(self, cmd: int, addr: typing.List[int] = None):
        self._gpio_write(self._nfi_latch, self._gpio_read(
            self._nfi_latch) | self._nfi_cle_mask)
        self._data_write(self._nfi_data, cmd)

        self._gpio_write(self._nfi_latch, self._gpio_read(
            self._nfi_latch) & ~self._nfi_cle_mask)

        if addr is not None:
            self._gpio_write(self._nfi_latch, self._gpio_read(
                self._nfi_latch) | self._nfi_ale_mask)

            for a in addr:
                self._data_write(self._nfi_data, a)

            self._gpio_write(self._nfi_latch, self._gpio_read(
                self._nfi_latch) & ~self._nfi_ale_mask)

    def read(self, page: int):
        tempData = bytearray()
        tempSpare = bytearray()

        if self._page_size == 0:
            if self._page_width == 0:
                ''' First read '''
                self._send_cmd(
                    0x00, [0x00, (page & 0xff), ((page >> 8) & 0xff), ((page >> 16) & 0xff)])

                if self._nfi_busy != -1 and self._nfi_rb_mask:
                    while ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) == 0) if not self._wait_invert else ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) != 0):
                        time.sleep(0.05)

                else:
                    time.sleep(0.1)

                for _ in range(0x100):
                    tempData.append(self._data_read(self._nfi_data))

                ''' Second read '''
                self._send_cmd(
                    0x01, [0x00, (page & 0xff), ((page >> 8) & 0xff), ((page >> 16) & 0xff)])

                if self._nfi_busy != -1 and self._nfi_rb_mask != -1:
                    while ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) == 0) if not self._wait_invert else ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) != 0):
                        time.sleep(0.05)

                else:
                    time.sleep(0.1)

                for _ in range(0x100):
                    tempData.append(self._data_read(self._nfi_data))

                ''' Spare read '''
                self._send_cmd(
                    0x50, [0x00, (page & 0xff), ((page >> 8) & 0xff), ((page >> 16) & 0xff)])

                if self._nfi_busy != -1 and self._nfi_rb_mask != -1:
                    while ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) == 0) if not self._wait_invert else ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) != 0):
                        time.sleep(0.05)

                else:
                    time.sleep(0.1)

                for _ in range(0x10):
                    tempSpare.append(self._data_read(self._nfi_data))

            else:
                ''' First read '''
                self._send_cmd(
                    0x00, [0x00, (page & 0xff), ((page >> 8) & 0xff), ((page >> 16) & 0xff)])

                if self._nfi_busy != -1 and self._nfi_rb_mask != -1:
                    while ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) == 0) if not self._wait_invert else ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) != 0):
                        time.sleep(0.05)

                else:
                    time.sleep(0.1)

                for _ in range(0x100):
                    tempData += self._data_read(
                        self._nfi_data).to_bytes(2, self._endian)

                ''' Spare read '''
                self._send_cmd(
                    0x50, [0x00, (page & 0xff), ((page >> 8) & 0xff), ((page >> 16) & 0xff)])

                if self._nfi_busy != -1 and self._nfi_rb_mask != -1:
                    while ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) == 0) if not self._wait_invert else ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) != 0):
                        time.sleep(0.05)

                else:
                    time.sleep(0.1)

                for _ in range(0x8):
                    tempSpare += self._data_read(
                        self._nfi_data).to_bytes(2, self._endian)

        else:
            self._send_cmd(0x00, [0x00, 0x00, (page & 0xff),
                           ((page >> 8) & 0xff), ((page >> 16) & 0xff)])
            self._send_cmd(0x30)

            if self._nfi_busy != -1 and self._nfi_rb_mask != -1:
                while ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) == 0) if not self._wait_invert else ((self._gpio_read(self._nfi_busy) & self._nfi_rb_mask) != 0):
                    time.sleep(0.05)

            else:
                time.sleep(0.1)

            if self._page_width == 0:
                for _ in range(0x800):
                    tempData.append(self._data_read(self._nfi_data))

                for _ in range(0x40):
                    tempSpare.append(self._data_read(self._nfi_data))

            else:
                for _ in range(0x400):
                    tempData += self._data_read(
                        self._nfi_data).to_bytes(2, self._endian)

                for _ in range(0x20):
                    tempSpare += self._data_read(
                        self._nfi_data).to_bytes(2, self._endian)

        return bytes(tempData), bytes(tempSpare), b""

    def write(self, page: int, data: typing.Union[bytes, bytearray]):
        raise NotImplementedError()

    def erase(self, page: int):
        raise NotImplementedError()


class O1N_REGS(enum.Enum):
    BOOTRAM = (0x0000 << 1)
    DATARAM = (0x0200 << 1)
    SPARERAM = (0x8010 << 1)
    REG_MANUFACTURER_ID = (0xF000 << 1)
    REG_DEVICE_ID = (0xF001 << 1)
    REG_VERSION_ID = (0xF002 << 1)
    REG_DATA_BUFFER_SIZE = (0xF003 << 1)
    REG_BOOT_BUFFER_SIZE = (0xF004 << 1)
    REG_NUM_BUFFERS = (0xF005 << 1)
    REG_TECHNOLOGY = (0xF006 << 1)
    REG_START_ADDRESS1 = (0xF100 << 1)
    REG_START_ADDRESS2 = (0xF101 << 1)
    REG_START_ADDRESS3 = (0xF102 << 1)
    REG_START_ADDRESS4 = (0xF103 << 1)
    REG_START_ADDRESS5 = (0xF104 << 1)
    REG_START_ADDRESS6 = (0xF105 << 1)
    REG_START_ADDRESS7 = (0xF106 << 1)
    REG_START_ADDRESS8 = (0xF107 << 1)
    REG_START_BUFFER = (0xF200 << 1)
    REG_COMMAND = (0xF220 << 1)
    REG_SYS_CFG1 = (0xF221 << 1)
    REG_SYS_CFG2 = (0xF222 << 1)
    REG_CTRL_STATUS = (0xF240 << 1)
    REG_INTERRUPT = (0xF241 << 1)
    REG_START_BLOCK_ADDRESS = (0xF24C << 1)
    REG_END_BLOCK_ADDRESS = (0xF24D << 1)
    REG_WP_STATUS = (0xF24E << 1)
    REG_ECC_STATUS = (0xFF00 << 1)
    REG_ECC_M0 = (0xFF01 << 1)
    REG_ECC_S0 = (0xFF02 << 1)
    REG_ECC_M1 = (0xFF03 << 1)
    REG_ECC_S1 = (0xFF04 << 1)
    REG_ECC_M2 = (0xFF05 << 1)
    REG_ECC_S2 = (0xFF06 << 1)
    REG_ECC_M3 = (0xFF07 << 1)
    REG_ECC_S3 = (0xFF08 << 1)


class O1N_NANDOPS(enum.Enum):
    READ = 0x00
    READOOB = 0x13
    PROG = 0x80
    PROGOOB = 0x1A
    X2_PROG = 0x7D
    X2_CACHE_PROG = 0x7F
    UNLOCK = 0x23
    LOCK = 0x2A
    LOCK_TIGHT = 0x2C
    UNLOCK_ALL = 0x27
    ERASE = 0x94
    MULTIBLOCK_ERASE = 0x95
    ERASE_VERIFY = 0x71
    RESET = 0xF0
    HOT_RESET = 0xF3
    OTP_ACCESS = 0x65
    READID = 0x90
    PI_UPDATE = 0x05
    PI_ACCESS = 0x66
    RECOVER_LSB = 0x05


class OneNANDController():
    def __init__(self, read16_func, write16_func, mem_read_func, mem_write_func, base: int = 0, nand_size: int = 0):
        self._cmd_read = read16_func
        self._cmd_write = write16_func
        self._data_read = mem_read_func
        self._data_write = mem_write_func

        self._ecc_enabled = True

        self._o1n_base = base
        self._o1n_size = nand_size

        self._cmd_write(self._o1n_base + O1N_REGS.REG_SYS_CFG1.value, 0x40c0)

        self._cmd_write(self._o1n_base +
                        O1N_REGS.REG_START_ADDRESS1.value, 0x0)
        self._cmd_write(self._o1n_base +
                        O1N_REGS.REG_START_ADDRESS2.value, 0x0)

        self._cmd_write(self._o1n_base + O1N_REGS.REG_INTERRUPT.value, 0x0)
        self._cmd_write(self._o1n_base +
                        O1N_REGS.REG_COMMAND.value, O1N_NANDOPS.HOT_RESET)

        while (self._cmd_read(self._o1n_base + O1N_REGS.REG_INTERRUPT.value) & 0x8000) != 0x8000:
            time.sleep(0.05)

        self._idcode = (self._cmd_read(self._o1n_base + O1N_REGS.REG_MANUFACTURER_ID.value)
                        << 24) | (self._cmd_read(self._o1n_base + O1N_REGS.REG_DEVICE_ID.value) << 16)
        self._ddp = bool(self._cmd_read(self._o1n_base +
                         O1N_REGS.REG_DEVICE_ID.value) & 8)

        density_raw = (self._cmd_read(self._o1n_base +
                       O1N_REGS.REG_DEVICE_ID.value) >> 4) & 0xf

        self._density = 2 << ((5 if self._ddp else 6) + density_raw)

    def read(self, page: int):
        if self._ecc_enabled:
            self._cmd_write(self._o1n_base + O1N_REGS.REG_SYS_CFG1.value,
                            self._cmd_read(self._o1n_base + O1N_REGS.REG_SYS_CFG1.value) & ~0x100)
        else:
            self._cmd_write(self._o1n_base + O1N_REGS.REG_SYS_CFG1.value,
                            self._cmd_read(self._o1n_base + O1N_REGS.REG_SYS_CFG1.value) | 0x100)

        self._cmd_write(self._o1n_base + O1N_REGS.REG_INTERRUPT.value, 0x0)
        self._cmd_write(self._o1n_base + O1N_REGS.REG_ECC_STATUS.value, 0x0)
        self._cmd_write(self._o1n_base +
                        O1N_REGS.REG_START_BUFFER.value, 0x800)

        UPPER_BANK = 0x8000 if self._ddp and (
            page >> 6) >= self._density else 0x0

        self._cmd_write(self._o1n_base + O1N_REGS.REG_START_ADDRESS1.value,
                        UPPER_BANK | ((page >> 6) & (self._density - 1)))
        self._cmd_write(self._o1n_base +
                        O1N_REGS.REG_START_ADDRESS2.value, UPPER_BANK)

        self._cmd_write(self._o1n_base +
                        O1N_REGS.REG_START_ADDRESS8.value, (page & 63) << 2)
        self._cmd_write(self._o1n_base +
                        O1N_REGS.REG_COMMAND.value, O1N_NANDOPS.READ)

        while (self._cmd_read(self._o1n_base + O1N_REGS.REG_INTERRUPT.value) & 0x8080) != 0x8080:
            time.sleep(0.05)

        return self._data_read(self._o1n_base + O1N_REGS.DATARAM, 0x800 if self._o1n_size == 0 else 0x1000), self._data_read(self._o1n_base + O1N_REGS.SPARERAM, 0x40 if self._o1n_size == 0 else 0x80), b""

    def write(self, page: int, data: typing.Union[bytes, bytearray]):
        raise NotImplementedError()

    def erase(self, page: int):
        raise NotImplementedError()
