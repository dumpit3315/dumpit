from pyftdi import gpio
import time
import random
import typing
import sys
if sys.platform == "linux":
    import gpiod
    from gpiod.line import Value, Direction
    _GPIOD_SUPPORT = False  # TODO

else:
    _GPIOD_SUPPORT = False


class _FakeChipset(gpio.GpioAsyncController):
    def __init__(self):
        '''
        self.TDI = 0
        self.TDO = 1
        self.TMS = 2
        self.TCK = 3
        self.TRST = 4
        self.SRST = 5
        self.RTCK = 6        
        '''

        self.TDI = 2
        self.TDO = 0
        self.TMS = 3
        self.TCK = 5
        self.TRST = 7
        self.SRST = 4
        self.RTCK = 1

        self.IDCODE = 0x3f0f0f0f  # ARM7TDMI IDCODE
        self.IR_LENGTH = 4  # Assume ARM7TDMI/ARM926 spec

        self.jtag_pins = 0
        self.jtag_state = 0
        self.instruction = 0
        self.dr_shift = 0
        self.ir_shift = 0

        self.ir_code = 0

        self.jtag_dir = 0
        self.trace_reseting = False
        self.tck_on = False

        self.tdo_temp = 0
        self._SR_TEMP = 0
        self._SR_LEN = 0

    def configure(self, addr, dir, **kwargs):
        self.jtag_dir = dir
        kwargs = dict(kwargs)

        self.jtag_dir = dir
        self.jtag_pins = kwargs.get("initial", 0)

    def read(self):
        return self.jtag_pins

    # Spec from https://ynzinfo.tripod.com/JTAG/ids_jtag.htm
    # Based on https://medium.com/@aliaksandr.kavalchuk/diving-into-jtag-protocol-part-1-overview-fbdc428d3a16
    def write(self, out: int):
        self.jtag_pins = out

        if self.jtag_pins & (1 << self.TCK) and not self.tck_on:  # Active pin is TCK
            self.tck_on = True
            self.jtag_pins |= (1 << self.RTCK)  # Mirror RTCK

            # Per JTAG Spec, TDI and TMS were sampled on the rising edge, and allows shift register operations to be done.
            if not self.trace_reseting:  # TRST is HIGH, do something
                if self.jtag_state == 5:  # If the state is Shift-DR, output regardless of TMS
                    self.tdo_temp = self._SR_TEMP & 1
                    self._SR_TEMP >>= 1

                    if self.instruction == 0:
                        self._SR_TEMP |= (1 << (self._SR_LEN - 1))

                    elif self.instruction == 1:  # Bypass, directly connect TDI to TDO
                        if self.jtag_pins & (1 << self.TDI):
                            self.tdo_temp = 1

                        else:
                            self.tdo_temp = 0

                elif self.jtag_state == 11:  # If the state is Shift-IR, output regardless of TMS
                    self.tdo_temp = self._SR_TEMP & 1
                    self._SR_TEMP >>= 1

                    if self.jtag_pins & (1 << self.TDI):
                        self._SR_TEMP |= (1 << (self._SR_LEN - 1))

                if self.jtag_pins & (1 << self.TMS):
                    if self.jtag_state == 0:  # Idle -> Select DR
                        self.jtag_state = 1

                    elif self.jtag_state == 1:  # Select DR -> Select IR
                        self.jtag_state = 2

                    elif self.jtag_state == 2:  # Select IR -> Reset
                        self.jtag_state = 3
                        self.instruction = 0
                        self.dr_shift = 0
                        self.ir_shift = 0

                    # Capture/Shift DR -> Exit1 DR
                    elif self.jtag_state in [4, 5]:
                        self.jtag_state = 6

                    elif self.jtag_state in [6, 8]:  # Exit DR -> Update DR
                        self.jtag_state = 9

                    elif self.jtag_state == 7:  # Pause DR -> Exit2 DR
                        self.jtag_state = 8

                    elif self.jtag_state == 9:  # Update DR -> Select DR
                        self.jtag_state = 1
                        self.dr_shift = 0

                    # Capture/Shift IR -> Exit1 IR
                    elif self.jtag_state in [10, 11]:
                        self.jtag_state = 12

                    elif self.jtag_state in [12, 14]:  # Exit IR -> Update IR
                        self.jtag_state = 15

                    elif self.jtag_state == 13:  # Pause IR -> Exit2 DR
                        self.jtag_state = 14

                    elif self.jtag_state == 15:  # Update IR -> Select DR
                        self.jtag_state = 1
                        self.ir_code = 0
                        self.ir_shift = 0

                else:
                    if self.jtag_state == 3:  # Reset -> Idle
                        self.jtag_state = 0

                    elif self.jtag_state == 1:  # Select DR -> Capture DR
                        self.jtag_state = 4
                        if self.instruction == 0:  # IDCODE
                            if self.dr_shift < 32:
                                self._SR_TEMP = self.IDCODE
                                self._SR_LEN = 32

                        elif self.instruction == 1:  # BYPASS
                            self._SR_TEMP = 0
                            self._SR_LEN = 1

                    elif self.jtag_state == 4:  # Capture DR -> Shift DR
                        self.jtag_state = 5

                        self.tdo_temp = self._SR_TEMP & 1
                        self._SR_TEMP >>= 1

                        if self.instruction == 0:
                            self._SR_TEMP |= (1 << (self._SR_LEN - 1))

                        elif self.instruction == 1:
                            self.tdo_temp = 0

                    elif self.jtag_state == 6:  # Exit1 DR -> Pause DR
                        self.jtag_state = 7

                    elif self.jtag_state == 8:  # Exit2 DR -> Shift DR
                        self.jtag_state = 5

                        self.tdo_temp = self._SR_TEMP & 1
                        self._SR_TEMP >>= 1

                        if self.instruction == 0:
                            self._SR_TEMP |= (1 << (self._SR_LEN - 1))

                        elif self.instruction == 1:  # Bypass, directly connect TDI to TDO
                            if self.jtag_pins & (1 << self.TDI):
                                self.tdo_temp = 1

                            else:
                                self.tdo_temp = 0

                    elif self.jtag_state == 9:  # Update DR -> Idle
                        self.jtag_state = 0
                        self.dr_shift = 0

                    elif self.jtag_state == 2:  # Select IR -> Capture IR
                        self.jtag_state = 10
                        self._SR_TEMP = 0b01
                        self._SR_LEN = self.IR_LENGTH

                    elif self.jtag_state == 10:  # Capture IR -> Shift IR
                        self.jtag_state = 11

                        self.tdo_temp = self._SR_TEMP & 1
                        self._SR_TEMP >>= 1

                        if self.jtag_pins & (1 << self.TDI):
                            self._SR_TEMP |= (1 << (self._SR_LEN - 1))

                    elif self.jtag_state == 12:  # Exit1 IR -> Pause IR
                        self.jtag_state = 13

                    elif self.jtag_state == 14:  # Exit2 IR -> Shift IR
                        self.jtag_state = 11
                        self.tdo_temp = self._SR_TEMP & 1
                        self._SR_TEMP >>= 1

                        if self.jtag_pins & (1 << self.TDI):
                            self._SR_TEMP |= (1 << (self._SR_LEN - 1))

                    elif self.jtag_state == 15:  # Update IR -> Idle
                        self.jtag_state = 0
                        self.ir_code = 0
                        self.ir_shift = 0

        elif not self.jtag_pins & (1 << self.TCK) and self.tck_on:  # TCK isn't active
            self.tck_on = False
            self.jtag_pins &= ~(1 << self.RTCK)  # Mirror RTCK

            if self.jtag_state == 15:  # IR applies on falling edge
                if self._SR_TEMP == (2**self.IR_LENGTH)-1:
                    self.instruction = 1

                elif self._SR_TEMP == (2**self.IR_LENGTH)-2:
                    self.instruction = 0

                else:
                    raise ValueError(
                        f"Unknown JTAG register: {bin(self._SR_TEMP)}")

            # Per JTAG spec, TDO was outputed falling edge
            if self.tdo_temp:
                self.jtag_pins |= (1 << self.TDO)

            else:
                self.jtag_pins &= ~(1 << self.TDO)

        if not self.jtag_pins & (1 << self.TRST) and not self.trace_reseting:  # TRST is low
            self.trace_reseting = True

        elif self.jtag_pins & (1 << self.TRST) and self.trace_reseting:
            self.trace_reseting = False
            self.instruction = 0
            self.jtag_state = 0
            self.dr_shift = 0
            self.ir_shift = 0

    def set_direction(self, pins: int, direction: int):
        assert direction <= pins
        self.jtag_dir &= ~pins
        self.jtag_dir |= (pins & direction)

    def close(self):
        pass


DELAY = 500
MAX_DEVICES = 16


def _msleep(dur: int):
    s = time.perf_counter_ns()
    while time.perf_counter_ns() < (s+(dur*1000)):
        pass


def _pulse_tck(dev: typing.Union[gpio.GpioAsyncController, gpio.GpioMpsseController], tck: int):
    dev.write(dev.read() & ~(1 << tck))
    _msleep(DELAY)
    dev.write(dev.read() | (1 << tck))


def _pulse_tdi(dev: typing.Union[gpio.GpioAsyncController, gpio.GpioMpsseController], tck: int, tdi: int, value: int):
    dev.write(dev.read() & ~(1 << tck))
    _msleep(DELAY)

    if value:
        dev.write(dev.read() | (1 << tdi))

    else:
        dev.write(dev.read() & ~(1 << tdi))

    dev.write(dev.read() | (1 << tck))


def _pulse_tdi_rising(dev: typing.Union[gpio.GpioAsyncController, gpio.GpioMpsseController], tck: int, tdi: int, value: int):
    if value:
        dev.write(dev.read() | (1 << tdi))

    else:
        dev.write(dev.read() & ~(1 << tdi))

    dev.write(dev.read() | (1 << tck))
    _msleep(DELAY)
    dev.write(dev.read() & ~(1 << tck))


def _pulse_tdo(dev: typing.Union[gpio.GpioAsyncController, gpio.GpioMpsseController], tck: int, tdo: int):
    dev.write(dev.read() & ~(1 << tck))
    _msleep(DELAY)
    temp = (dev.read() >> tdo) & 1
    dev.write(dev.read() | (1 << tck))
    return temp


def _write_tap(dev: typing.Union[gpio.GpioAsyncController, gpio.GpioMpsseController], tck: int, tms: int, tap: str):
    for bit in list(tap):
        assert bit in ["1", "0"]
        dev.write(dev.read() & ~(1 << tck))
        _msleep(DELAY)

        if bit == "1":
            dev.write(dev.read() | (1 << tms))

        else:
            dev.write(dev.read() & ~(1 << tms))

        dev.write(dev.read() | (1 << tck))


def _do_write_read(dev: typing.Union[gpio.GpioAsyncController, gpio.GpioMpsseController], tck: int, tdi: int, tdo: int, value: int):
    temp = 0

    # Lower TCK for rising edge pulse first
    dev.write(dev.read() & ~(1 << tck))
    for i in range(32):
        _pulse_tdi_rising(dev, tck, tdi, (value >> i) & 1)
        _msleep(DELAY)

        if dev.read() & (1 << tdo):
            temp |= (1 << i)

    return temp


if _GPIOD_SUPPORT:
    def _pulse_tck_gpiod(dev: gpiod.LineRequest, tck: int):
        _msleep(DELAY)
        dev.set_value(tck, Value.INACTIVE)
        dev.set_value(tck, Value.ACTIVE)

    def _pulse_tdi_gpiod(dev: gpiod.LineRequest, tck: int, tdi: int, value: int):
        _msleep(DELAY)
        dev.set_value(tck, Value.INACTIVE)
        dev.set_value(tdi, value)
        dev.set_value(tck, Value.ACTIVE)

    def _pulse_tdo_gpiod(dev: gpiod.LineRequest, tck: int, tdo: int):
        _msleep(DELAY)
        dev.set_value(tck, Value.INACTIVE)
        temp = dev.get_value(tdo)
        dev.set_value(tck, Value.ACTIVE)
        return temp

    def _write_tap_gpiod(dev: gpiod.LineRequest, tck: int, tms: int, tap: str):
        for bit in list(tap):
            assert bit in ["1", "0"]
            _msleep(DELAY)
            dev.set_value(tck, Value.INACTIVE)
            dev.set_value(tms, int(bit == "1"))
            dev.set_value(tck, Value.ACTIVE)

    def _do_write_read_gpiod(dev: gpiod.LineRequest, tck: int, tdi: int, tdo: int, value: int):
        temp = 0
        for i in range(32):
            _pulse_tdi(dev, tck, tdi, (value >> i) & 1)
            _msleep(DELAY)
            temp |= (dev.get_value(tdo) << i)

        return temp


def find_jtag_idcode(src: str, dummy: bool = False, mpsse: bool = False, max: int = 1):
    possible_combinations = []

    inDevice = (gpio.GpioMpsseController(
    ) if mpsse else gpio.GpioAsyncController()) if not dummy else _FakeChipset()
    inDevice.configure(src, 0xffff if mpsse else 0xff,
                       initial=0xffff if mpsse else 0xff)

    for tdo in range(16 if mpsse else 8):
        for tck in range(16 if mpsse else 8):
            if tck == tdo:
                continue
            for tms in range(16 if mpsse else 8):
                if tms in [tdo, tck]:
                    continue
                inDevice.set_direction(
                    0xffff if mpsse else 0xff, (1 << tck) | (1 << tms))
                inDevice.write(0xffff if mpsse else 0xff)
                idcodes = []

                _write_tap(inDevice, tck, tms, "11111")  # Restore Idle
                # Enter to Shift DR
                _write_tap(inDevice, tck, tms, "111110100")

                for x in range(MAX_DEVICES):
                    idcodes.append(0)
                    for s in range(32):
                        # Low, outputs TDO, High shifts the content
                        _pulse_tck(inDevice, tck)
                        _msleep(DELAY)

                        if inDevice.read() & (1 << tdo):
                            idcodes[x] |= 1 << s

                    if idcodes[x] == 0xffffffff or not idcodes[x] & 1:
                        idcodes.pop(x)
                        break

                if len(idcodes) > 0:
                    possible_ntrst = []

                    for ntrst in range(16 if mpsse else 8):
                        if ntrst in [tdo, tck, tms]:
                            continue

                        inDevice.set_direction(
                            0xffff if mpsse else 0xff, (1 << tck) | (1 << tms) | (1 << ntrst))
                        inDevice.write(
                            (0xffff if mpsse else 0xff) & ~(1 << ntrst))

                        _msleep(DELAY)

                        _write_tap(inDevice, tck, tms, "11111")  # Restore Idle
                        # Enter to Shift DR
                        _write_tap(inDevice, tck, tms, "111110100")

                        new_idcode = 0
                        for s in range(32):
                            _pulse_tck(inDevice, tck)
                            _msleep(DELAY)

                            if inDevice.read() & (1 << tdo):
                                new_idcode |= 1 << s

                        if idcodes[0] != new_idcode:
                            possible_ntrst.append(ntrst)

                    possible_combinations.append(
                        {"tdo": tdo, "tck": tck, "tms": tms, "possible_ntrst": possible_ntrst, "idcodes": [hex(x) for x in idcodes]})

                    if len(possible_combinations) >= max:
                        inDevice.close()
                        return possible_combinations

    inDevice.close()
    return possible_combinations


def find_jtag_bypass(src: str, dummy: bool = False, mpsse: bool = False, max: int = 1, known_tdo: int = -1, known_tck: int = -1, known_tms: int = -1):
    possible_combinations = []

    inDevice = (gpio.GpioMpsseController(
    ) if mpsse else gpio.GpioAsyncController()) if not dummy else _FakeChipset()
    inDevice.configure(src, 0xffff if mpsse else 0xff,
                       initial=0xffff if mpsse else 0xff)

    for tdi in range(16 if mpsse else 8):
        for tdo in range(16 if mpsse else 8):
            if known_tdo != -1 and tdo != known_tdo:
                continue
            if tdo == tdi:
                continue
            for tck in range(16 if mpsse else 8):
                if known_tck != -1 and tck != known_tck:
                    continue
                if tck in [tdi, tdo]:
                    continue
                for tms in range(16 if mpsse else 8):
                    if known_tms != -1 and tms != known_tms:
                        continue
                    if tms in [tdi, tdo, tck]:
                        continue

                    inDevice.set_direction(
                        0xffff if mpsse else 0xff, (1 << tdi) | (1 << tck) | (1 << tms))
                    inDevice.write(0xffff if mpsse else 0xff)

                    _write_tap(inDevice, tck, tms, "11111")  # Restore Idle
                    # Enter Shift IR
                    _write_tap(inDevice, tck, tms, "1111101100")

                    for _ in range(MAX_DEVICES):
                        for _ in range(32):
                            _pulse_tdi(inDevice, tck, tdi, 1)

                    _write_tap(inDevice, tck, tms, "11100")

                    for _ in range(MAX_DEVICES):
                        _pulse_tdi(inDevice, tck, tdi, 1)

                    _msleep(DELAY)
                    inDevice.write(inDevice.read() & ~(1 << tdi))

                    devices = 0

                    for _ in range(MAX_DEVICES):
                        if (_pulse_tdo(inDevice, tck, tdo) == 0):
                            break
                        devices += 1

                    if devices >= MAX_DEVICES or devices <= 0:
                        continue

                    _write_tap(inDevice, tck, tms, "11111")  # Restore Idle
                    # Enter Shift IR
                    _write_tap(inDevice, tck, tms, "1111101100")

                    for _ in range(devices):
                        for _ in range(32):
                            _pulse_tdi(inDevice, tck, tdi, 1)

                    _write_tap(inDevice, tck, tms, "110100")  # Enter Shift DR

                    expected = random.randint(0, (2**32)-1)
                    actual = _do_write_read(inDevice, tck, tdi, tdo, expected)

                    if actual == expected:
                        possible_ntrst = []
                        for ntrst in range(16 if mpsse else 8):
                            if ntrst in [tdi, tdo, tck, tms]:
                                continue
                            inDevice.set_direction(0xffff if mpsse else 0xff, (1 << tdi) | (
                                1 << tck) | (1 << tms) | (1 << ntrst))
                            inDevice.write(
                                (0xffff if mpsse else 0xff) & ~(1 << ntrst))

                            _msleep(DELAY)

                            # Restore Idle
                            _write_tap(inDevice, tck, tms, "11111")
                            # Enter Shift IR
                            _write_tap(inDevice, tck, tms, "1111101100")

                            for _ in range(MAX_DEVICES):
                                for _ in range(32):
                                    _pulse_tdi(inDevice, tck, tdi, 1)

                            _write_tap(inDevice, tck, tms, "11100")

                            for _ in range(MAX_DEVICES):
                                _pulse_tdi(inDevice, tck, tdi, 1)

                            _msleep(DELAY)
                            inDevice.write(inDevice.read() & ~(1 << tdi))

                            devices_2 = 0

                            for _ in range(MAX_DEVICES):
                                if (_pulse_tdo(inDevice, tck, tdo) == 0):
                                    break
                                devices_2 += 1

                            if devices != devices_2 and devices_2 <= MAX_DEVICES:
                                possible_ntrst.append(ntrst)

                        possible_combinations.append(
                            {"tdi": tdi, "tdo": tdo, "tck": tck, "tms": tms, "possible_ntrst": possible_ntrst})

                        if len(possible_combinations) >= max:
                            inDevice.close()
                            return possible_combinations

    inDevice.close()
    return possible_combinations


def find_jtag_rtck(src: str, dummy: bool = False, mpsse: bool = False, known_tck: int = -1):
    possible_rtck = []
    inDevice = (gpio.GpioMpsseController(
    ) if mpsse else gpio.GpioAsyncController()) if not dummy else _FakeChipset()
    inDevice.configure(src, 0xffff if mpsse else 0xff,
                       initial=0xffff if mpsse else 0xff)

    for tck in range(16 if mpsse else 8):
        if known_tck != -1 and tck != known_tck:
            continue
        for rtck in range(16 if mpsse else 8):
            if rtck == tck:
                continue

            inDevice.set_direction(0xffff if mpsse else 0xff, (1 << tck))
            inDevice.write(0xffff if mpsse else 0xff)

            rtck_match = 0
            rtck_bit = 0

            for _ in range(30):
                rtck_bit = 1 if not rtck_bit else 0
                if rtck_bit:
                    inDevice.write(inDevice.read() | (1 << tck))

                else:
                    inDevice.write(inDevice.read() & ~(1 << tck))

                _msleep(DELAY)

                if rtck_bit:
                    if inDevice.read() & (1 << rtck):
                        rtck_match += 1

                else:
                    if not inDevice.read() & (1 << rtck):
                        rtck_match += 1

            if rtck_match >= 30:
                possible_rtck.append(rtck)

    return possible_rtck


if _GPIOD_SUPPORT:
    def set_all_pins_high(chip: gpiod.Chip, lines: int):
        for l in range(lines):
            with chip.request_lines({l: gpiod.LineSettings(Direction.OUTPUT, output_value=Value.ACTIVE)}, "Findit"):
                pass

    def find_jtag_idcode_gpiod(chip: int, max: int = 1):
        possible_combinations = []

        with gpiod.Chip(f"/dev/gpiochip{chip}") as inDevice:
            lineInfo = inDevice.get_info()

            for tdo in range(lineInfo.num_lines):
                for tck in range(lineInfo.num_lines):
                    if tck == tdo:
                        continue
                    for tms in range(lineInfo.num_lines):
                        if tms in [tdo, tck]:
                            continue
                        set_all_pins_high(inDevice, lineInfo.num_lines)
                        isFound = False
                        idcodes = []

                        with inDevice.request_lines({
                            tdo: gpiod.LineSettings(Direction.INPUT, output_value=Value.ACTIVE),
                            tck: gpiod.LineSettings(Direction.OUTPUT, output_value=Value.ACTIVE),
                            tms: gpiod.LineSettings(
                                Direction.OUTPUT, output_value=Value.ACTIVE)
                        }, "Findit") as line:
                            # Restore Idle
                            _write_tap_gpiod(line, tck, tms, "11111")
                            # Enter to Shift DR
                            _write_tap_gpiod(line, tck, tms, "111110100")

                            for x in range(MAX_DEVICES):
                                idcodes.append(0)
                                for s in range(32):
                                    _pulse_tck_gpiod(line, tck)
                                    _msleep(DELAY)

                                    idcodes[x] |= line.get_value(tdo) << s

                                if idcodes[x] == 0xffffffff or not idcodes[x] & 1:
                                    idcodes.pop(x)
                                    break

                            if len(idcodes) > 0:
                                isFound = True
                                break

                        if isFound:
                            possible_ntrst = []

                            for ntrst in range(lineInfo.num_lines):
                                if ntrst in [tdo, tck, tms]:
                                    continue
                                set_all_pins_high(inDevice, lineInfo.num_lines)

                                with inDevice.request_lines({
                                    tdo: gpiod.LineSettings(Direction.INPUT, output_value=Value.ACTIVE),
                                    tck: gpiod.LineSettings(Direction.OUTPUT, output_value=Value.ACTIVE),
                                    tms: gpiod.LineSettings(Direction.OUTPUT, output_value=Value.ACTIVE),
                                    ntrst: gpiod.LineSettings(
                                        Direction.OUTPUT, output_value=Value.INACTIVE)
                                }, "Findit") as line:
                                    _msleep(DELAY)

                                    # Restore Idle
                                    _write_tap_gpiod(line, tck, tms, "11111")
                                    # Enter to Shift DR
                                    _write_tap_gpiod(
                                        line, tck, tms, "111110100")

                                    new_idcode = 0
                                    for s in range(32):
                                        _pulse_tck_gpiod(line, tck)
                                        _msleep(DELAY)

                                        new_idcode |= line.get_value(tdo) << s

                                    if idcodes[0] != new_idcode:
                                        possible_ntrst.append(ntrst)

                            possible_combinations.append(
                                {"tdo": tdo, "tck": tck, "tms": tms, "possible_ntrst": possible_ntrst, "idcodes": [hex(x) for x in idcodes]})

                            if len(possible_combinations) >= max:
                                return possible_combinations

        return possible_combinations

    def find_jtag_bypass_gpiod(chip: int, max: int = 1, known_tdo: int = -1, known_tck: int = -1, known_tms: int = -1):
        possible_combinations = []

        inDevice = (gpio.GpioMpsseController(
        ) if mpsse else gpio.GpioAsyncController()) if not dummy else _FakeChipset()
        inDevice.configure(src, 0xffff if mpsse else 0xff,
                           initial=0xffff if mpsse else 0xff)

        for tdi in range(16 if mpsse else 8):
            for tdo in range(16 if mpsse else 8):
                if known_tdo != -1 and tdo != known_tdo:
                    continue
                if tdo == tdi:
                    continue
                for tck in range(16 if mpsse else 8):
                    if known_tck != -1 and tck != known_tck:
                        continue
                    if tck in [tdi, tdo]:
                        continue
                    for tms in range(16 if mpsse else 8):
                        if known_tms != -1 and tms != known_tms:
                            continue
                        if tms in [tdi, tdo, tck]:
                            continue

                        inDevice.set_direction(
                            0xffff if mpsse else 0xff, (1 << tdi) | (1 << tck) | (1 << tms))
                        inDevice.write(0xffff if mpsse else 0xff)

                        _write_tap(inDevice, tck, tms, "11111")  # Restore Idle
                        # Enter Shift IR
                        _write_tap(inDevice, tck, tms, "1111101100")

                        for _ in range(MAX_DEVICES):
                            for _ in range(32):
                                _pulse_tdi(inDevice, tck, tdi, 1)

                        _write_tap(inDevice, tck, tms, "11100")

                        for _ in range(MAX_DEVICES):
                            _pulse_tdi(inDevice, tck, tdi, 1)

                        _msleep(DELAY)
                        inDevice.write(inDevice.read() & ~(1 << tdi))

                        devices = 0

                        for _ in range(MAX_DEVICES):
                            if (_pulse_tdo(inDevice, tck, tdo) == 0):
                                break
                            devices += 1

                        if devices >= MAX_DEVICES or devices <= 0:
                            continue

                        _write_tap(inDevice, tck, tms, "11111")  # Restore Idle
                        # Enter Shift IR
                        _write_tap(inDevice, tck, tms, "1111101100")

                        for _ in range(devices):
                            for _ in range(32):
                                _pulse_tdi(inDevice, tck, tdi, 1)

                        # Enter Shift DR
                        _write_tap(inDevice, tck, tms, "110100")

                        expected = random.randint(0, (2**32)-1)
                        actual = _do_write_read(
                            inDevice, tck, tdi, tdo, expected)

                        if actual == expected:
                            possible_ntrst = []
                            for ntrst in range(16 if mpsse else 8):
                                if ntrst in [tdi, tdo, tck, tms]:
                                    continue
                                inDevice.set_direction(0xffff if mpsse else 0xff, (1 << tdi) | (
                                    1 << tck) | (1 << tms) | (1 << ntrst))
                                inDevice.write(
                                    (0xffff if mpsse else 0xff) & ~(1 << ntrst))

                                _msleep(DELAY)

                                # Restore Idle
                                _write_tap(inDevice, tck, tms, "11111")
                                # Enter Shift IR
                                _write_tap(inDevice, tck, tms, "1111101100")

                                for _ in range(MAX_DEVICES):
                                    for _ in range(32):
                                        _pulse_tdi(inDevice, tck, tdi, 1)

                                _write_tap(inDevice, tck, tms, "11100")

                                for _ in range(MAX_DEVICES):
                                    _pulse_tdi(inDevice, tck, tdi, 1)

                                _msleep(DELAY)
                                inDevice.write(inDevice.read() & ~(1 << tdi))

                                devices_2 = 0

                                for _ in range(MAX_DEVICES):
                                    if (_pulse_tdo(inDevice, tck, tdo) == 0):
                                        break
                                    devices_2 += 1

                                if devices != devices_2 and devices_2 <= MAX_DEVICES:
                                    possible_ntrst.append(ntrst)

                            possible_combinations.append(
                                {"tdi": tdi, "tdo": tdo, "tck": tck, "tms": tms, "possible_ntrst": possible_ntrst})

                            if len(possible_combinations) >= max:
                                inDevice.close()
                                return possible_combinations

        inDevice.close()
        return possible_combinations

    def find_jtag_rtck_gpiod(chip: int, known_tck: int = -1):
        possible_rtck = []

        with gpiod.Chip(f"/dev/gpiochip{chip}") as inDevice:
            lineInfo = inDevice.get_info()

            for tck in range(lineInfo.num_lines):
                if known_tck != -1 and tck != known_tck:
                    continue
                for rtck in range(lineInfo.num_lines):
                    if rtck == tck:
                        continue
                    set_all_pins_high(inDevice, lineInfo.num_lines)

                    with inDevice.request_lines({
                        tck: gpiod.LineSettings(Direction.OUTPUT, output_value=Value.ACTIVE),
                        rtck: gpiod.LineSettings(
                            Direction.OUTPUT, output_value=Value.ACTIVE)
                    }, "Findit") as line:
                        rtck_match = 0
                        rtck_bit = 0

                        for _ in range(30):
                            rtck_bit = 1 if not rtck_bit else 0
                            line.set_value(tck, rtck_bit)

                            _msleep(DELAY)

                            if line.get_value(rtck) == rtck_bit:
                                rtck_match += 1

                        if rtck_match >= 30:
                            possible_rtck.append(rtck)

        return possible_rtck

if __name__ == "__main__":
    print(find_jtag_idcode("", True))
    print(find_jtag_bypass("", True, known_tdo=0, known_tck=5, known_tms=3))
    print(find_jtag_rtck("", True, known_tck=5))

    print(find_jtag_idcode("ftdi:1"))
