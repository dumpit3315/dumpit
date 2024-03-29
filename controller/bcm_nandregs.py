import time
import typing

_DEBUG_CONTROLLER = False


class BCM2133NANDController():
    def __init__(self, read32_func, write32_func, read16_func, write16_func, read8_func, write8_func, page_size: int = 0, page_width: int = -1):
        self._cmd_read = read32_func
        self._cmd_write = write32_func
        self._cmd2_read = read16_func
        self._cmd2_write = write16_func
        self._mem_read = read8_func
        self._mem_write = write8_func

        self._page_size = page_size
        self._page_width = page_width

        self._idcode = 0
        self.ecc_enabled = True

        self._is_axi = (self._cmd_read(0x8880010) & 0xf0) in [0xf0, 0xe0]

        if self._is_axi:
            self._cmd_write(0x2200480, 0x0)
            bitcheck_type = self._mem_read(0x8880001) in [0x90, 0xb0]

            if bitcheck_type:
                if self._page_width == -1:
                    self._page_width = int(
                        (self._cmd_read(0x8880000) & 2) == 0)

            else:
                if self._page_width == -1:
                    self._page_width = int(
                        (((self._cmd_read(0x8880000) >> 19) & 1) + 1) == 0)

            for _ in range(4):
                self._idcode <<= 8
                self._idcode |= (self._cmd2_read(0x2080000) & 0xff)

            self._cmd2_read(0x2080000)

        else:
            self._cmd2_write(0x8000000, 0xff)
            self._cmd2_write(0x8000000, 0x90)
            self._cmd2_write(0x8000004, 0x0)
            self._idcode = 0

            for _ in range(0x80):
                if (self._cmd_read(0x8090000) & 0x40) == 0:
                    break
                time.sleep(0.1)

            while (self._cmd_read(0x8090000) & 0x40) == 0 and not _DEBUG_CONTROLLER:
                pass #time.sleep(0.1)

            for _ in range(4):
                self._idcode <<= 8
                self._idcode |= (self._cmd2_read(0x8000008) & 0xff)

            if self._page_width == -1:
                self._page_width = 0

    def read(self, page: int):
        tempData = bytearray()
        tempSpare = bytearray()

        self._mem_write(0x809001c, self._mem_read(0x809001c) | 0x1)

        if self._is_axi:
            if self._page_size == 1:
                self._cmd_write(0x2b18000, (page << 16) & 0xffffffff)
                self._cmd_write(0x2b18000, ((page << 16) >> 32) & 0xffffffff)
            else:
                self._cmd_write(0x2800000, (page << 8) & 0xffffffff)
                self._cmd_write(0x2b18000, ((page << 8) >> 24) & 0xffffffff)

            for _ in range(0x800):
                if (self._mem_read(0x809001c) & 0x2) == 0:
                    break
                pass #time.sleep(0.01)

            while (self._mem_read(0x809001c) & 0x2) == 0 and not _DEBUG_CONTROLLER:
                pass

            tempData += self._mem_read(0x2298000,
                                       0x800 if self._page_size == 1 else 0x200)
            tempSpare += self._mem_read(0x2298000,
                                        0x40 if self._page_size == 1 else 0x10)
        else:
            if self._page_size == 0:
                if self._page_width == 0:
                    ''' First read '''
                    self._cmd2_write(0x8000000, 0x00)

                    self._cmd2_write(0x8000004, 0x00)
                    self._cmd2_write(0x8000004, page & 0xff)
                    self._cmd2_write(0x8000004, (page >> 8) & 0xff)
                    self._cmd2_write(0x8000004, (page >> 16) & 0xff)

                    for _ in range(0x400):
                        if (self._cmd_read(0x8090000) & 0x40) == 0:
                            break
                        pass #time.sleep(0.01)

                    while (self._cmd_read(0x8090000) & 0x40) == 0 and not _DEBUG_CONTROLLER:
                        pass

                    tempData += self._mem_read(0x2298000, 0x100)

                    ''' Second read '''
                    self._cmd2_write(0x8000000, 0x01)

                    self._cmd2_write(0x8000004, 0x00)
                    self._cmd2_write(0x8000004, page & 0xff)
                    self._cmd2_write(0x8000004, (page >> 8) & 0xff)
                    self._cmd2_write(0x8000004, (page >> 16) & 0xff)

                    for _ in range(0x400):
                        if (self._cmd_read(0x8090000) & 0x40) == 0:
                            break
                        pass #time.sleep(0.01)

                    while (self._cmd_read(0x8090000) & 0x40) == 0 and not _DEBUG_CONTROLLER:
                        pass

                    tempData += self._mem_read(0x2298000, 0x100)

                    ''' Spare read '''
                    self._cmd2_write(0x8000000, 0x50)

                    self._cmd2_write(0x8000004, 0x00)
                    self._cmd2_write(0x8000004, page & 0xff)
                    self._cmd2_write(0x8000004, (page >> 8) & 0xff)
                    self._cmd2_write(0x8000004, (page >> 16) & 0xff)

                    for _ in range(0x400):
                        if (self._cmd_read(0x8090000) & 0x40) == 0:
                            break
                        pass #time.sleep(0.01)

                    while (self._cmd_read(0x8090000) & 0x40) == 0 and not _DEBUG_CONTROLLER:
                        pass

                    tempSpare += self._mem_read(0x2298000, 0x10)

                else:
                    ''' First read '''
                    self._cmd2_write(0x8000000, 0x00)

                    self._cmd2_write(0x8000004, 0x00)
                    self._cmd2_write(0x8000004, page & 0xff)
                    self._cmd2_write(0x8000004, (page >> 8) & 0xff)
                    self._cmd2_write(0x8000004, (page >> 16) & 0xff)

                    for _ in range(0x400):
                        if (self._cmd_read(0x8090000) & 0x40) == 0:
                            break
                        pass #time.sleep(0.01)

                    while (self._cmd_read(0x8090000) & 0x40) == 0 and not _DEBUG_CONTROLLER:
                        pass

                    tempData += self._mem_read(0x2298000, 0x200)

                    ''' Spare read '''
                    self._cmd2_write(0x8000000, 0x50)

                    self._cmd2_write(0x8000004, 0x00)
                    self._cmd2_write(0x8000004, page & 0xff)
                    self._cmd2_write(0x8000004, (page >> 8) & 0xff)
                    self._cmd2_write(0x8000004, (page >> 16) & 0xff)

                    for _ in range(0x400):
                        if (self._cmd_read(0x8090000) & 0x40) == 0:
                            break
                        pass #time.sleep(0.01)

                    while (self._cmd_read(0x8090000) & 0x40) == 0 and not _DEBUG_CONTROLLER:
                        pass

                    tempSpare += self._mem_read(0x2298000, 0x10)

            else:
                self._cmd2_write(0x8000000, 0x00)

                self._cmd2_write(0x8000004, 0x00)
                self._cmd2_write(0x8000004, 0x00)
                self._cmd2_write(0x8000004, page & 0xff)
                self._cmd2_write(0x8000004, (page >> 8) & 0xff)
                self._cmd2_write(0x8000004, (page >> 16) & 0xff)

                self._cmd2_write(0x8000000, 0x30)

                for _ in range(0x400):
                    if (self._cmd_read(0x8090000) & 0x40) == 0:
                        break
                    pass #time.sleep(0.01)

                while (self._cmd_read(0x8090000) & 0x40) == 0 and not _DEBUG_CONTROLLER:
                    pass

                tempData += self._mem_read(0x2298000, 0x800)
                tempSpare += self._mem_read(0x2298000, 0x40)

        self._mem_write(0x809001c, self._mem_read(0x809001c) & 0xfe)

        return bytes(tempData), bytes(tempSpare), b""

    def write(self, page: int, data: typing.Union[bytes, bytearray]):
        raise NotImplementedError()

    def erase(self, page: int):
        raise NotImplementedError()

def _moduletest():
    global _DEBUG_CONTROLLER
    _DEBUG_CONTROLLER = True

    def dummy_cmd_read(offset):
        print(f"CMD READ {hex(offset)}")
        return 0x0

    def dummy_cmd_write(offset, value):
        print(f"CMD WRITE {hex(offset)} {hex(value)} {bin(value)}")
        
    def dummy_cmd_read2(offset):
        print(f"CMD READ2 {hex(offset)}")
        return 0x0

    def dummy_cmd_write2(offset, value):
        print(f"CMD WRITE2 {hex(offset)} {hex(value)} {bin(value)}")

    def dummy_mem_read(offset, size=1):
        print(f"MEM READ {hex(offset)} {hex(size)}")
        return 0xff if size <= 1 else b"\xff"*size

    def dummy_mem_write(offset, data):
        print(f"MEM WRITE {hex(offset)} {data}")
        pass

    print("-BCM-NANDC 512-8-")
    test = BCM2133NANDController(dummy_cmd_read, dummy_cmd_write, dummy_cmd_read2, dummy_cmd_write2, dummy_mem_read, dummy_mem_write, 0, 0)
    print("-READ-")
    print(test.read(0))
    
    print("-BCM-NANDC 512-16-")
    test = BCM2133NANDController(dummy_cmd_read, dummy_cmd_write, dummy_cmd_read2, dummy_cmd_write2, dummy_mem_read, dummy_mem_write, 0, 1)
    print("-READ-")
    print(test.read(0))
    
    print("-BCM-NANDC 2048-8-")
    test = BCM2133NANDController(dummy_cmd_read, dummy_cmd_write, dummy_cmd_read2, dummy_cmd_write2, dummy_mem_read, dummy_mem_write, 1, 0)
    print("-READ-")
    print(test.read(0))
    
    print("-BCM-NANDC 2048-16-")
    test = BCM2133NANDController(dummy_cmd_read, dummy_cmd_write, dummy_cmd_read2, dummy_cmd_write2, dummy_mem_read, dummy_mem_write, 1, 1)
    print("-READ-")
    print(test.read(0))
    
    