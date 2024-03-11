import wx
import wx.richtext
import wx.stc
from res import main
from res import forwardDialog
from res import ft232r_pinconfig
from res import ft232h_pinconfig
from res import resetDelay
from res import nandControlConfig
from res import nandInitScript
from res import targetReadConfig
from res import metadataUserEditor
import os
import sys
import const
import subprocess
import threading
import queue
import contextlib
import socketio
import socketio.exceptions
import time
import re
import libfindit
import traceback
import json
import requests
import gc
import uuid
import platform
import intelhex
import datetime
import random
import hashlib
from controller import qcom_nandregs
from controller import common_nandregs
from controller import bcm_nandregs
from controller import pxa3_nandregs
from controller import pnx_nandregs
import tempfile
import io
import struct
import typing
import getpass
import pathlib

os.environ["WXSUPPRESS_SIZER_FLAGS_CHECK"] = "1"
_PTRACKING = queue.Queue()
_PTRACKCOUNT = {}

# Unix, Windows and old Macintosh end-of-line
newlines = [b"\n", b"\r\n", b"\r"]


def _unbuffered(proc, stream="stdout"):
    stream = getattr(proc, stream)
    with contextlib.closing(stream):
        while True:
            out = []
            last = stream.read(1)
            # Don't loop forever
            if last == b"" and proc.poll() is not None:
                break
            while last not in newlines:
                # Don't loop forever
                if last == b"" and proc.poll() is not None:
                    break
                out.append(last)
                last = stream.read(1)
            out = b"".join(out)
            yield out


def get_arch_platform():
    """
    Finds if the platform is 32 or 64 bits
    Several different ways are tried in case one fails
    """
    try:
        import platform

        archi_bits = 64 if platform.architecture()[0] == "64bit" else 32
        return archi_bits
    except:
        pass
    try:
        import struct

        archi_bits = struct.calcsize("P") * 8
        return archi_bits
    except:
        pass
    try:
        import ctypes

        archi_bits = ctypes.sizeof(ctypes.c_voidp) * 8
        return archi_bits
    except:
        pass
    try:
        import sys

        archi_bits = 64 if sys.maxsize > 2**32 else 32
        return archi_bits
    except:
        pass
    # default to 32 (is this safe)?
    return 32


def getOCDExec():
    if os.path.exists(
        os.path.join(
            os.path.dirname(__file__),
            f"ocd/{sys.platform}-{get_arch_platform()}/bin/openocd",
        )
    ):
        return os.path.join(
            os.path.dirname(__file__),
            f"ocd/{sys.platform}-{get_arch_platform()}/bin/openocd",
        )

    elif os.path.exists(
        os.path.join(
            os.path.dirname(__file__),
            f"ocd/{sys.platform}-{get_arch_platform()}/bin/openocd.exe",
        )
    ):
        return os.path.join(
            os.path.dirname(__file__),
            f"ocd/{sys.platform}-{get_arch_platform()}/bin/openocd.exe",
        )

    return os.path.join(f"ocd/{sys.platform}-{get_arch_platform()}/bin/openocd")


def _msleep(dur: int):
    s = time.perf_counter_ns()
    while time.perf_counter_ns() < (s + (dur * 1000)):
        pass


def doTrackThread(user_id, action, openocd_version, config, **kwargs):
    try:
        res = requests.post(
            "https://dumpit.ucomsite.my.id/analytics/track",
            json={
                "user_id": user_id,
                "action": action,
                "dumpit_version": const.DUMPIT_VERSION,
                "python_version": sys.version,
                "openocd_version": openocd_version,
                "os": f"{platform.system()} {platform.version()}",
                "config": config,
                **kwargs,
            },
            timeout=5,
        )

        assert (
            res.status_code >= 200 and res.status_code <= 299
        ), f"{res.status_code} {res.reason}"
        _PTRACKING.put(action)

    except Exception:
        if True:
            print("unable to track:")
            traceback.print_exc()


"""
class ForwardApp(forwardDialog.forwardDialog):
    def __init__(self, parent, token):
        super().__init__(parent)
        self._ws_parent: MainApp = parent

        self.tPin.SetValue(token)
        self.status.Value = ""
        self._isConnect = False
        self._ocd = None
        self._logThreadQueue = queue.Queue()
        self._wsThreadQueue = queue.Queue()
        self._logThread = None
        self._wsThread = threading.Thread(target=self._doWSLoop)
        self._wsThread.daemon = True

        self._wsThread.start()

    def _doWSLoop(self):
        while True:
            try:
                self._wsThreadQueue.put(self._ws_parent._sio.receive(1))

            except socketio.exceptions.TimeoutError:
                pass

            except Exception:
                break

    def _ocdSendCommand(self, cmd: str):
        if self._ws_parent._debug_logs:
            print(f"EXEC {cmd}")

        if self._ocd and self._ocd.poll() is None:
            self._ocd.stdin.write(cmd.encode("latin-1") + b"\x1a")
            self._ocd.stdin.flush()

            resTemp = bytearray()
            while True:
                t = self._ocd.stdout.read(1)
                if t in [b"\x1a", b""]:
                    break

                resTemp += t

            return resTemp.decode("latin-1")

        else:
            return ""

    def _doLogging(self):
        for l in _unbuffered(self._ocd, "stderr"):
            try:
                self._logThreadQueue.put(l.decode("utf-8"))

            except Exception:
                pass

    def doLoop(self, event):
        try:
            if not self._ws_parent._sio.connected:
                if self._isConnect and self._ocd.poll() is None:
                    self._ocd.terminate()

                self._ws_parent._doAnalytics("disconnect", reason=1)

                self.Unbind(wx.EVT_IDLE)
                return self.EndModal(0)

            q = self._wsThreadQueue.get_nowait()

            if q[0] == "forward_client_connected":
                INIT_CMD = getInitCmd(self._ws_parent)
                self._ws_parent._doAnalytics("connect", type=1)

                self.tPin.Hide()
                self.lPin.Hide()

                self.status.Show()
                self.status.Value = f'Command-line arguments: openocd -c "{INIT_CMD}"\n\n'

                self.Layout()

                self._isConnect = True
                self._ocd = subprocess.Popen([getOCDExec(
                ), "-c", INIT_CMD], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                self._ocdSendCommand("")

                self._logThread = threading.Thread(target=self._doLogging)
                self._logThread.daemon = True

                self._logThread.start()

            elif q[0] == "data":
                self._ws_parent._sio.emit("data", self._ocdSendCommand(q[1]))
                
            elif q[0] == "command":
                pass

        except queue.Empty:
            pass

        if self._isConnect and self._ocd:
            try:
                p = self._logThreadQueue.get_nowait()

                if not p.startswith("0x"):
                    self.status.AppendText(p + "\n")
                    self.status.ShowPosition(self.status.GetLastPosition())

                self._ws_parent._sio.emit("log", p)

            except queue.Empty:
                if self._ocd.poll() is not None:
                    self._ws_parent._sio.call("bye", "", timeout=30)
                    self._ws_parent._sio.disconnect()

    def doStop(self, event):
        self._ws_parent._sio.call("bye", "", timeout=30)
        self._ws_parent._sio.disconnect()
"""


class ForwardApp(forwardDialog.forwardDialog):
    def __init__(self, parent, token):
        super().__init__(parent)
        self._ws_parent: MainApp = parent

        self.tPin.SetValue(token)
        self.status.Value = ""

        self._wsThreadQueue = queue.Queue()

        self._wsThread = threading.Thread(target=self._doWSLoop)
        self._wsThread.daemon = True

        self._loop_running = True
        self._wsThread.start()

    def _doWSLoop(self):
        while self._loop_running:
            try:
                self._wsThreadQueue.put(self._ws_parent._sio.receive(1))

            except socketio.exceptions.TimeoutError:
                pass

            except Exception:
                break

    def doLoop(self, event):
        try:
            if not self._ws_parent._sio.connected:
                self._ws_parent._doAnalytics("disconnect", reason=1)
                self.Unbind(wx.EVT_IDLE)
                self._loop_running = False

                if self._wsThread:
                    self._wsThread.join(15)
                return self.EndModal(0)

            q = self._wsThreadQueue.get_nowait()

            if q[0] == "forward_client_connected":
                self._ws_parent._reconnect_token = q[1]["reconnect_token"]
                self.bConnect.Enable(1)

                self.Unbind(wx.EVT_IDLE)
                self._loop_running = False

                if self._wsThread:
                    self._wsThread.join(15)

                self.lPin.Show(False)
                self.tPin.Show(False)

                self.lConnect.Show()

                self.Layout()

                self.pConnectTimeout.StartOnce(15000)

            elif q[1] == "bye":
                # print("bye event")
                self._ws_parent._sio.disconnect()

        except queue.Empty:
            pass

        event.RequestMore()

    def doStop(self, event):
        try:
            self._ws_parent._sio.call("bye", "", timeout=30)
        except Exception:
            pass
        self._ws_parent._sio.disconnect()

        if not self._loop_running:
            self._ws_parent._doAnalytics("disconnect", reason=1)
            return self.EndModal(0)

    def doConnect(self, event):
        self.pConnectTimeout.Stop()
        return self.EndModal(1)

    def doConnectTimeout(self, event):
        return self.EndModal(1)


class FT232HConfig(ft232h_pinconfig.FT232H_Pin_Config):
    def __init__(self, parent):
        super().__init__(parent)
        for name, img, flip in const._ft232h_boards:
            self.c_Board.Append(name)

        self.base_parent: MainApp = parent
        self.c_Board.Selection = 0

        self.board.Bitmap = wx.Bitmap(
            const._ft232h_boards[self.c_Board.Selection][1], wx.BITMAP_TYPE_ANY
        )
        self.isFlip = const._ft232h_boards[self.c_Board.Selection][2]

        self.Layout()
        self.setupPins()

    def setupPins(self):
        self.pins_layout = []

        if self.isFlip:
            for i in range(8):
                self.pins_layout.append(getattr(self, f"cfg_p2{i}"))
                if i == 7:
                    continue
                getattr(self, f"cfg_p2{i}").Clear()
                getattr(self, f"cfg_p2{i}").Append(
                    ["TDI", "TDO", "TCK", "TMS", "TRST", "SRST", "High", "Low"]
                )
                getattr(self, f"cfg_p2{i}").Selection = 0
                getattr(self, f"cfg_p2{i}").Enable(True)

            for i in range(8):
                self.pins_layout.append(getattr(self, f"cfg_p1{i}"))
                getattr(self, f"cfg_p1{i}").Clear()
                getattr(self, f"cfg_p1{i}").Append(
                    ["TDI", "TDO", "TCK", "TMS", "TRST", "SRST", "High", "Low"]
                )
                getattr(self, f"cfg_p1{i}").Selection = 0
                getattr(self, f"cfg_p1{i}").Enable(True)

            self.cfg_p27.Clear()
            self.cfg_p27.Append("RTCK")
            self.cfg_p27.Selection = 0
            self.cfg_p27.Enable(False)

        else:
            for i in range(8):
                self.pins_layout.append(getattr(self, f"cfg_p1{i}"))
                if i == 7:
                    continue
                getattr(self, f"cfg_p1{i}").Clear()
                getattr(self, f"cfg_p1{i}").Append(
                    ["TDI", "TDO", "TCK", "TMS", "TRST", "SRST", "High", "Low"]
                )
                getattr(self, f"cfg_p1{i}").Selection = 0
                getattr(self, f"cfg_p1{i}").Enable(True)

            for i in range(8):
                self.pins_layout.append(getattr(self, f"cfg_p2{i}"))
                getattr(self, f"cfg_p2{i}").Clear()
                getattr(self, f"cfg_p2{i}").Append(
                    ["TDI", "TDO", "TCK", "TMS", "TRST", "SRST", "High", "Low"]
                )
                getattr(self, f"cfg_p2{i}").Selection = 0
                getattr(self, f"cfg_p2{i}").Enable(True)

            self.cfg_p17.Clear()
            self.cfg_p17.Append("RTCK")
            self.cfg_p17.Selection = 0
            self.cfg_p17.Enable(False)

        for e, p in enumerate(self.pins_layout):
            if e == self.base_parent._ft232h_tdi:
                p.Selection = 0

            elif e == self.base_parent._ft232h_tdo:
                p.Selection = 1

            elif e == self.base_parent._ft232h_tck:
                p.Selection = 2

            elif e == self.base_parent._ft232h_tms:
                p.Selection = 3

            elif e == self.base_parent._ft232h_trst:
                p.Selection = 4

            elif e == self.base_parent._ft232h_srst:
                p.Selection = 5

            elif e != 7:
                p.Selection = 6 if self.base_parent._ft232h_pins & (
                    1 << e) else 7

    def doChangeBoard(self, event):
        self.board.Bitmap = wx.Bitmap(
            const._ft232h_boards[self.c_Board.Selection][1], wx.BITMAP_TYPE_ANY
        )
        self.isFlip = const._ft232h_boards[self.c_Board.Selection][2]

        self.Layout()
        self.setupPins()

    def doApply(self, events):
        hasTDI = False
        hasTDO = False
        hasTCK = False
        hasTMS = False
        hasTRST = False
        hasSRST = False

        for e, p in enumerate(self.pins_layout):
            if e != 7:
                if p.Selection == 0:
                    if hasTDI:
                        return
                    hasTDI = True

                elif p.Selection == 1:
                    if hasTDO:
                        return
                    hasTDO = True

                elif p.Selection == 2:
                    if hasTCK:
                        return
                    hasTCK = True

                elif p.Selection == 3:
                    if hasTMS:
                        return
                    hasTMS = True

                elif p.Selection == 4:
                    if hasTRST:
                        return
                    hasTRST = True

                elif p.Selection == 5:
                    if hasSRST:
                        return
                    hasSRST = True

        if (
            not hasTDI
            or not hasTDO
            or not hasTCK
            or not hasTMS
            or not hasTRST
            or not hasSRST
        ):
            return

        self.base_parent._ft232h_pins = 0xFFFF
        self.base_parent._ft232h_dirs = 0xFFFF

        for e, p in enumerate(self.pins_layout):
            if e != 7:
                if p.Selection == 0:
                    self.base_parent._ft232h_tdi = e
                    self.base_parent._ft232h_pins &= ~(1 << e)

                elif p.Selection == 1:
                    self.base_parent._ft232h_tdo = e
                    self.base_parent._ft232h_dirs &= ~(1 << e)
                    self.base_parent._ft232h_pins &= ~(1 << e)

                elif p.Selection == 2:
                    self.base_parent._ft232h_tck = e
                    self.base_parent._ft232h_pins &= ~(1 << e)

                elif p.Selection == 3:
                    self.base_parent._ft232h_tms = e

                elif p.Selection == 4:
                    self.base_parent._ft232h_trst = e

                elif p.Selection == 5:
                    self.base_parent._ft232h_srst = e

                elif p.Selection == 7:
                    self.base_parent._ft232h_pins &= ~(1 << e)

        # print(bin(self.base_parent._ft232h_pins))
        # print(bin(self.base_parent._ft232h_dirs))

        self.EndModal(0)

    def doCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def doReset(self, event):
        for e, p in enumerate(self.pins_layout):
            if e == const._ft232h_default_jtag_tdi:
                p.Selection = 0

            elif e == const._ft232h_default_jtag_tdo:
                p.Selection = 1

            elif e == const._ft232h_default_jtag_tck:
                p.Selection = 2

            elif e == const._ft232h_default_jtag_tms:
                p.Selection = 3

            elif e == const._ft232h_default_jtag_trst:
                p.Selection = 4

            elif e == const._ft232h_default_jtag_srst:
                p.Selection = 5

            elif e != 7:
                p.Selection = 6


class FT232RConfig(ft232r_pinconfig.FT232R_Pin_Config):
    def __init__(self, parent):
        super().__init__(parent)
        self.base_parent: MainApp = parent

        for name, img in const._ft232r_boards:
            self.c_Board.Append(name)

        self.c_Board.Selection = 0

        self.board.Bitmap = wx.Bitmap(
            const._ft232r_boards[self.c_Board.Selection][1], wx.BITMAP_TYPE_ANY
        )
        self.Layout()

        self.cfg_tdi.Selection = self.base_parent._ft232r_tdi
        self.cfg_tdo.Selection = self.base_parent._ft232r_tdo
        self.cfg_tck.Selection = self.base_parent._ft232r_tck
        self.cfg_tms.Selection = self.base_parent._ft232r_tms
        self.cfg_trst.Selection = self.base_parent._ft232r_trst
        self.cfg_srst.Selection = self.base_parent._ft232r_srst

        self.pin_layout = [
            self.cfg_tdi,
            self.cfg_tdo,
            self.cfg_tck,
            self.cfg_tms,
            self.cfg_trst,
            self.cfg_srst,
        ]

    def doChangeBoard(self, event):
        self.board.Bitmap = wx.Bitmap(
            const._ft232r_boards[self.c_Board.Selection][1], wx.BITMAP_TYPE_ANY
        )
        self.Layout()

    def doApply(self, events):
        for e, x in enumerate(self.pin_layout):
            for f, y in enumerate(self.pin_layout):
                if e != f and x.Selection == y.Selection:
                    return

        self.base_parent._ft232r_tdi = self.cfg_tdi.Selection
        self.base_parent._ft232r_tdo = self.cfg_tdo.Selection
        self.base_parent._ft232r_tck = self.cfg_tck.Selection
        self.base_parent._ft232r_tms = self.cfg_tms.Selection
        self.base_parent._ft232r_trst = self.cfg_trst.Selection
        self.base_parent._ft232r_srst = self.cfg_srst.Selection

        self.EndModal(0)

    def doCancel(self, event):
        self.EndModal(wx.ID_CANCEL)


class ResetConfig(resetDelay.ResetDelayConfig):
    def __init__(self, parent):
        super().__init__(parent)
        self.base_parent: MainApp = parent

        self.nNTRSTWidth.Value = self.base_parent.ntrst_reset_pulse
        self.nSRSTWidth.Value = self.base_parent.nsrst_reset_pulse
        self.nNTRSTDelay.Value = self.base_parent.ntrst_reset_delay
        self.nSRSTDelay.Value = self.base_parent.nsrst_reset_delay
        self.nResetDelay.Value = self.base_parent.reset_delay
        self.cUseCustom.Value = self.base_parent.custom_reset

    def bDoApply(self, event):
        self.base_parent.ntrst_reset_pulse = self.nNTRSTWidth.Value
        self.base_parent.nsrst_reset_pulse = self.nSRSTWidth.Value
        self.base_parent.ntrst_reset_delay = self.nNTRSTDelay.Value
        self.base_parent.nsrst_reset_delay = self.nSRSTDelay.Value
        self.base_parent.reset_delay = self.nResetDelay.Value
        self.base_parent.custom_reset = self.cUseCustom.Value
        if not self.cUseCustom.Value:
            self.base_parent._ocdSendCommand(
                f"jtag_ntrst_delay 0; adapter srst delay 0; jtag_ntrst_assert_width 0; adapter srst pulse_width 0"
            )

        else:
            self.base_parent._ocdSendCommand(
                f"jtag_ntrst_delay {self.base_parent.ntrst_reset_delay}; adapter srst delay {self.base_parent.nsrst_reset_delay}; jtag_ntrst_assert_width {self.base_parent.ntrst_reset_pulse}; adapter srst pulse_width {self.base_parent.nsrst_reset_pulse}"
            )
        self.EndModal(0)

    def bDoCancel(self, event):
        self.EndModal(0)


class NANDControllerConfig(nandControlConfig.NANDControllerConfig):
    def __init__(self, parent):
        super().__init__(parent)
        self.base_parent: MainApp = parent

        self.cPageWidth.Selection = self.base_parent.page_width + 1
        self.bSkipRegInit.Value = self.base_parent.skip_init
        self.bSkipGPIOInit.Value = self.base_parent.skip_gpio_init

        self.tCustomCFG1.Value = f"{self.base_parent.custom_cfg1:02x}"
        self.tCustomCFG2.Value = f"{self.base_parent.custom_cfg2:02x}"
        self.tCustomCFGCMN.Value = f"{self.base_parent.custom_cfg_common:02x}"

        self.bDisableMSM6550Quirks.Value = not self.base_parent.msm6550_discrepancy
        self.bUseFastAPI.Value = self.base_parent.fast_api
        self.bSelect2ndBank.Value = bool(self.base_parent.nand_dev_id)

        self.init_code = self.base_parent.nand_init_code

    def doApply(self, event):
        self.base_parent.page_width = self.cPageWidth.Selection - 1
        self.base_parent.skip_init = self.bSkipRegInit.Value
        self.base_parent.skip_gpio_init = self.bSkipGPIOInit.Value

        self.base_parent.custom_cfg1 = int(self.tCustomCFG1.Value, 16)
        self.base_parent.custom_cfg2 = int(self.tCustomCFG2.Value, 16)
        self.base_parent.custom_cfg_common = int(self.tCustomCFGCMN.Value, 16)

        self.base_parent.msm6550_discrepancy = not self.bDisableMSM6550Quirks.Value
        self.base_parent.fast_api = self.bUseFastAPI.Value
        self.base_parent.nand_dev_id = int(self.bSelect2ndBank.Value)

        self.base_parent.nand_init_code = self.init_code
        self.EndModal(0)

    def doCancel(self, event):
        self.EndModal(0)

    def doCodeEdit(self, event):
        InitCodeEditor(self).ShowModal()


class TargetReadConfig(targetReadConfig.TargetReadConfig):
    def __init__(self, parent):
        super().__init__(parent)
        self.base_parent: MainApp = parent

        self.sReadSize.Value = self.base_parent.nor_read_size // 0x100
        self.tReadSize.Label = f"{self.sReadSize.Value*0x100} bytes"

        self.sMaxPass.Value = self.base_parent.max_read_pass
        self.sMaxIdentical.Value = self.base_parent.max_identical_read
        self.bCheckIdentical.Value = self.base_parent.check_identical_reads
        self.bDisablePerformanceOpts.Value = self.base_parent.disable_platform_options
        self.cIdenticalMode.Selection = self.base_parent.identical_check_mode

        self.cOutFormat.Selection = self.base_parent.nand_format

    def doChangeReadSize(self, event):
        self.tReadSize.Label = f"{self.sReadSize.Value*0x100} bytes"
        self.Layout()

    def doApply(self, event):
        self.base_parent.nor_read_size = self.sReadSize.Value * 0x100
        self.base_parent.max_read_pass = self.sMaxPass.Value
        self.base_parent.max_identical_read = self.sMaxIdentical.Value
        self.base_parent.check_identical_reads = self.bCheckIdentical.Value
        self.base_parent.disable_platform_options = self.bDisablePerformanceOpts.Value
        self.base_parent.identical_check_mode = self.cIdenticalMode.Selection
        self.base_parent.nand_format = self.cOutFormat.Selection

        t = self.base_parent.cTarget.Selection
        isBig = False

        if t >= self.base_parent._beTarget:
            isBig = True
            t -= self.base_parent._beTarget

        else:
            t -= 1

        if not self.bDisablePerformanceOpts.Value:
            for v in const._additional_config:
                if const._targets[t] in const._additional_config[v]:
                    self.base_parent._ocdSendCommand(v)
                    break

        else:
            for v in const._additional_config_unset:
                if const._targets[t] in const._additional_config_unset[v]:
                    self.base_parent._ocdSendCommand(v)
                    break

        self.EndModal(0)

    def doCancel(self, event):
        self.EndModal(0)


class UserMetadataConfig(metadataUserEditor.MetadataEditor):
    def __init__(self, parent):
        super().__init__(parent)
        self.base_parent: MainApp = parent

        self.tDeviceName.Value = self.base_parent.metadata["device_name"]
        self.tManufacturer.Value = self.base_parent.metadata["device_manufacturer"]
        self.tPerformer.Value = self.base_parent.metadata["performer"]
        self.tDeviceVersion.Value = self.base_parent.metadata["device_version"]
        self.tLender.Value = self.base_parent.metadata["lender"]

        self.cDisableMetadata.Value = self.base_parent.metadata["ignore_metadata"]

    def doApply(self, event):
        self.base_parent.metadata["device_name"] = self.tDeviceName.Value
        self.base_parent.metadata["device_manufacturer"] = self.tManufacturer.Value
        self.base_parent.metadata["performer"] = self.tPerformer.Value
        self.base_parent.metadata["device_version"] = self.tDeviceVersion.Value
        self.base_parent.metadata["lender"] = self.tLender.Value

        self.base_parent.metadata["ignore_metadata"] = self.cDisableMetadata.Value

        self.EndModal(0)

    def doCancel(self, event):
        self.EndModal(0)


class InitCodeEditor(nandInitScript.NANDCodeEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.base_parent: NANDControllerConfig = parent

        self.tTCLCode.SetLexer(wx.stc.STC_LEX_TCL)
        self.tTCLCode.Value = self.base_parent.init_code

    def doApply(self, event):
        self.base_parent.init_code = self.tTCLCode.Value
        self.EndModal(0)

    def doCancel(self, event):
        self.EndModal(0)


class MainApp(main.main):
    def __init__(self, parent):
        global _PTRACKCOUNT

        super().__init__(parent)

        print("Dumpit started")
        self.status.Value = ""
        self.finderStatus.Value = ""
        self.sInfo.Value = ""

        for i, n in const._interfaces:
            self.cInterface.Append(i)

        self.cInterface.Selection = 0

        self.cTarget.Append("Auto")
        self.cTarget.Selection = 0

        self._beTarget = 1

        for t in const._targets:
            self.cTarget.Append(t)
            self._beTarget += 1

        for t in const._targets:
            self.cTarget.Append(t + " (BE)")

        for r, v in const._reset_type:
            self.cResetMode.Append(r)

        self.cResetMode.Selection = 3

        """
        self._resetDelays = []

        for e in const._reset_delays:
            for c in const._reset_delays:
                for d in const._reset_delays:
                    for f in const._reset_delays:
                        for g in const._reset_delays:
                            self._resetDelays.append((d, c, e, g, f))
        
        for rt, rs, sr, rt_a, rs_a in self._resetDelays:
            self.cResetDelay.Append(
                f"{rt}ms TRST / {rs}ms SRST / {sr}ms RST delay / {rt_a}ms TRST assert / {rs_a}ms SRST assert")

        self.cResetDelay.Selection = 0
        """

        for p in const._platforms:
            self.cChipset.Append(p["name"])

        self.cChipset.Selection = 0
        self.progress.Value = 0

        self._ocd_version = (
            subprocess.check_output(
                [getOCDExec(), "--version"], encoding="utf-8", stderr=subprocess.STDOUT
            )
            .splitlines()[0]
            .rstrip()
        )

        self.status.Value += (
            f"Dumpit v{const.DUMPIT_VERSION}\nOpenOCD: {self._ocd_version}"
        )

        for name, parm in const._ft232h_adapters:
            self.cFTAdapter.Append(name)

        self.cFTAdapter.Selection = 0

        """ Start dumpit stuff """
        self._isConnect = False
        self._isConnectRemote = False
        self._isForward = False

        self._ocd = None
        self._sio = None
        self._logThread = None
        self._logThreadQueue = None

        self._sioThread = None
        self._sioMsgQueue = None

        self._sioLogThread = None

        self._errMsgQueue = None
        self._progMsgQueue = None
        self._btnMsgQueue = None
        self._pong_flag = threading.Event()
        self._timeout_flag = threading.Event()

        self.log_time = 0

        self._next_ping = 0
        self._next_timeout = 0
        self._reconnect_token = None

        self._reconnecting = False
        self._logPushBuff = []
        self._logPushDelay = queue.Queue()

        self._dumpThread = None

        self._isRead = False
        self._isReadCanceled = False

        self._logSupressed = False

        self._ft232h_tdi = const._ft232h_default_jtag_tdi
        self._ft232h_tdo = const._ft232h_default_jtag_tdo
        self._ft232h_tms = const._ft232h_default_jtag_tms
        self._ft232h_tck = const._ft232h_default_jtag_tck
        self._ft232h_trst = const._ft232h_default_jtag_trst
        self._ft232h_srst = const._ft232h_default_jtag_srst

        self._ft232h_pins = 0xFFFF & ~(
            1 << self._ft232h_tdi | 1 << self._ft232h_tdo | 1 << self._ft232h_tck
        )
        self._ft232h_dirs = 0xFFFF & ~(1 << self._ft232h_tdo)

        self._ft232r_tdi = const._ft232r_bit_rx
        self._ft232r_tdo = const._ft232r_bit_rts
        self._ft232r_tck = const._ft232r_bit_tx
        self._ft232r_tms = const._ft232r_bit_cts
        self._ft232r_trst = const._ft232r_bit_dtr
        self._ft232r_srst = const._ft232r_bit_dcd

        self._gpio_tdi = 10
        self._gpio_tdo = 9
        self._gpio_tck = 11
        self._gpio_tms = 8
        self._gpio_trst = 7
        self._gpio_srst = 24

        self._known_tdi = -1
        self._known_tdo = -1
        self._known_tck = -1
        self._known_tms = -1
        self._known_trst = -1

        self._debug_logs = False
        self._loaded_dcc = None

        self._cfi_start_offset = None

        self.ntrst_reset_delay = 50
        self.ntrst_reset_pulse = 100

        self.nsrst_reset_delay = 50
        self.nsrst_reset_pulse = 100

        self.reset_delay = 100
        self.custom_reset = False

        self.page_width = -1

        self.skip_init = False
        self.skip_gpio_init = True
        self.custom_cfg1 = -1
        self.custom_cfg2 = -1
        self.custom_cfg_common = -1
        self.nand_dev_id = 0

        self.nand_init_code = ""

        self._isInitDone = False

        self.nor_read_size = 4096
        self.max_read_pass = 10
        self.max_identical_read = 3
        self.check_identical_reads = False
        self.disable_platform_options = False
        self.identical_check_mode = 0

        self._command_history = []
        self._command_history_index = 0

        self.idcode = 0
        self.metadata = {
            "ignore_metadata": False,
            "device_name": "unknown",
            "device_manufacturer": "unknown",
            "performer": getpass.getuser(),
            "device_version": "unknown",
            "lender": "",
        }

        self.msm6550_discrepancy = True
        # 0 = Spare at the end, 1 = Interleaved (Standard), 2 = Split, 3 = No Spare
        self.nand_format = 0
        self.fast_api = True

        self.remotePerformer = ""
        self.remoteAssistant = ""
        self.remoteLender = ""

        self._nand_idcodes = json.load(
            open(os.path.join(os.path.dirname(__file__), "nand_ids.json"), "r")
        )

        if os.path.exists(
            os.path.join(os.path.dirname(__file__), "dumpit_config.json")
        ):
            cfg = json.load(
                open(os.path.join(os.path.dirname(
                    __file__), "dumpit_config.json"), "r")
            )
            if "interface" in cfg:
                self.cInterface.Selection = cfg["interface"]
            if "speed" in cfg:
                self.nSpeed.Value = cfg["speed"]
            if "chipset" in cfg:
                self.cChipset.Selection = cfg["chipset"]
            if "target" in cfg:
                self.cTarget.Selection = cfg["target"]
            if "tap" in cfg:
                self.cTap.Selection = cfg["tap"]
            if "ir" in cfg:
                self.nIR.Value = cfg["ir"]
            if "reset_mode" in cfg:
                self.cResetMode.Selection = cfg["reset_mode"]
            if "trst_reset_pulse" in cfg:
                self.ntrst_reset_pulse = cfg["trst_reset_pulse"]
            if "srst_reset_pulse" in cfg:
                self.nsrst_reset_pulse = cfg["srst_reset_pulse"]
            if "trst_reset_delay" in cfg:
                self.ntrst_reset_delay = cfg["trst_reset_delay"]
            if "srst_reset_delay" in cfg:
                self.nsrst_reset_delay = cfg["srst_reset_delay"]
            if "reset_delay" in cfg:
                self.reset_delay = cfg["reset_delay"]
            if "custom_reset" in cfg:
                self.custom_reset = cfg["custom_reset"]
            if "skip_init" in cfg:
                self.bSkipInit.Value = cfg["skip_init"]
            if "start" in cfg:
                self.tStart.Value = cfg["start"]
            if "end" in cfg:
                self.tEnd.Value = cfg["end"]
            if "nand_size" in cfg:
                self.cNandSize.Selection = cfg["nand_size"]
            if "ecc_disabled" in cfg:
                self.bECCDisable.Value = cfg["ecc_disabled"]
            if "bad_blocks_in_data" in cfg:
                self.bBadBlockinData.Value = cfg["bad_blocks_in_data"]
            if "target_remote" in cfg:
                self.bTargetRemote.Value = cfg["target_remote"]
            if "use_gdb" in cfg:
                self.bUseGDB.Value = cfg["use_gdb"]
            if "ft232r_usb_id" in cfg:
                self.tUSBID.Value = cfg["ft232r_usb_id"]
            if "ft232r_restore_serial" in cfg:
                self.tRestoreSerial.Value = cfg["ft232r_restore_serial"]
            if "ft232r_tdi" in cfg:
                self._ft232r_tdi = cfg["ft232r_tdi"]
            if "ft232r_tdo" in cfg:
                self._ft232r_tdo = cfg["ft232r_tdo"]
            if "ft232r_tms" in cfg:
                self._ft232r_tck = cfg["ft232r_tms"]
            if "ft232r_tck" in cfg:
                self._ft232r_tms = cfg["ft232r_tck"]
            if "ft232r_trst" in cfg:
                self._ft232r_trst = cfg["ft232r_trst"]
            if "ft232r_srst" in cfg:
                self._ft232r_srst = cfg["ft232r_srst"]
            if "ft232h_adapter" in cfg:
                self.cFTAdapter.Selection = cfg["ft232h_adapter"]
            if "ft232h_usb_id" in cfg:
                self.tUSBID1.Value = cfg["ft232h_usb_id"]
            if "ft232h_channel" in cfg:
                self.cChannel.Selection = cfg["ft232h_channel"]
            if "ft232h_sampling_edge" in cfg:
                self.rSamplingEdge.Selection = cfg["ft232h_sampling_edge"]
            if "ft232h_tdi" in cfg:
                self._ft232h_tdi = cfg["ft232h_tdi"]
            if "ft232h_tdo" in cfg:
                self._ft232h_tdo = cfg["ft232h_tdo"]
            if "ft232h_tck" in cfg:
                self._ft232h_tck = cfg["ft232h_tck"]
            if "ft232h_tms" in cfg:
                self._ft232h_tms = cfg["ft232h_tms"]
            if "ft232h_trst" in cfg:
                self._ft232h_trst = cfg["ft232h_trst"]
            if "ft232h_srst" in cfg:
                self._ft232h_srst = cfg["ft232h_srst"]

            if "ft232h_pins" in cfg:
                self._ft232h_pins = (
                    (
                        cfg["ft232h_pins"]
                        & ~(
                            1 << self._ft232h_tdi
                            | 1 << self._ft232h_tdo
                            | 1 << self._ft232h_tck
                        )
                    )
                    | 1 << self._ft232h_tms
                    | 1 << self._ft232h_trst
                    | 1 << self._ft232h_srst
                )
                self._ft232h_dirs = 0xFFFF & ~(1 << self._ft232h_tdo)

            if "gpio_chip" in cfg:
                self.nGPIODChip.Value = cfg["gpio_chip"]
            if "gpio_tdi" in cfg:
                self._gpio_tdi = cfg["gpio_tdi"]
            if "gpio_tdo" in cfg:
                self._gpio_tdo = cfg["gpio_tdo"]
            if "gpio_tck" in cfg:
                self._gpio_tck = cfg["gpio_tck"]
            if "gpio_tms" in cfg:
                self._gpio_tms = cfg["gpio_tms"]
            if "gpio_trst" in cfg:
                self._gpio_trst = cfg["gpio_trst"]
            if "gpio_srst" in cfg:
                self._gpio_srst = cfg["gpio_srst"]
            if "parport_cable" in cfg:
                self.cParCable.Selection = cfg["parport_cable"]
            if "parport_port" in cfg:
                self.tParPort.Value = cfg["parport_port"]
            if "remote_bitbang_host" in cfg:
                self.tRBBHost.Value = cfg["remote_bitbang_host"]
            if "remote_bitbang_port" in cfg:
                self.tRBBPort.Value = cfg["remote_bitbang_port"]
            if "finder_use_mpsse" in cfg:
                self.bUseMPSSE.Value = cfg["finder_use_mpsse"]
            if "enable_analytics" in cfg:
                self.bEnableAnalytics.Value = cfg["enable_analytics"]
            if "user_id" in cfg:
                self.tUserID.Value = cfg["user_id"]
            if "tracking_count" in cfg:
                _PTRACKCOUNT = cfg["tracking_count"]
            if "debug_log" in cfg:
                self._debug_logs = cfg["debug_log"]
            if "nand_skip_init" in cfg:
                self.skip_init = cfg["nand_skip_init"]
            if "nand_skip_init_gpio" in cfg:
                self.skip_gpio_init = cfg["nand_skip_init_gpio"]
            if "nand_custom_cfg1" in cfg:
                self.custom_cfg1 = cfg["nand_custom_cfg1"]
            if "nand_custom_cfg2" in cfg:
                self.custom_cfg2 = cfg["nand_custom_cfg2"]
            if "nand_custom_cfg_common" in cfg:
                self.custom_cfg_common = cfg["nand_custom_cfg_common"]
            if "nand_device_id" in cfg:
                self.nand_dev_id = cfg["nand_device_id"]
            if "nand_page_width" in cfg:
                self.page_width = cfg["nand_page_width"]
            if "nand_init_code" in cfg:
                self.nand_init_code = cfg["nand_init_code"]
            if "msm6550_discrepancy" in cfg:
                self.msm6550_discrepancy = cfg["msm6550_discrepancy"]
            if "nand_out_format" in cfg:
                self.nand_format = cfg["nand_out_format"]
            if "use_fast_api" in cfg:
                self.fast_api = cfg["use_fast_api"]

            if "read_size" in cfg:
                self.nor_read_size = cfg["read_size"]
            if "max_read_pass" in cfg:
                self.max_read_pass = cfg["max_read_pass"]
            if "max_identical" in cfg:
                self.max_identical_read = cfg["max_identical"]
            if "check_identical" in cfg:
                self.check_identical_reads = cfg["check_identical"]
            if "disable_platform_options" in cfg:
                self.disable_platform_options = cfg["disable_platform_options"]
            if "identical_check_mode" in cfg:
                self.identical_check_mode = cfg["identical_check_mode"]

            if "metadata" in cfg:
                self.metadata = cfg["metadata"]

        if not self.tUserID.Value:
            self.tUserID.Value = str(uuid.uuid4())

        self.Update()
        self.Layout()

    def _doAnalytics(self, action, **kwargs):
        if self.bEnableAnalytics.Value:
            cfg = {}

            cfg["interface"] = self.cInterface.GetString(
                self.cInterface.Selection)
            cfg["speed"] = self.nSpeed.Value
            cfg["chipset"] = self.cChipset.GetString(self.cChipset.Selection)
            cfg["target"] = self.cTarget.GetString(self.cTarget.Selection)
            cfg["tap"] = self.cTap.GetString(self.cTap.Selection)
            cfg["ir"] = self.nIR.Value
            cfg["reset_mode"] = self.cResetMode.GetString(
                self.cResetMode.Selection)
            cfg["trst_reset_pulse"] = self.ntrst_reset_pulse
            cfg["srst_reset_pulse"] = self.nsrst_reset_pulse
            cfg["trst_reset_delay"] = self.ntrst_reset_delay
            cfg["srst_reset_delay"] = self.nsrst_reset_delay
            cfg["reset_delay"] = self.reset_delay
            cfg["custom_reset"] = self.custom_reset
            cfg["skip_init"] = self.bSkipInit.Value
            cfg["start"] = self.tStart.Value
            cfg["end"] = self.tEnd.Value
            cfg["nand_size"] = self.cNandSize.GetString(
                self.cNandSize.Selection)
            cfg["ecc_disabled"] = self.bECCDisable.Value
            cfg["bad_blocks_in_data"] = self.bBadBlockinData.Value
            cfg["use_gdb"] = self.bUseGDB.Value

            cfg["ft232r_usb_id"] = self.tUSBID.Value
            cfg["ft232r_restore_serial"] = self.tRestoreSerial.Value
            cfg["ft232r_tdi"] = self._ft232r_tdi
            cfg["ft232r_tdo"] = self._ft232r_tdo
            cfg["ft232r_tms"] = self._ft232r_tck
            cfg["ft232r_tck"] = self._ft232r_tms
            cfg["ft232r_trst"] = self._ft232r_trst
            cfg["ft232r_srst"] = self._ft232r_srst

            cfg["ft232h_adapter"] = self.cFTAdapter.GetString(
                self.cFTAdapter.Selection)
            cfg["ft232h_usb_id"] = self.tUSBID1.Value
            cfg["ft232h_channel"] = self.cChannel.Selection
            cfg["ft232h_sampling_edge"] = self.rSamplingEdge.GetString(
                self.rSamplingEdge.Selection
            )
            cfg["ft232h_tdi"] = self._ft232h_tdi
            cfg["ft232h_tdo"] = self._ft232h_tdo
            cfg["ft232h_tck"] = self._ft232h_tck
            cfg["ft232h_tms"] = self._ft232h_tms
            cfg["ft232h_trst"] = self._ft232h_trst
            cfg["ft232h_srst"] = self._ft232h_srst

            cfg["ft232h_pins"] = self._ft232h_pins

            cfg["gpio_chip"] = self.nGPIODChip.Value
            cfg["gpio_tdi"] = self._gpio_tdi
            cfg["gpio_tdo"] = self._gpio_tdo
            cfg["gpio_tck"] = self._gpio_tck
            cfg["gpio_tms"] = self._gpio_tms
            cfg["gpio_trst"] = self._gpio_trst
            cfg["gpio_srst"] = self._gpio_srst

            cfg["parport_cable"] = self.cParCable.GetString(
                self.cParCable.Selection)
            cfg["parport_port"] = self.tParPort.Value

            cfg["finder_use_mpsse"] = self.bUseMPSSE.Value

            cfg["nand_skip_init"] = self.skip_init
            cfg["nand_skip_init_gpio"] = self.skip_gpio_init
            cfg["nand_custom_cfg1"] = self.custom_cfg1
            cfg["nand_custom_cfg2"] = self.custom_cfg2
            cfg["nand_custom_cfg_common"] = self.custom_cfg_common
            cfg["nand_device_id"] = self.nand_dev_id
            cfg["nand_page_width"] = self.page_width

            cfg["nand_init_code"] = self.nand_init_code
            cfg["msm6550_discrepancy"] = self.msm6550_discrepancy
            cfg["nand_out_format"] = self.nand_format
            cfg["use_fast_api"] = self.fast_api

            cfg["read_size"] = self.nor_read_size
            cfg["max_read_pass"] = self.max_read_pass
            cfg["max_identical"] = self.max_identical_read
            cfg["check_identical"] = self.check_identical_reads
            cfg["disable_platform_options"] = self.disable_platform_options
            cfg["identical_check_mode"] = self.identical_check_mode

            cfg["dcc_used"] = self._loaded_dcc is not None

            pAnalyticsThread = threading.Thread(
                target=doTrackThread,
                args=(self.tUserID.Value, action, self._ocd_version, cfg),
                kwargs=kwargs,
            )
            pAnalyticsThread.daemon = True

            pAnalyticsThread.start()

    def _doLogging(self):
        for l in _unbuffered(self._ocd, "stderr"):
            try:
                if not self._logSupressed or l.startswith(b"Error:") or l.startswith(b"Warn :"):
                    self._logThreadQueue.put(l.decode("utf-8"))
                    if self._isForward:
                        log_randid = random.randbytes(16).hex()
                        self._logPushBuff.append((l, log_randid))
                        self._logPushDelay.put(
                            {"data": l.decode("utf-8"), "id": log_randid}
                        )

            except Exception:
                pass

    def _doWSLoop(self):
        while self._sio.connected or self._reconnecting:
            if not self._reconnecting:
                try:
                    p = self._sio.receive(1)

                    if p[0] == "data":
                        self._sioMsgQueue.put(p[1])

                    elif p[0] == "command":
                        if p[1]["c"] == "initDone":
                            if self._debug_logs:
                                print("init done received")
                            self._isInitDone = True

                        elif p[1]["c"] == "initUndone":
                            if self._debug_logs:
                                print("init undone received")
                            self._isInitDone = False

                        elif p[1]["c"] == "progress":
                            self.progress.Value = p[1]["d"][0]
                            self.sPageStatus.SetStatusText(p[1]["d"][1])

                        elif p[1]["c"] == "isRead":
                            if p[1]["d"]:
                                self._isRead = True
                                self._isReadCanceled = False
                                self._btnMsgQueue.put(True)
                            else:
                                self._btnMsgQueue.put(False)
                                self._isRead = False
                                self._isReadCanceled = False

                        elif p[1]["c"] == "isSupressed":
                            self._logSupressed = p[1]["d"]

                        elif p[1]["c"] == "doStopRead":
                            self._isReadCanceled = True

                        elif p[1]["c"] == "configure":
                            self._cfi_start_offset = p[1]["d"]["cfi_base_offset"]
                            self.cChipset.Selection = p[1]["d"]["chipset"]
                            self.cTarget.Selection = p[1]["d"]["target"]

                        elif p[1]["c"] == "identity":
                            self.remotePerformer = p[1]["d"]["performer"]
                            self.remoteLender = p[1]["d"]["lender"]

                            if self._debug_logs:
                                print("IDENTITY CLIENT:",
                                      self.remotePerformer, self.remoteLender)

                            self._sio.emit(
                                "command",
                                {
                                    "c": "identity",
                                    "d": {"assistant": self.remoteAssistant},
                                },
                            )

                        elif p[1]["c"] == "idcode":
                            self.idcode = p[1]["d"]

                    elif p[0] == "log" and (
                        not self._logSupressed or p[1].startswith(
                            b"Error:") or p[1].startswith(b"Warn :")
                    ):
                        self._logThreadQueue.put(p[1])

                    elif p[0] == "bye":
                        # print("bye event")
                        self._sio.disconnect()

                    elif p[0] == "ping_remote":
                        self._sio.emit("pong_remote")

                    elif p[0] == "pong_remote":
                        self._pong_flag.set()

                    elif p[0] == "protocol" and p[1] == "dumpit":
                        res = self._sio.call(
                            "forward_reconnect", self._reconnect_token, timeout=5
                        )

                        if not res["error"]:
                            self._reconnect_token = res["reconnect_token"]

                        else:
                            self._sio.disconnect()

                except socketio.exceptions.TimeoutError:
                    pass

                except Exception:
                    pass

    def _doWSLoop_Forward(self):
        while (self._ocd.poll() is None and self._sio.connected) or self._reconnecting:
            if not self._reconnecting:
                try:
                    p = self._sio.receive(1)

                    if p[0] == "data":
                        self._sio.emit("data", self._ocdSendCommand(p[1]))

                    elif p[0] == "command":
                        if p[1]["c"] == "initDone":
                            if self._debug_logs:
                                print("init done received")
                            self._isInitDone = True

                        elif p[1]["c"] == "initUndone":
                            if self._debug_logs:
                                print("init undone received")
                            self._isInitDone = False

                        elif p[1]["c"] == "progress":
                            self.progress.Value = p[1]["d"][0]
                            self.sPageStatus.SetStatusText(p[1]["d"][1])

                        elif p[1]["c"] == "isRead":
                            if p[1]["d"]:
                                self._isRead = True
                                self._isReadCanceled = False
                                self._btnMsgQueue.put(True)
                            else:
                                self._btnMsgQueue.put(False)
                                self._isRead = False
                                self._isReadCanceled = False

                        elif p[1]["c"] == "isSupressed":
                            self._logSupressed = p[1]["d"]

                        elif p[1]["c"] == "doStopRead":
                            self._isReadCanceled = True

                        elif p[1]["c"] == "identity":
                            self.remoteAssistant = p[1]["d"]["assistant"]

                            if self._debug_logs:
                                print("IDENTITY Server:", self.remoteAssistant)

                    elif p[0] == "bye":
                        # print("bye event")
                        self._sio.disconnect()

                    elif p[0] == "ping_remote":
                        self._sio.emit("pong_remote")

                    elif p[0] == "pong_remote":
                        self._pong_flag.set()

                    elif p[0] == "protocol" and p[1] == "dumpit":
                        res = self._sio.call(
                            "forward_reconnect", self._reconnect_token, timeout=5
                        )

                        if not res["error"]:
                            self._reconnect_token = res["reconnect_token"]

                            for l, id in self._logPushBuff:
                                time.sleep(0.1)
                                self._sio.emit(
                                    "log_req", {"data": l.decode(
                                        "utf-8"), "id": id}
                                )

                        else:
                            self._sio.disconnect()

                    elif p[0] == "log_ack":
                        for e, (_, id) in enumerate(self._logPushBuff):
                            if id == p[1]:
                                self._logPushBuff.pop(e)
                                break

                except socketio.exceptions.TimeoutError:
                    pass

                except Exception:
                    pass

    def _doWSLoop_Forward_Log(self):
        while (self._ocd.poll() is None and self._sio.connected) or self._reconnecting:
            if not self._reconnecting:
                if time.perf_counter() >= self.log_time:
                    self.log_time = time.perf_counter() + 0.1
                    try:
                        self._sio.emit(
                            "log_req", self._logPushDelay.get_nowait())

                    except queue.Empty:
                        pass

    def doLoop(self, event):
        global _PTRACKCOUNT

        if self._isConnect or self._isConnectRemote:
            event.RequestMore()

        try:
            track = _PTRACKING.get_nowait()
            if track not in _PTRACKCOUNT:
                _PTRACKCOUNT[track] = 0

            _PTRACKCOUNT[track] += 1

        except queue.Empty:
            pass

        if self._logThreadQueue:
            try:
                self.status.AppendText(
                    self._logThreadQueue.get_nowait() + "\n")
                self.status.ShowPosition(self.status.GetLastPosition())

            except queue.Empty:
                pass

        if self._errMsgQueue:
            try:
                p = self._errMsgQueue.get_nowait()
                wx.MessageBox(str(p), "Dumpit", wx.OK |
                              wx.CENTER | wx.ICON_ERROR, self)

            except queue.Empty:
                pass

        if self._progMsgQueue:
            try:
                p = self._progMsgQueue.get_nowait()
                self.progress.Value = min(
                    self.progress.Range, int(p[0] * self.progress.Range)
                )
                self.sPageStatus.SetStatusText(p[1])
                if self._isConnectRemote and self._sio:
                    self._sio.emit(
                        "command", {"c": "progress", "d": [int(
                            p[0] * self.progress.Range), p[1]]}
                    )

            except queue.Empty:
                pass

        if self._btnMsgQueue:
            try:
                p = self._btnMsgQueue.get_nowait()
                if p:
                    self.bDumpFlash.Enable(False)
                    self.bDumpMemory.Enable(False)
                    self.bStop.Enable(True)

                else:
                    self.bDumpFlash.Enable(True)
                    self.bDumpMemory.Enable(True)
                    self.bStop.Enable(False)

            except queue.Empty:
                pass

        if (
            self._isForward
            and self._ocd
            and self._isConnect
            and self._ocd.poll() is not None
        ):
            try:
                self._sio.call("bye", "", timeout=30)
            except Exception:
                pass
            self._sio.disconnect()
            self._isConnect = False
            self._isForward = False

        if (
            self._ocd
            and self._isConnect
            and self._ocd.poll() is not None
            and not self._isForward
        ):
            self._isConnect = False
            self.bConnect.Label = "Connect"
            self.bConnectRemote.Enable(True)
            self.bForwardRemote.Enable(True)
            self._doAnalytics("disconnect", reason=1)

        if self._sio and self._isConnectRemote and not self._sio.connected:
            self._isConnectRemote = False
            self.bConnect.Label = "Connect"
            self.bConnectRemote.Enable(True)
            self.bForwardRemote.Enable(True)
            self._doAnalytics("disconnect", reason=2)

            if (
                self._isForward
                and self._ocd
                and self._isConnect
                and self._ocd.poll() is None
            ):
                self._ocd.terminate()
                self._isConnect = False
                self._isForward = False

            # self.bReconnectRemote.Hide()
            # self.bForwardRemote.Show()

            self.Layout()

    def _ocdSendCommand(self, cmd: str, _return: bool = True):
        if self._debug_logs:
            print(f"EXEC {cmd}")

        if self._ocd and self._ocd.poll() is None:
            self._ocd.stdin.write(cmd.encode("latin-1") + b"\x1a")
            self._ocd.stdin.flush()

            resTemp = bytearray()
            while True:
                t = self._ocd.stdout.read(1)
                if t in [b"\x1a", b""]:
                    break

                resTemp += t

            if self._debug_logs:
                print(f"OUT {cmd}: {resTemp}")

            if _return:
                return resTemp.decode("latin-1")

            else:
                # print(f"SINK: {resTemp}")
                return ""

        elif self._sio and self._sio.connected:
            self._sio.emit("data", cmd)
            resTemp = self._sioMsgQueue.get(timeout=10)

            if self._debug_logs:
                print(f"OUT {cmd}: {resTemp}")

            if _return:
                return resTemp

            else:
                # print(f"SINK: {self._sioMsgQueue.get(timeout=10)}")
                return ""

        else:
            return ""

    def doConnect(self, event):
        if self._isConnect:
            self._isConnect = False
            self._ocd.terminate()
            self.bConnect.Label = "Connect"
            self.bConnectRemote.Enable(True)
            self.bForwardRemote.Enable(True)

            if self._isForward and self._isConnectRemote:
                self._isForward = False
                self._isConnectRemote = False

                if self._sio and self._sio.connected:
                    try:
                        self._sio.call("bye", "", timeout=30)
                    except Exception:
                        pass
                    self._sio.disconnect()

                    # self.bReconnectRemote.Hide()
                    # self.bForwardRemote.Show()

                    self.Layout()

            self._doAnalytics("disconnect", reason=0)

        elif self._isConnectRemote:
            self._isConnectRemote = False

            if self._sio and self._sio.connected:
                try:
                    self._sio.call("bye", "", timeout=30)
                except Exception:
                    pass
                self._sio.disconnect()

                # self.bReconnectRemote.Hide()
                # self.bForwardRemote.Show()

                self.Layout()

            self.bConnect.Label = "Connect"
            self.bConnectRemote.Enable(True)
            self.bForwardRemote.Enable(True)
            self._doAnalytics("disconnect", reason=0)

        else:
            self._isInitDone = False

            if self._ocd and self._ocd.poll() is None:
                self._ocd.kill()
            gc.collect()

            INIT_CMD = getInitCmd(self)

            self._doAnalytics("connect", type=0)

            # print(INIT_CMD)

            self._isConnect = True
            self._isConnectRemote = False
            self._isForward = False

            self.status.Value = f'Command-line arguments: openocd -c "{INIT_CMD}"\n\n'
            self._ocd = subprocess.Popen(
                [getOCDExec(), "-c", INIT_CMD],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # cwd=os.path.dirname(__file__),
            )

            self._ocdSendCommand("")

            self._logThreadQueue = queue.Queue()

            self._errMsgQueue = queue.Queue()
            self._progMsgQueue = queue.Queue()
            self._btnMsgQueue = queue.Queue()

            self._logThread = threading.Thread(target=self._doLogging)
            self._logThread.daemon = True

            self._logThread.start()

            self.bConnect.Label = "Disconnect"
            self.bConnectRemote.Enable(False)
            self.bForwardRemote.Enable(False)

            self.idcode = self.cmd_get_idcode()
            self._doAnalytics("idcode", idcode=self.idcode)

    def doReconnectRemote(self, event):
        if not self._isConnectRemote:
            return

        self._reconnecting = True
        try:
            self._sio.disconnect()
            time.sleep(2)

            self._sio = socketio.SimpleClient(
                handle_sigint=False, reconnection_delay=0.5, reconnection_delay_max=0.5
            )
            gc.collect()

            self._sio.connect(
                f"http://{self.bTargetRemote.Value}/"
                if self.bTargetRemote.Value.startswith("localhost")
                or self.bTargetRemote.Value.startswith("127.0.0.1")
                or self.bTargetRemote.Value.startswith("::1")
                or self.bTargetRemote.Value.startswith("[::1]")
                else f"https://{self.bTargetRemote.Value}/",
                transports=["websocket"],
                socketio_path="dumpit_remote",
            )

            while True:
                p = self._sio.receive(5)
                if p[0] == "protocol" and p[1] != "dumpit":
                    raise Exception("Not a valid Dumpit remote protocol.")
                elif p[0] == "protocol" and p[1] == "dumpit":
                    break

            res = self._sio.call("forward_reconnect",
                                 self._reconnect_token, timeout=5)
            if res["error"]:
                raise Exception(res["error"])

            self._reconnect_token = res["reconnect_token"]
            self._logThreadQueue.put("Reconnected to the remote.")

            if self._isForward:
                for l, id in self._logPushBuff:
                    time.sleep(0.1)
                    self._sio.emit(
                        "log_req", {"data": l.decode("utf-8"), "id": id})

        except Exception as e:
            if self._sio and self._sio.connected:
                try:
                    self._sio.call("bye", "", timeout=30)
                except Exception:
                    pass
                self._sio.disconnect()

            self._doAnalytics("error", error=str(
                e), traceback=traceback.format_exc())
            wx.MessageBox(str(e), "Dumpit", wx.OK |
                          wx.CENTER | wx.ICON_ERROR, self)

        finally:
            self._reconnecting = False

    def doConnectRemote(self, event):
        try:
            try:
                if self._sio:
                    self._sio.disconnect()

                if self._sioThread:
                    self._sioThread.join(15)
            except Exception:
                pass
            self._isInitDone = False

            self._sio = socketio.SimpleClient(
                handle_sigint=False, reconnection_delay=0.5, reconnection_delay_max=0.5
            )
            gc.collect()

            self._doAnalytics("connect", type=2)

            self._sio.connect(
                f"http://{self.bTargetRemote.Value}/"
                if self.bTargetRemote.Value.startswith("localhost")
                or self.bTargetRemote.Value.startswith("127.0.0.1")
                or self.bTargetRemote.Value.startswith("::1")
                or self.bTargetRemote.Value.startswith("[::1]")
                else f"https://{self.bTargetRemote.Value}/",
                transports=["websocket"],
                socketio_path="dumpit_remote",
            )

            while True:
                p = self._sio.receive(5)
                if p[0] == "protocol" and p[1] != "dumpit":
                    raise Exception("Not a valid Dumpit remote protocol.")
                elif p[0] == "protocol" and p[1] == "dumpit":
                    break

            rep = wx.TextEntryDialog(self, "Enter interface token")
            if rep.ShowModal() == wx.ID_CANCEL:
                try:
                    self._sio.call("bye", "", timeout=30)
                except Exception:
                    pass
                self._sio.disconnect()

                return

            res = self._sio.call("forward_connect", rep.GetValue(), timeout=5)
            if res["error"]:
                raise Exception(res["error"])

            self._reconnect_token = res["reconnect_token"]

            self.remotePerformer = ""
            self.remoteLender = ""
            self.remoteAssistant = self.metadata["performer"]

            # self.bReconnectRemote.Show()
            # self.bForwardRemote.Hide()

            self.Layout()

            self.status.Value = ""
            self._logThreadQueue = queue.Queue()
            self._sioMsgQueue = queue.Queue()

            self._errMsgQueue = queue.Queue()
            self._progMsgQueue = queue.Queue()
            self._btnMsgQueue = queue.Queue()

            self._pong_flag.clear()
            self._timeout_flag.clear()
            self._logPushBuff.clear()

            self._logPushDelay = queue.Queue()

            self._sioThread = threading.Thread(target=self._doWSLoop)
            self._sioThread.daemon = True

            self._sioThread.start()

            self._isConnectRemote = True
            self._isForward = False

            self.bConnect.Label = "Disconnect"
            self.bConnectRemote.Enable(False)
            self.bForwardRemote.Enable(False)

        except Exception as e:
            if self._sio and self._sio.connected:
                try:
                    self._sio.call("bye", "", timeout=30)
                except Exception:
                    pass
                self._sio.disconnect()

            self._doAnalytics("error", error=str(
                e), traceback=traceback.format_exc())
            wx.MessageBox(str(e), "Dumpit", wx.OK |
                          wx.CENTER | wx.ICON_ERROR, self)

    def doForwardRemote(self, event):
        try:
            try:
                if self._sio:
                    self._sio.disconnect()

                if self._sioThread:
                    self._sioThread.join(15)
            except Exception:
                pass
            self._isInitDone = False

            self._sio = socketio.SimpleClient(
                handle_sigint=False, reconnection_delay=0.5, reconnection_delay_max=0.5
            )
            gc.collect()

            self._sio.connect(
                f"http://{self.bTargetRemote.Value}/"
                if self.bTargetRemote.Value.startswith("localhost")
                or self.bTargetRemote.Value.startswith("127.0.0.1")
                or self.bTargetRemote.Value.startswith("::1")
                or self.bTargetRemote.Value.startswith("[::1]")
                else f"https://{self.bTargetRemote.Value}/",
                transports=["websocket"],
                socketio_path="dumpit_remote",
            )

            while True:
                p = self._sio.receive(5)
                if p[0] == "protocol" and p[1] != "dumpit":
                    raise Exception("Not a valid Dumpit remote protocol.")
                elif p[0] == "protocol" and p[1] == "dumpit":
                    break

            token = self._sio.call("forward_request", timeout=5)
            forward_wait = ForwardApp(self, token["token"]).ShowModal()
            if forward_wait == 1:
                # self.bReconnectRemote.Show()
                # self.bForwardRemote.Hide()

                self.Layout()

                if self._ocd and self._ocd.poll() is None:
                    self._ocd.kill()

                gc.collect()

                INIT_CMD = getInitCmd(self)

                self._doAnalytics("connect", type=1)

                # print(INIT_CMD)

                self._isConnect = True
                self._isForward = True
                self._isConnectRemote = True

                self.log_time = time.perf_counter() + 0.1

                self.remotePerformer = self.metadata["performer"]
                self.remoteLender = self.metadata["lender"]
                self.remoteAssistant = ""

                self._sio.emit(
                    "command",
                    {
                        "c": "identity",
                        "d": {
                            "performer": self.remotePerformer,
                            "lender": self.remoteLender,
                        },
                    },
                )

                self.status.Value = (
                    f'Command-line arguments: openocd -c "{INIT_CMD}"\n\n'
                )

                log_randid = random.randbytes(16).hex()
                self._logPushBuff.append(
                    (
                        f'Command-line arguments: openocd -c "{INIT_CMD}"\n\n'.encode(
                            "utf-8"
                        ),
                        log_randid,
                    )
                )

                time.sleep(0.1)
                self._sio.emit(
                    "log_req",
                    {
                        "data": f'Command-line arguments: openocd -c "{INIT_CMD}"\n\n',
                        "id": log_randid,
                    },
                )

                self._ocd = subprocess.Popen(
                    [getOCDExec(), "-c", INIT_CMD],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.path.dirname(__file__),
                )

                self._ocdSendCommand("")

                self._sio.emit(
                    "command",
                    {
                        "c": "configure",
                        "d": {
                            "cfi_base_offset": self._cfi_start_offset,
                            "chipset": self.cChipset.Selection,
                            "target": self.cTarget.Selection,
                        },
                    },
                )

                self._logThreadQueue = queue.Queue()
                self._sioMsgQueue = queue.Queue()

                self._errMsgQueue = queue.Queue()
                self._progMsgQueue = queue.Queue()
                self._btnMsgQueue = queue.Queue()

                self._pong_flag.clear()
                self._timeout_flag.clear()
                self._logPushBuff.clear()

                self._logPushDelay = queue.Queue()

                self._logThread = threading.Thread(target=self._doLogging)
                self._logThread.daemon = True

                self._sioThread = threading.Thread(
                    target=self._doWSLoop_Forward)
                self._sioThread.daemon = True

                self._sioLogThread = threading.Thread(
                    target=self._doWSLoop_Forward_Log)
                self._sioLogThread.daemon = True

                self._logThread.start()
                self._sioThread.start()
                self._sioLogThread.start()

                self.bConnect.Label = "Disconnect"
                self.bConnectRemote.Enable(False)
                self.bForwardRemote.Enable(False)

                self.idcode = self.cmd_get_idcode()
                self._sio.emit("command", {"c": "idcode", "d": self.idcode})

                self._doAnalytics("idcode", idcode=self.idcode)

        except Exception as e:
            if self._sio and self._sio.connected:
                try:
                    self._sio.call("bye", "", timeout=30)
                except Exception:
                    pass
                self._sio.disconnect()

            self._doAnalytics("error", error=str(
                e), traceback=traceback.format_exc())
            wx.MessageBox(str(e), "Dumpit", wx.OK |
                          wx.CENTER | wx.ICON_ERROR, self)

    def doHexCheck(self, event: wx.CommandEvent):
        event.EventObject.ChangeValue(
            re.sub("([^0-9a-fA-F]+)", "", event.EventObject.GetValue())
        )

    def cmd_get_idcode(self):
        if not self._isConnect and not self._isConnectRemote:
            return b""
        try:
            return int(self._ocdSendCommand("jtag cget target0.cpu -idcode"))

        except Exception:
            return 0

    def cmd_read_u8(self, offset: int, size: int = 1):
        if not self._isConnect and not self._isConnectRemote:
            return 0 if size <= 1 else b""
        if self._debug_logs:
            print(f"RDB {hex(offset)} {size}")

        c = self._ocdSendCommand(f"read_memory {hex(offset)} 8 {size}")

        if c.startswith("0x"):
            return (
                int(c, 16) if size <= 1 else bytes(
                    [int(x, 16) for x in c.split(" ")])
            )

        else:
            self._logThreadQueue.put(f"Invalid hex data: {c}")
            return 0xFF if size <= 1 else b"\xff" * size

    def cmd_read_u16(self, offset: int, size: int = 1):
        if not self._isConnect and not self._isConnectRemote:
            return 0 if size <= 1 else []
        if self._debug_logs:
            print(f"RDH {hex(offset)} {size}")

        c = self._ocdSendCommand(f"read_memory {hex(offset)} 16 {size}")

        if c.startswith("0x"):
            return int(c, 16) if size <= 1 else [int(x, 16) for x in c.split(" ")]

        else:
            self._logThreadQueue.put(f"Invalid hex data: {c}")
            return 0xFFFF if size <= 1 else b"\xff\xff" * size

    def cmd_read_u32(self, offset: int, size: int = 1):
        if not self._isConnect and not self._isConnectRemote:
            return 0 if size <= 1 else []
        if self._debug_logs:
            print(f"RDW {hex(offset)} {size}")

        c = self._ocdSendCommand(f"read_memory {hex(offset)} 32 {size}")

        if c.startswith("0x"):
            return int(c, 16) if size <= 1 else [int(x, 16) for x in c.split(" ")]

        else:
            self._logThreadQueue.put(f"Invalid hex data: {c}")
            return 0xFFFFFFFF if size <= 1 else b"\xff\xff\xff\xff" * size

    def cmd_read_flash(self, offset: int, size: int = 1):
        if not self._isConnect and not self._isConnectRemote:
            return b""
        if self._debug_logs:
            print(f"RDF {hex(offset)} {size}")

        c = self._ocdSendCommand(
            f"flash read_bank_memory 0 {hex(offset)} {size} 0x200")

        if c.startswith("0x"):
            return bytes([int(x, 16) for x in c.split(" ")])

        else:
            self._logThreadQueue.put(f"Invalid hex data: {c}")
            return b"\xff" * size

    def cmd_read_nand(self, page_size: int, offset: int, count: int = 1):
        if not self._isConnect and not self._isConnectRemote:
            return b"", b""

        if self._debug_logs:
            print(f"RDN {page_size} {hex(offset)} {count}")

        c = self._ocdSendCommand(
            f"nand dump_memory 0 {offset >> (11 if page_size == 1 else 9)} {count}")

        if c.startswith("0x"):
            temp = bytes([int(x, 16) for x in c.split(" ")])
            return temp[:((0x800 if page_size == 1 else 0x200) * count)], temp[((0x800 if page_size == 1 else 0x200) * count):]

        else:
            self._logThreadQueue.put(f"Invalid hex data: {c}")
            return b"\xff" * (((0x800 if page_size == 1 else 0x200) * count) + ((0x40 if page_size == 1 else 0x10) * count))

    def cmd_read_cp15(self, cr_n, op_1, cr_m, op_2):
        if not self._isConnect and not self._isConnectRemote:
            return 0

        try:
            return int(
                self._ocdSendCommand(
                    f"arm mrc 15 {op_1} {cr_n} {cr_m} {op_2}"), 16
            )

        except Exception:
            return 0

    def cmd_write_cp15(self, cr_n, op_1, cr_m, op_2, value):
        if not self._isConnect and not self._isConnectRemote:
            return 0
        self._ocdSendCommand(
            f"arm mcr 15 {hex(op_1)} {hex(cr_n)} {hex(cr_m)} {hex(op_2)} {hex(value)}"
        )

    def cmd_write_u8(self, offset: int, value: int):
        if not self._isConnect and not self._isConnectRemote:
            return
        if self._debug_logs:
            print(f"WDB {hex(offset)} {value}")
        self._ocdSendCommand(f"mwb {hex(offset)} {hex(value)}")

    def cmd_write_u16(self, offset: int, value: int):
        if not self._isConnect and not self._isConnectRemote:
            return
        if self._debug_logs:
            print(f"WDH {hex(offset)} {value}")
        self._ocdSendCommand(f"mwh {hex(offset)} {hex(value)}")

    def cmd_write_u32(self, offset: int, value: int):
        if not self._isConnect and not self._isConnectRemote:
            return
        if self._debug_logs:
            print(f"WDW {hex(offset)} {value}")
        self._ocdSendCommand(f"mww {hex(offset)} {hex(value)}")

    def doReadMemoryThread(self, name, cOffset, eOffset):
        self._isRead = True
        self._isReadCanceled = False

        self._btnMsgQueue.put(True)
        if self._isConnectRemote and self._sio:
            self._sio.emit("command", {"c": "isRead", "d": True})

        self._doAnalytics(
            "dump_start", addr_start=cOffset, addr_end=eOffset, is_memory=True
        )

        self._ocdSendCommand("halt")

        self._logSupressed = True
        self._logThreadQueue.put(
            f"Dump memory started {datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if self._isConnectRemote and self._sio:
            self._sio.emit("command", {"c": "isSupressed", "d": True})

        CFI_READ_BUFFER = self.nor_read_size

        read_times = []

        try:
            with open(name, "wb") as tempFile:
                while cOffset < eOffset and not self._isReadCanceled:
                    readTimeStart = time.perf_counter()
                    tempFile.write(
                        self.cmd_read_u8(
                            cOffset, min(CFI_READ_BUFFER, eOffset - cOffset)
                        )
                    )
                    cOffset += min(CFI_READ_BUFFER, eOffset - cOffset)
                    readTimeEnd = time.perf_counter()

                    read_times.append(readTimeEnd-readTimeStart)
                    if len(read_times) > 50:
                        read_times.pop(0)

                    self._progMsgQueue.put(
                        [cOffset / eOffset, f"Read {hex(cOffset)} of {hex(eOffset)}, average time of last 50 commands: {round(sum(read_times)/len(read_times), 4)}"])

            self._logThreadQueue.put(
                f"Dump memory finished {datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}"
            )

        except Exception as e:
            traceback.print_exc()
            self._doAnalytics("error", error=str(
                e), traceback=traceback.format_exc())
            self._errMsgQueue.put(str(e))

        finally:
            time.sleep(1)
            self._btnMsgQueue.put(False)
            self._isRead = False
            self._isReadCanceled = False
            if self._isConnectRemote and self._sio:
                self._sio.emit("command", {"c": "isRead", "d": False})
            self._logSupressed = False
            if self._isConnectRemote and self._sio:
                self._sio.emit("command", {"c": "isSupressed", "d": False})

            self._doAnalytics(
                "dump_end", addr_start=cOffset, addr_end=eOffset, is_memory=True
            )

    def doReadMemory(self, event):
        if (not self._isConnect and not self._isConnectRemote) or self._isRead:
            return

        cOffset = int(self.tStart.Value, 16)
        eOffset = int(self.tEnd.Value, 16)

        if cOffset >= eOffset:
            return wx.MessageBox(
                f"start offset must be less than end offset",
                "Dumpit",
                wx.OK | wx.CENTER | wx.ICON_ERROR,
                self,
            )

        with wx.FileDialog(
            self, "Dump memory", wildcard="Binary file|*.bin", style=wx.FD_SAVE
        ) as fd:
            fd: wx.FileDialog
            if fd.ShowModal() != wx.ID_CANCEL:
                self.progress.Value = 0
                if self._isConnectRemote and self._sio:
                    self._sio.emit("command", {"c": "progress", "d": 0})

                self._dumpThread = threading.Thread(
                    target=self.doReadMemoryThread,
                    args=(fd.GetPath(), cOffset, eOffset),
                )
                self._dumpThread.daemon = True

                self._dumpThread.start()

    def doReadFlashThread(self, name, cOffset, eOffset, baseO1N=-1):
        spareBuf = bytearray()
        bbBuf = bytearray()

        self._isRead = True
        self._isReadCanceled = False

        if self._isConnectRemote and self._sio:
            self._sio.emit("command", {"c": "isRead", "d": True})

        NANDC = None

        self._btnMsgQueue.put(True)
        self._doAnalytics(
            "dump_start", addr_start=cOffset, addr_end=eOffset, is_memory=False
        )

        self._ocdSendCommand("halt")

        if self.nand_init_code:
            for l in self.nand_init_code.splitlines():
                self._ocdSendCommand(l)

        selPlat = const._platforms[self.cChipset.Selection]

        cp15 = self.cmd_read_cp15(1, 0, 0, 0)
        self.cmd_write_cp15(1, 0, 0, 0, cp15 & 0xFFFFFFFE)

        page_mode = 1

        try:
            if not self._isInitDone:
                if self._loaded_dcc is not None:
                    self._cfi_start_offset = 0

                    self._ocdSendCommand("soft_reset_halt")
                    self._ocdSendCommand(f"load_image $_DCC_PATH", False)
                    self._ocdSendCommand("arm core_state arm")
                    self._ocdSendCommand(f"resume $_DCC_START_OFFSET")

                    if not self._ocdSendCommand("flash probe 0").startswith(
                        "flash 'ocl' found at"
                    ):
                        raise Exception("Flash probe failed!")
                    self._ocdSendCommand("flash info 0")

                elif selPlat["mode"] == 12 or (self.fast_api and selPlat["mode"] in [1, 2, 3, 5, 9]):
                    if selPlat["mode"] == 1:
                        self._ocdSendCommand(
                            f"msm6250 base_addr 0 {hex(selPlat['flash_regs'])}")
                        self._ocdSendCommand(
                            f"msm6250 int_addr 0 {hex(selPlat['flash_int'])}")
                        self._ocdSendCommand(
                            f"msm6250 int_clr_addr 0 {hex(selPlat['flash_int_clear'])}")
                        self._ocdSendCommand(
                            f"msm6250 msm6550_discrepancy 0 {int(False if not self.msm6550_discrepancy else selPlat['flash_has_header'])}")
                        self._ocdSendCommand(
                            f"msm6250 op 0 {hex(selPlat['flash_nand_int'])}")
                        self._ocdSendCommand(
                            f"msm6250 skip_init 0 {int(self.skip_init)}")

                    elif selPlat["mode"] == 2:
                        self._ocdSendCommand(
                            f"msm6800 base_addr 0 {hex(selPlat['flash_regs'])}")
                        if self.custom_cfg1 != -1:
                            self._ocdSendCommand(
                                f"msm6800 custom_cfg1 0 {hex(self.custom_cfg1)}")
                        if self.custom_cfg2 != -1:
                            self._ocdSendCommand(
                                f"msm6800 custom_cfg2 0 {hex(self.custom_cfg2)}")
                        if self.custom_cfg_common != -1:
                            self._ocdSendCommand(
                                f"msm6800 custom_cfg_common 0 {hex(self.custom_cfg_common)}")
                        self._ocdSendCommand(
                            f"msm6800 device_id 0 {self.nand_dev_id}")
                        self._ocdSendCommand(
                            f"msm6800 int_addr 0 {hex(selPlat['flash_int'])}")
                        self._ocdSendCommand(
                            f"msm6800 int_clr_addr 0 {hex(selPlat['flash_int_clear'])}")
                        self._ocdSendCommand(
                            f"msm6800 op 0 {hex(selPlat['flash_nand_int'])}")
                        self._ocdSendCommand(
                            f"msm6800 skip_gpio_init 0 {int(self.skip_gpio_init)}")
                        self._ocdSendCommand(
                            f"msm6800 skip_init 0 {int(self.skip_init)}")

                    elif selPlat["mode"] == 3:
                        self._ocdSendCommand(
                            f"msm7200 base_addr 0 {hex(selPlat['flash_regs'])}")
                        if self.custom_cfg1 != -1:
                            self._ocdSendCommand(
                                f"msm7200 custom_cfg1 0 {hex(self.custom_cfg1)}")
                        if self.custom_cfg2 != -1:
                            self._ocdSendCommand(
                                f"msm7200 custom_cfg2 0 {hex(self.custom_cfg2)}")
                        self._ocdSendCommand(
                            f"msm7200 device_id 0 {self.nand_dev_id}")
                        self._ocdSendCommand(
                            f"msm7200 skip_init 0 {int(self.skip_init)}")

                    elif selPlat["mode"] == 5:
                        self._ocdSendCommand(
                            f"nand_generic ale 0 {selPlat['flash_addr']}")

                        self._ocdSendCommand(
                            f"nand_generic cle 0 {selPlat['flash_cmd']}")

                        if selPlat['flash_wait'] is not None:
                            self._ocdSendCommand(
                                f"nand_generic rb 0 {selPlat['flash_wait']}")
                            self._ocdSendCommand(
                                f"nand_generic rb_mask 0 {selPlat['wait_mask']}")
                        else:
                            self._ocdSendCommand(
                                f"nand_generic rb 0 {selPlat['flash_buffer']}")

                        self._ocdSendCommand(
                            f"nand_generic re 0 {selPlat['flash_buffer']}")

                        if selPlat["reg_width"] == 0:
                            self._ocdSendCommand(f"nand_generic ale_width 0 1")
                            self._ocdSendCommand(f"nand_generic cle_width 0 1")
                            self._ocdSendCommand(f"nand_generic rb_width 0 4")
                            self._ocdSendCommand(f"nand_generic re_width 0 1")
                            self._ocdSendCommand(f"nand_generic rb_inverted 0")

                        elif selPlat["reg_width"] == 1:
                            self._ocdSendCommand(f"nand_generic ale_width 0 1")
                            self._ocdSendCommand(f"nand_generic cle_width 0 1")
                            self._ocdSendCommand(f"nand_generic rb_width 0 4")
                            self._ocdSendCommand(f"nand_generic re_width 0 2")
                            self._ocdSendCommand(
                                f"nand_generic rb_inverted 0 0")

                        elif selPlat["reg_width"] == 2:
                            self._ocdSendCommand(f"nand_generic ale_width 0 2")
                            self._ocdSendCommand(f"nand_generic cle_width 0 2")
                            self._ocdSendCommand(f"nand_generic rb_width 0 4")
                            self._ocdSendCommand(f"nand_generic re_width 0 2")
                            self._ocdSendCommand(
                                f"nand_generic rb_inverted 0 0")

                        elif selPlat["reg_width"] == 4:
                            self._ocdSendCommand(f"nand_generic ale_width 0 4")
                            self._ocdSendCommand(f"nand_generic cle_width 0 4")
                            self._ocdSendCommand(f"nand_generic rb_width 0 4")
                            self._ocdSendCommand(f"nand_generic re_width 0 4")
                            self._ocdSendCommand(
                                f"nand_generic rb_inverted 0 0")

                        elif selPlat["reg_width"] == 5:
                            self._ocdSendCommand(f"nand_generic ale_width 0 4")
                            self._ocdSendCommand(f"nand_generic cle_width 0 4")
                            self._ocdSendCommand(f"nand_generic rb_width 0 4")
                            self._ocdSendCommand(f"nand_generic re_width 0 4")
                            self._ocdSendCommand(
                                f"nand_generic rb_inverted 0 1")

                    elif selPlat["mode"] == 9:
                        self._ocdSendCommand(
                            f"nand_generic ale 0 {selPlat['flash_addr']}")
                        self._ocdSendCommand(
                            f"nand_generic ale_mask 0 {selPlat['ale_mask']}")
                        self._ocdSendCommand(
                            f"nand_generic cle 0 {selPlat['flash_cmd']}")
                        self._ocdSendCommand(
                            f"nand_generic cle_mask 0 {selPlat['cle_mask']}")

                        if selPlat['flash_wait'] is not None:
                            self._ocdSendCommand(
                                f"nand_generic rb 0 {selPlat['flash_wait']}")
                            self._ocdSendCommand(
                                f"nand_generic rb_mask 0 {selPlat['wait_mask']}")
                        else:
                            self._ocdSendCommand(
                                f"nand_generic rb 0 {selPlat['flash_buffer']}")

                        self._ocdSendCommand(
                            f"nand_generic re 0 {selPlat['flash_buffer']}")

                        self._ocdSendCommand(
                            f"nand_generic re_width 0 {selPlat['reg_width']}")

                        if selPlat["gpio_width"] == 1:
                            self._ocdSendCommand(f"nand_generic ale_width 0 1")
                            self._ocdSendCommand(f"nand_generic cle_width 0 1")
                            self._ocdSendCommand(f"nand_generic rb_width 0 1")
                            self._ocdSendCommand(
                                f"nand_generic rb_inverted 0 0")

                        elif selPlat["gpio_width"] == 2:
                            self._ocdSendCommand(f"nand_generic ale_width 0 2")
                            self._ocdSendCommand(f"nand_generic cle_width 0 2")
                            self._ocdSendCommand(f"nand_generic rb_width 0 2")
                            self._ocdSendCommand(
                                f"nand_generic rb_inverted 0 0")

                        elif selPlat["gpio_width"] == 4:
                            self._ocdSendCommand(f"nand_generic ale_width 0 4")
                            self._ocdSendCommand(f"nand_generic cle_width 0 4")
                            self._ocdSendCommand(f"nand_generic rb_width 0 4")
                            self._ocdSendCommand(
                                f"nand_generic rb_inverted 0 0")

                        elif selPlat["gpio_width"] == 5:
                            self._ocdSendCommand(f"nand_generic ale_width 0 4")
                            self._ocdSendCommand(f"nand_generic cle_width 0 4")
                            self._ocdSendCommand(f"nand_generic rb_width 0 4")
                            self._ocdSendCommand(
                                f"nand_generic rb_inverted 0 1")

                    if not self._ocdSendCommand("nand probe 0").startswith("NAND flash device"):
                        raise Exception("Flash probe failed!")

                    nand_info = self._ocdSendCommand(
                        "nand info 0 0 8").splitlines()[0].rstrip()
                    id, size, voltage, bit_width, mfr, page_size, _, erasesize = re.search(
                        "#([0-9]*): NAND ([0-9]*)MiB ([0-9.]*)V ([0-9]*)-bit \(([\S]*)\) pagesize: ([0-9]*), buswidth: ([0-9]*), erasesize: ([0-9]*)", nand_info).groups()

                    if int(page_size) <= 512:
                        page_mode = 0

                    assert (
                        cOffset < (size << 20)
                        and eOffset < (size << 20)
                    ), "Flash address is out of range"

                elif selPlat["mode"] == 1:
                    NANDC = qcom_nandregs.MSM6250NANDController(
                        self.cmd_read_u32,
                        self.cmd_write_u32,
                        self.cmd_read_u8,
                        None,
                        selPlat["flash_regs"],
                        nand_int_clr_addr=selPlat["flash_int_clear"],
                        nand_int_addr=selPlat["flash_int"],
                        nand_op_reset_flag=selPlat["flash_nand_int"],
                        msm6550_discrepancy=False if not self.msm6550_discrepancy else selPlat[
                            "flash_has_header"],
                        skip_init=self.skip_init,
                    )
                    assert NANDC._idcode not in [
                        0x0,
                        0xFFFFFFFF,
                        0xFFFF0000,
                        0xFFFF00FF,
                    ], "NAND detect failed"

                    MFR_ID_HEX = f"0x{((NANDC._idcode >> 24) & 0xff):02x}"
                    DEV_ID_HEX = f"0x{((NANDC._idcode >> 16) & 0xff):02x}"

                    if self.page_width == -1:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_width = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_16bit"]
                            )
                    else:
                        NANDC._page_width = self.page_width

                    if MFR_ID_HEX in self._nand_idcodes["mfrids"]:
                        self._logThreadQueue.put(
                            f'Found NAND with an idcode of {hex(NANDC._idcode)}, which is manufacturered by {self._nand_idcodes["mfrids"][MFR_ID_HEX]}'
                        )

                    else:
                        self._logThreadQueue.put(
                            f"Found NAND with an idcode of {hex(NANDC._idcode)}, from unknown manufacturer"
                        )

                    if DEV_ID_HEX in self._nand_idcodes["devids"]:
                        NAND_INFO = self._nand_idcodes["devids"][DEV_ID_HEX]

                        self._logThreadQueue.put(
                            f'Page size: {NAND_INFO["page_size"]}')
                        self._logThreadQueue.put(
                            f'Spare size: {NAND_INFO["spare_size"]}'
                        )
                        self._logThreadQueue.put(
                            f'Flash size: {NAND_INFO["flash_size"] >> 20}MB'
                        )
                        self._logThreadQueue.put(
                            f'Data width: {(16 if NAND_INFO["is_16bit"] else 8)}'
                        )

                        assert (
                            cOffset < NAND_INFO["flash_size"]
                            and eOffset < NAND_INFO["flash_size"]
                        ), "Flash address is out of range"

                elif selPlat["mode"] == 2:
                    NANDC = qcom_nandregs.MSM6800NANDController(
                        self.cmd_read_u32,
                        self.cmd_write_u32,
                        self.cmd_read_u8,
                        None,
                        selPlat["flash_regs"],
                        nand_int_clr_addr=selPlat["flash_int_clear"],
                        nand_int_addr=selPlat["flash_int"],
                        nand_op_reset_flag=selPlat["flash_nand_int"],
                        page_size=(
                            -1
                            if self.cNandSize.Selection == 2
                            else self.cNandSize.Selection
                        ),
                        page_width=self.page_width,
                        skip_init=self.skip_init,
                        skip_gpio_init=self.skip_gpio_init,
                        devid=self.nand_dev_id,
                    )
                    assert NANDC._idcode not in [
                        0x0,
                        0xFFFFFFFF,
                        0xFFFF0000,
                        0xFFFF00FF,
                    ], "NAND detect failed"

                    MFR_ID_HEX = f"0x{((NANDC._idcode >> 24) & 0xff):02x}"
                    DEV_ID_HEX = f"0x{((NANDC._idcode >> 16) & 0xff):02x}"

                    if MFR_ID_HEX in self._nand_idcodes["mfrids"]:
                        self._logThreadQueue.put(
                            f'Found NAND with an idcode of {hex(NANDC._idcode)}, which is manufacturered by {self._nand_idcodes["mfrids"][MFR_ID_HEX]}'
                        )

                    else:
                        self._logThreadQueue.put(
                            f"Found NAND with an idcode of {hex(NANDC._idcode)}, from unknown manufacturer"
                        )

                    if DEV_ID_HEX in self._nand_idcodes["devids"]:
                        NAND_INFO = self._nand_idcodes["devids"][DEV_ID_HEX]

                        self._logThreadQueue.put(
                            f'Page size: {NAND_INFO["page_size"] if not NAND_INFO["is_extended"] else (1024 << (NANDC._idcode & 0x3))}'
                        )
                        self._logThreadQueue.put(
                            f'Spare size: {NAND_INFO["spare_size"]}'
                        )
                        self._logThreadQueue.put(
                            f'Flash size: {NAND_INFO["flash_size"] >> 20}MB'
                        )
                        self._logThreadQueue.put(
                            f'Data width: {(16 if NAND_INFO["is_16bit"] else 8)}'
                        )
                        self._logThreadQueue.put(
                            f'Extended ID: {"none" if not NAND_INFO["is_extended"] else hex(NANDC._idcode & 0xff)}'
                        )

                        assert (
                            cOffset < NAND_INFO["flash_size"]
                            and eOffset < NAND_INFO["flash_size"]
                        ), "Flash address is out of range"

                elif selPlat["mode"] == 3:
                    NANDC = qcom_nandregs.MSM7200NANDController(
                        self.cmd_read_u32,
                        self.cmd_write_u32,
                        self.cmd_read_u8,
                        None,
                        selPlat["flash_regs"],
                        bb_in_data=self.bBadBlockinData.Value,
                        page_size=(
                            -1
                            if self.cNandSize.Selection == 2
                            else self.cNandSize.Selection
                        ),
                        skip_init=self.skip_init,
                        devid=self.nand_dev_id,
                    )
                    assert NANDC._idcode not in [
                        0x0,
                        0xFFFFFFFF,
                        0xFFFF0000,
                        0xFFFF00FF,
                    ], "NAND detect failed"

                    MFR_ID_HEX = f"0x{((NANDC._idcode >> 24) & 0xff):02x}"
                    DEV_ID_HEX = f"0x{((NANDC._idcode >> 16) & 0xff):02x}"

                    if self.page_width == -1:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_width = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_16bit"]
                            )
                    else:
                        NANDC._page_width = self.page_width

                    if MFR_ID_HEX in self._nand_idcodes["mfrids"]:
                        self._logThreadQueue.put(
                            f'Found NAND with an idcode of {hex(NANDC._idcode)}, which is manufacturered by {self._nand_idcodes["mfrids"][MFR_ID_HEX]}'
                        )

                    else:
                        self._logThreadQueue.put(
                            f"Found NAND with an idcode of {hex(NANDC._idcode)}, from unknown manufacturer"
                        )

                    if DEV_ID_HEX in self._nand_idcodes["devids"]:
                        NAND_INFO = self._nand_idcodes["devids"][DEV_ID_HEX]

                        self._logThreadQueue.put(
                            f'Page size: {NAND_INFO["page_size"] if not NAND_INFO["is_extended"] else (1024 << (NANDC._idcode & 0x3))}'
                        )
                        self._logThreadQueue.put(
                            f'Spare size: {NAND_INFO["spare_size"]}'
                        )
                        self._logThreadQueue.put(
                            f'Flash size: {NAND_INFO["flash_size"] >> 20}MB'
                        )
                        self._logThreadQueue.put(
                            f'Data width: {(16 if NAND_INFO["is_16bit"] else 8)}'
                        )
                        self._logThreadQueue.put(
                            f'Extended ID: {"none" if not NAND_INFO["is_extended"] else hex(NANDC._idcode & 0xff)}'
                        )

                        assert (
                            cOffset < NAND_INFO["flash_size"]
                            and eOffset < NAND_INFO["flash_size"]
                        ), "Flash address is out of range"

                elif selPlat["mode"] == 4:
                    assert (
                        cOffset >= self._cfi_start_offset
                    ), f"Read address must be greater or equal than {hex(self._cfi_start_offset)}"

                    if not self._ocdSendCommand("flash probe 0").startswith(
                        "flash 'cfi' found at"
                    ):
                        raise Exception("Flash probe failed!")
                    self._ocdSendCommand("flash info 0")

                elif selPlat["mode"] == -1:
                    self._cfi_start_offset = 0
                    self._ocdSendCommand("flash probe 0")
                    self._ocdSendCommand("flash info 0")

                elif selPlat["mode"] == 5:
                    if selPlat["reg_width"] == 0:
                        NANDC = common_nandregs.GenericNANDController(
                            self.cmd_write_u8,
                            self.cmd_read_u8,
                            self.cmd_write_u8,
                            "big"
                            if self.cTarget.Selection >= self._beTarget
                            else "little",
                            self.cmd_read_u32,
                            selPlat["flash_cmd"],
                            selPlat["flash_addr"],
                            selPlat["flash_buffer"],
                            selPlat["flash_wait"],
                            selPlat["wait_mask"],
                            (
                                0
                                if self.cNandSize.Selection == 2
                                else self.cNandSize.Selection
                            ),
                            0,
                        )

                    elif selPlat["reg_width"] == 1:
                        NANDC = common_nandregs.GenericNANDController(
                            self.cmd_write_u8,
                            self.cmd_read_u16,
                            self.cmd_write_u16,
                            "big"
                            if self.cTarget.Selection >= self._beTarget
                            else "little",
                            self.cmd_read_u32,
                            selPlat["flash_cmd"],
                            selPlat["flash_addr"],
                            selPlat["flash_buffer"],
                            selPlat["flash_wait"],
                            selPlat["wait_mask"],
                            (
                                0
                                if self.cNandSize.Selection == 2
                                else self.cNandSize.Selection
                            ),
                            1,
                        )

                    elif selPlat["reg_width"] == 2:
                        NANDC = common_nandregs.GenericNANDController(
                            self.cmd_write_u16,
                            self.cmd_read_u16,
                            self.cmd_write_u16,
                            "big"
                            if self.cTarget.Selection >= self._beTarget
                            else "little",
                            self.cmd_read_u32,
                            selPlat["flash_cmd"],
                            selPlat["flash_addr"],
                            selPlat["flash_buffer"],
                            selPlat["flash_wait"],
                            selPlat["wait_mask"],
                            (
                                0
                                if self.cNandSize.Selection == 2
                                else self.cNandSize.Selection
                            ),
                            0,
                        )

                    elif selPlat["reg_width"] == 4:
                        NANDC = common_nandregs.GenericNANDController(
                            self.cmd_write_u32,
                            self.cmd_read_u32,
                            self.cmd_write_u32,
                            "big"
                            if self.cTarget.Selection >= self._beTarget
                            else "little",
                            self.cmd_read_u32,
                            selPlat["flash_cmd"],
                            selPlat["flash_addr"],
                            selPlat["flash_buffer"],
                            selPlat["flash_wait"],
                            selPlat["wait_mask"],
                            (
                                0
                                if self.cNandSize.Selection == 2
                                else self.cNandSize.Selection
                            ),
                            0,
                        )

                    elif selPlat["reg_width"] == 5:
                        NANDC = common_nandregs.GenericNANDController(
                            self.cmd_write_u32,
                            self.cmd_read_u32,
                            self.cmd_write_u32,
                            "big"
                            if self.cTarget.Selection >= self._beTarget
                            else "little",
                            self.cmd_read_u32,
                            selPlat["flash_cmd"],
                            selPlat["flash_addr"],
                            selPlat["flash_buffer"],
                            selPlat["flash_wait"],
                            selPlat["wait_mask"],
                            (
                                0
                                if self.cNandSize.Selection == 2
                                else self.cNandSize.Selection
                            ),
                            0,
                            True,
                        )

                    _msleep(const._jtag_init_delay)

                    assert NANDC._idcode not in [
                        0x0,
                        0xFFFFFFFF,
                        0xFFFF0000,
                        0xFFFF00FF,
                    ], "NAND detect failed"

                    MFR_ID_HEX = f"0x{((NANDC._idcode >> 24) & 0xff):02x}"
                    DEV_ID_HEX = f"0x{((NANDC._idcode >> 16) & 0xff):02x}"

                    if self.page_width == -1:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_width = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_16bit"]
                            )
                    else:
                        NANDC._page_width = self.page_width

                    if self.cNandSize.Selection == 2:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_size = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_extended"]
                            )

                    if MFR_ID_HEX in self._nand_idcodes["mfrids"]:
                        self._logThreadQueue.put(
                            f'Found NAND with an idcode of {hex(NANDC._idcode)}, which is manufacturered by {self._nand_idcodes["mfrids"][MFR_ID_HEX]}'
                        )

                    else:
                        self._logThreadQueue.put(
                            f"Found NAND with an idcode of {hex(NANDC._idcode)}, from unknown manufacturer"
                        )

                    if DEV_ID_HEX in self._nand_idcodes["devids"]:
                        NAND_INFO = self._nand_idcodes["devids"][DEV_ID_HEX]

                        self._logThreadQueue.put(
                            f'Page size: {NAND_INFO["page_size"] if not NAND_INFO["is_extended"] else (1024 << (NANDC._idcode & 0x3))}'
                        )
                        self._logThreadQueue.put(
                            f'Spare size: {NAND_INFO["spare_size"]}'
                        )
                        self._logThreadQueue.put(
                            f'Flash size: {NAND_INFO["flash_size"] >> 20}MB'
                        )
                        self._logThreadQueue.put(
                            f'Data width: {(16 if NAND_INFO["is_16bit"] else 8)}'
                        )
                        self._logThreadQueue.put(
                            f'Extended ID: {"none" if not NAND_INFO["is_extended"] else hex(NANDC._idcode & 0xff)}'
                        )

                        assert (
                            cOffset < NAND_INFO["flash_size"]
                            and eOffset < NAND_INFO["flash_size"]
                        ), "Flash address is out of range"

                elif selPlat["mode"] == 9:
                    if selPlat["reg_width"] == 1:
                        DATA_READ = self.cmd_read_u8
                        DATA_WRITE = self.cmd_write_u8

                    elif selPlat["reg_width"] == 2:
                        DATA_READ = self.cmd_read_u16
                        DATA_WRITE = self.cmd_write_u16

                    elif selPlat["reg_width"] == 4:
                        DATA_READ = self.cmd_read_u32
                        DATA_WRITE = self.cmd_write_u32

                    if selPlat["gpio_width"] == 1:
                        GP_READ = self.cmd_read_u8
                        GP_WRITE = self.cmd_write_u8

                    elif selPlat["gpio_width"] == 2:
                        GP_READ = self.cmd_read_u16
                        GP_WRITE = self.cmd_write_u16

                    elif selPlat["gpio_width"] in [4, 5]:
                        GP_READ = self.cmd_read_u32
                        GP_WRITE = self.cmd_write_u32

                    NANDC = common_nandregs.GenericNANDControllerGPIO(
                        GP_READ,
                        GP_WRITE,
                        DATA_READ,
                        DATA_WRITE,
                        "big" if self.cTarget.Selection >= self._beTarget else "little",
                        selPlat["flash_latch"],
                        selPlat["flash_buffer"],
                        selPlat["cle_mask"],
                        selPlat["ale_mask"],
                        selPlat["flash_wait"],
                        selPlat["wait_mask"],
                        (
                            0
                            if self.cNandSize.Selection == 2
                            else self.cNandSize.Selection
                        ),
                        0,
                        selPlat["gpio_width"] == 5,
                    )

                    _msleep(const._jtag_init_delay)

                    assert NANDC._idcode not in [
                        0x0,
                        0xFFFFFFFF,
                        0xFFFF0000,
                        0xFFFF00FF,
                    ], "NAND detect failed"

                    MFR_ID_HEX = f"0x{((NANDC._idcode >> 24) & 0xff):02x}"
                    DEV_ID_HEX = f"0x{((NANDC._idcode >> 16) & 0xff):02x}"

                    if self.page_width == -1:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_width = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_16bit"]
                            )
                    else:
                        NANDC._page_width = self.page_width

                    if self.cNandSize.Selection == 2:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_size = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_extended"]
                            )

                    if MFR_ID_HEX in self._nand_idcodes["mfrids"]:
                        self._logThreadQueue.put(
                            f'Found NAND with an idcode of {hex(NANDC._idcode)}, which is manufacturered by {self._nand_idcodes["mfrids"][MFR_ID_HEX]}'
                        )

                    else:
                        self._logThreadQueue.put(
                            f"Found NAND with an idcode of {hex(NANDC._idcode)}, from unknown manufacturer"
                        )

                    if DEV_ID_HEX in self._nand_idcodes["devids"]:
                        NAND_INFO = self._nand_idcodes["devids"][DEV_ID_HEX]

                        self._logThreadQueue.put(
                            f'Page size: {NAND_INFO["page_size"] if not NAND_INFO["is_extended"] else (1024 << (NANDC._idcode & 0x3))}'
                        )
                        self._logThreadQueue.put(
                            f'Spare size: {NAND_INFO["spare_size"]}'
                        )
                        self._logThreadQueue.put(
                            f'Flash size: {NAND_INFO["flash_size"] >> 20}MB'
                        )
                        self._logThreadQueue.put(
                            f'Data width: {(16 if NAND_INFO["is_16bit"] else 8)}'
                        )
                        self._logThreadQueue.put(
                            f'Extended ID: {"none" if not NAND_INFO["is_extended"] else hex(NANDC._idcode & 0xff)}'
                        )

                        assert (
                            cOffset < NAND_INFO["flash_size"]
                            and eOffset < NAND_INFO["flash_size"]
                        ), "Flash address is out of range"

                elif selPlat["mode"] == 7:
                    NANDC = common_nandregs.OneNANDController(
                        self.cmd_read_u16,
                        self.cmd_write_u16,
                        self.cmd_read_u8,
                        self.cmd_write_u8,
                        selPlat["o1n_offset"] if "o1n_offset" in selPlat else baseO1N,
                        (
                            0
                            if self.cNandSize.Selection == 2
                            else self.cNandSize.Selection
                        ),
                    )

                    assert ((NANDC._idcode >> 24) & 0xff) not in [
                        0xEC,
                        0x20,
                    ], "NAND detect failed"

                    MFR_ID_HEX = f"0x{((NANDC._idcode >> 24) & 0xff):02x}"

                    if MFR_ID_HEX in self._nand_idcodes["mfrids"]:
                        self._logThreadQueue.put(
                            f'Found OneNAND with an idcode of {hex(NANDC._idcode)}, which is manufacturered by {self._nand_idcodes["mfrids"][MFR_ID_HEX]}'
                        )

                    else:
                        self._logThreadQueue.put(
                            f"Found OneNAND with an idcode of {hex(NANDC._idcode)}, from unknown manufacturer"
                        )

                    self._logThreadQueue.put(
                        f"Flash size: {NANDC._density >> 3}MB")

                    assert cOffset < (NANDC._density << 17) and eOffset < (
                        NANDC._density << 17
                    ), "Flash address is out of range"

                elif selPlat["mode"] == 10:
                    NANDC = qcom_nandregs.MSM7200OneNANDController(
                        self.cmd_read_u32,
                        self.cmd_write_u32,
                        self.cmd_read_u8,
                        None,
                        selPlat["flash_regs"],
                        page_size=(
                            -1
                            if self.cNandSize.Selection == 2
                            else self.cNandSize.Selection
                        ),
                        skip_init=self.skip_init,
                    )

                    assert ((NANDC._idcode >> 24) & 0xff) not in [
                        0xEC,
                        0x20,
                    ], "NAND detect failed"

                    MFR_ID_HEX = f"0x{((NANDC._idcode >> 24) & 0xff):02x}"

                    if MFR_ID_HEX in self._nand_idcodes["mfrids"]:
                        self._logThreadQueue.put(
                            f'Found OneNAND with an idcode of {hex(NANDC._idcode)}, which is manufacturered by {self._nand_idcodes["mfrids"][MFR_ID_HEX]}'
                        )

                    else:
                        self._logThreadQueue.put(
                            f"Found OneNAND with an idcode of {hex(NANDC._idcode)}, from unknown manufacturer"
                        )

                    self._logThreadQueue.put(
                        f"Flash size: {NANDC._density >> 3}MB")

                    assert cOffset < (NANDC._density << 17) and eOffset < (
                        NANDC._density << 17
                    ), "Flash address is out of range"

                elif selPlat["mode"] == 8:
                    NANDC = bcm_nandregs.BCM2133NANDController(
                        self.cmd_read_u32,
                        self.cmd_write_u32,
                        self.cmd_read_u16,
                        self.cmd_write_u16,
                        self.cmd_read_u8,
                        self.cmd_write_u8,
                        page_width=self.page_width,
                    )
                    assert NANDC._idcode not in [
                        0x0,
                        0xFFFFFFFF,
                        0xFFFF0000,
                        0xFFFF00FF,
                    ], "NAND detect failed"

                    MFR_ID_HEX = f"0x{((NANDC._idcode >> 24) & 0xff):02x}"
                    DEV_ID_HEX = f"0x{((NANDC._idcode >> 16) & 0xff):02x}"

                    if self.page_width == -1:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_width = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_16bit"]
                            )

                    if self.cNandSize.Selection == 2:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_size = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_extended"]
                            )

                    if MFR_ID_HEX in self._nand_idcodes["mfrids"]:
                        self._logThreadQueue.put(
                            f'Found NAND with an idcode of {hex(NANDC._idcode)}, which is manufacturered by {self._nand_idcodes["mfrids"][MFR_ID_HEX]}'
                        )

                    else:
                        self._logThreadQueue.put(
                            f"Found NAND with an idcode of {hex(NANDC._idcode)}, from unknown manufacturer"
                        )

                    if DEV_ID_HEX in self._nand_idcodes["devids"]:
                        NAND_INFO = self._nand_idcodes["devids"][DEV_ID_HEX]

                        self._logThreadQueue.put(
                            f'Page size: {NAND_INFO["page_size"] if not NAND_INFO["is_extended"] else (1024 << (NANDC._idcode & 0x3))}'
                        )
                        self._logThreadQueue.put(
                            f'Spare size: {NAND_INFO["spare_size"]}'
                        )
                        self._logThreadQueue.put(
                            f'Flash size: {NAND_INFO["flash_size"] >> 20}MB'
                        )
                        self._logThreadQueue.put(
                            f'Data width: {(16 if NAND_INFO["is_16bit"] else 8)}'
                        )
                        self._logThreadQueue.put(
                            f'Extended ID: {"none" if not NAND_INFO["is_extended"] else hex(NANDC._idcode & 0xff)}'
                        )

                        assert (
                            cOffset < NAND_INFO["flash_size"]
                            and eOffset < NAND_INFO["flash_size"]
                        ), "Flash address is out of range"

                elif selPlat["mode"] == 11:
                    NANDC = pxa3_nandregs.PXA3NANDController(
                        self.cmd_read_u32,
                        self.cmd_write_u32,
                        page_size=(
                            -1
                            if self.cNandSize.Selection == 2
                            else self.cNandSize.Selection
                        ),
                        page_width=self.page_width
                    )

                    _msleep(const._jtag_init_delay)

                    assert NANDC._idcode not in [
                        0x0,
                        0xFFFFFFFF,
                        0xFFFF0000,
                        0xFFFF00FF,
                    ], "NAND detect failed"

                    MFR_ID_HEX = f"0x{((NANDC._idcode >> 24) & 0xff):02x}"
                    DEV_ID_HEX = f"0x{((NANDC._idcode >> 16) & 0xff):02x}"

                    if self.page_width == -1:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_width = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_16bit"]
                            )

                    if self.cNandSize.Selection == 2:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_size = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_extended"]
                            )

                    if MFR_ID_HEX in self._nand_idcodes["mfrids"]:
                        self._logThreadQueue.put(
                            f'Found NAND with an idcode of {hex(NANDC._idcode)}, which is manufacturered by {self._nand_idcodes["mfrids"][MFR_ID_HEX]}'
                        )

                    else:
                        self._logThreadQueue.put(
                            f"Found NAND with an idcode of {hex(NANDC._idcode)}, from unknown manufacturer"
                        )

                    if DEV_ID_HEX in self._nand_idcodes["devids"]:
                        NAND_INFO = self._nand_idcodes["devids"][DEV_ID_HEX]

                        self._logThreadQueue.put(
                            f'Page size: {NAND_INFO["page_size"] if not NAND_INFO["is_extended"] else (1024 << (NANDC._idcode & 0x3))}'
                        )
                        self._logThreadQueue.put(
                            f'Spare size: {NAND_INFO["spare_size"]}'
                        )
                        self._logThreadQueue.put(
                            f'Flash size: {NAND_INFO["flash_size"] >> 20}MB'
                        )
                        self._logThreadQueue.put(
                            f'Data width: {(16 if NAND_INFO["is_16bit"] else 8)}'
                        )
                        self._logThreadQueue.put(
                            f'Extended ID: {"none" if not NAND_INFO["is_extended"] else hex(NANDC._idcode & 0xff)}'
                        )

                        assert (
                            cOffset < NAND_INFO["flash_size"]
                            and eOffset < NAND_INFO["flash_size"]
                        ), "Flash address is out of range"

                elif selPlat["mode"] == 13:
                    NANDC = pnx_nandregs.PNX6NANDController(
                        self.cmd_read_u32,
                        self.cmd_write_u32,
                        selPlat["flash_regs"],
                        (
                            0
                            if self.cNandSize.Selection == 2
                            else self.cNandSize.Selection
                        ),
                        0,
                    )

                    _msleep(const._jtag_init_delay)

                    assert NANDC._idcode not in [
                        0x0,
                        0xFFFFFFFF,
                        0xFFFF0000,
                        0xFFFF00FF,
                    ], "NAND detect failed"

                    MFR_ID_HEX = f"0x{((NANDC._idcode >> 24) & 0xff):02x}"
                    DEV_ID_HEX = f"0x{((NANDC._idcode >> 16) & 0xff):02x}"

                    if self.page_width == -1:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_width = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_16bit"]
                            )
                    else:
                        NANDC._page_width = self.page_width

                    if self.cNandSize.Selection == 2:
                        if DEV_ID_HEX in self._nand_idcodes["devids"]:
                            NANDC._page_size = int(
                                self._nand_idcodes["devids"][DEV_ID_HEX]["is_extended"]
                            )

                    if MFR_ID_HEX in self._nand_idcodes["mfrids"]:
                        self._logThreadQueue.put(
                            f'Found NAND with an idcode of {hex(NANDC._idcode)}, which is manufacturered by {self._nand_idcodes["mfrids"][MFR_ID_HEX]}'
                        )

                    else:
                        self._logThreadQueue.put(
                            f"Found NAND with an idcode of {hex(NANDC._idcode)}, from unknown manufacturer"
                        )

                    if DEV_ID_HEX in self._nand_idcodes["devids"]:
                        NAND_INFO = self._nand_idcodes["devids"][DEV_ID_HEX]

                        self._logThreadQueue.put(
                            f'Page size: {NAND_INFO["page_size"] if not NAND_INFO["is_extended"] else (1024 << (NANDC._idcode & 0x3))}'
                        )
                        self._logThreadQueue.put(
                            f'Spare size: {NAND_INFO["spare_size"]}'
                        )
                        self._logThreadQueue.put(
                            f'Flash size: {NAND_INFO["flash_size"] >> 20}MB'
                        )
                        self._logThreadQueue.put(
                            f'Data width: {(16 if NAND_INFO["is_16bit"] else 8)}'
                        )
                        self._logThreadQueue.put(
                            f'Extended ID: {"none" if not NAND_INFO["is_extended"] else hex(NANDC._idcode & 0xff)}'
                        )

                        assert (
                            cOffset < NAND_INFO["flash_size"]
                            and eOffset < NAND_INFO["flash_size"]
                        ), "Flash address is out of range"

            if self.cNandSize.Selection == 2 and NANDC is not None:
                flash_div = (
                    (0x800 if NANDC._page_size == 1 else 0x200)
                    if const._platforms[self.cChipset.Selection]["mode"] not in [7, 10]
                    else (0x1000 if NANDC._page_size == 1 else 0x800)
                )

                if (cOffset % flash_div) != 0 or (eOffset % flash_div) != 0:
                    raise Exception(
                        f"offset not divisible by {hex(flash_div)} is not supported")

            time.sleep(1)
            self._logSupressed = True
            self._logThreadQueue.put(
                f"Dump flash started {datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            if self._isConnectRemote and self._sio:
                self._sio.emit("command", {"c": "isSupressed", "d": True})

            CFI_READ_BUFFER = self.nor_read_size

            read_times = []

            with open(name, "wb") as tempFile:
                sOffset = cOffset

                if not self.check_identical_reads:
                    while cOffset < eOffset and not self._isReadCanceled:
                        readTimeStart = time.perf_counter()

                        if self._loaded_dcc is not None or selPlat["mode"] in [-1, 4]:
                            tempFile.write(
                                self.cmd_read_flash(
                                    cOffset - self._cfi_start_offset,
                                    min(CFI_READ_BUFFER, eOffset - cOffset),
                                )
                            )
                            cOffset += min(CFI_READ_BUFFER, eOffset - cOffset)

                        elif (self.fast_api and selPlat["mode"] in [1, 2, 3, 5, 9, 12]):
                            data, spare = self.cmd_read_nand(
                                page_mode, cOffset, 16)
                            cOffset += (0x800 if page_mode ==
                                        1 else 0x200) * 16

                            tempFile.write(data)
                            spareBuf += spare

                        elif NANDC is not None:
                            data, spare, bbm = NANDC.read(
                                cOffset
                                >> (
                                    (11 if NANDC._page_size == 1 else 9)
                                    if selPlat["mode"] not in [7, 10]
                                    else (12 if NANDC._page_size == 1 else 11)
                                )
                            )

                            tempFile.write(data)
                            spareBuf += spare
                            bbBuf += bbm

                            if self.nand_format == 1:
                                tempFile.write(spare)

                            cOffset += (
                                (0x800 if NANDC._page_size == 1 else 0x200)
                                if selPlat["mode"] not in [7, 10]
                                else (
                                    0x1000 if NANDC._page_size == 1 else 0x800
                                )
                            )

                        else:
                            raise NotImplementedError()

                        readTimeEnd = time.perf_counter()

                        read_times.append(readTimeEnd-readTimeStart)
                        if len(read_times) > 50:
                            read_times.pop(0)

                        self._progMsgQueue.put(
                            [cOffset / eOffset, f"Read {hex(cOffset)} of {hex(eOffset)}, average time of last 50 commands: {round(sum(read_times)/len(read_times), 4)}"])

                else:
                    if self.identical_check_mode == 0:
                        inconsistentReads = []

                        while cOffset < eOffset and not self._isReadCanceled:
                            readTimeStart = time.perf_counter()

                            checkTemp = []
                            checkTempHash = []

                            isInconsistent = True

                            if self._loaded_dcc is not None or selPlat["mode"] in [
                                -1,
                                4,
                            ]:
                                for _ in range(self.max_read_pass):
                                    tempData = self.cmd_read_flash(
                                        cOffset - self._cfi_start_offset,
                                        min(CFI_READ_BUFFER, eOffset - cOffset),
                                    )
                                    tempHash = hashlib.sha256(
                                        tempData).hexdigest()

                                    checkTemp.append(tempData)
                                    checkTempHash.append(tempHash)

                                    if (
                                        checkTempHash.count(tempHash)
                                        >= self.max_identical_read
                                    ):
                                        isInconsistent = False
                                        break

                                if isInconsistent:
                                    inconsistentReads.append(cOffset)
                                tempFile.write(tempData)
                                cOffset += min(CFI_READ_BUFFER,
                                               eOffset - cOffset)

                            elif (self.fast_api and selPlat["mode"] in [1, 2, 3, 5, 9, 12]):
                                for _ in range(self.max_read_pass):
                                    data, spare = self.cmd_read_nand(
                                        page_mode, cOffset, 16)

                                    tempData = data + spare
                                    tempHash = hashlib.sha256(
                                        tempData).hexdigest()

                                    checkTemp.append(tempData)
                                    checkTempHash.append(tempHash)

                                    if (
                                        checkTempHash.count(tempHash)
                                        >= self.max_identical_read
                                    ):
                                        isInconsistent = False
                                        break

                                if isInconsistent:
                                    inconsistentReads.append(cOffset)

                                tempFile.write(data)
                                spareBuf += spare

                                cOffset += (0x800 if page_mode ==
                                            1 else 0x200) * 16

                            elif NANDC is not None:
                                for _ in range(self.max_read_pass):
                                    data, spare, bbm = NANDC.read(
                                        cOffset
                                        >> (
                                            (11 if NANDC._page_size == 1 else 9)
                                            if selPlat["mode"] not in [7, 10]
                                            else (
                                                12
                                                if NANDC._page_size == 1
                                                else 11
                                            )
                                        )
                                    )

                                    tempData = data + spare + bbm
                                    tempHash = hashlib.sha256(
                                        tempData).hexdigest()

                                    checkTemp.append(tempData)
                                    checkTempHash.append(tempHash)

                                    if (
                                        checkTempHash.count(tempHash)
                                        >= self.max_identical_read
                                    ):
                                        isInconsistent = False
                                        break

                                if isInconsistent:
                                    inconsistentReads.append(cOffset)

                                tempFile.write(data)
                                spareBuf += spare
                                bbBuf += bbm

                                if self.nand_format == 1:
                                    tempFile.write(spare)

                                cOffset += (
                                    (0x800 if NANDC._page_size == 1 else 0x200)
                                    if selPlat["mode"] not in [7, 10]
                                    else (
                                        0x1000
                                        if NANDC._page_size == 1
                                        else 0x800
                                    )
                                )

                            else:
                                raise NotImplementedError()

                            readTimeEnd = time.perf_counter()

                            read_times.append(readTimeEnd-readTimeStart)
                            if len(read_times) > 50:
                                read_times.pop(0)

                            self._progMsgQueue.put(
                                [cOffset / eOffset, f"Read {hex(cOffset)} of {hex(eOffset)}, average time of last 50 commands: {round(sum(read_times)/len(read_times), 4)}"])

                        if len(inconsistentReads) >= 1:
                            self._logThreadQueue.put(
                                f"Inconsistent reads: {' '.join([hex(x) for x in inconsistentReads])}"
                            )

                    elif self.identical_check_mode == 1:
                        tempFilesHash = []
                        if self.nand_mode == 1:
                            raise Exception(
                                "Check for identical reads by reading the entire flash option doesn't work on interleaved NAND format.")

                        for c in range(self.max_read_pass):
                            if self._isReadCanceled:
                                break

                            spareBuf.clear()
                            bbBuf.clear()
                            cOffset = sOffset

                            with tempfile.TemporaryFile(
                                prefix="dumpit_", suffix=".bin"
                            ) as tempFileTemp:
                                while cOffset < eOffset and not self._isReadCanceled:
                                    readTimeStart = time.perf_counter()

                                    if self._loaded_dcc is not None or selPlat[
                                        "mode"
                                    ] in [-1, 4]:
                                        tempFileTemp.write(
                                            self.cmd_read_flash(
                                                cOffset - self._cfi_start_offset,
                                                min(CFI_READ_BUFFER,
                                                    eOffset - cOffset),
                                            )
                                        )
                                        cOffset += min(
                                            CFI_READ_BUFFER, eOffset - cOffset
                                        )

                                    elif (self.fast_api and selPlat["mode"] in [1, 2, 3, 5, 9, 12]):
                                        data, spare = self.cmd_read_nand(
                                            page_mode, cOffset, 16)
                                        cOffset += (0x800 if page_mode ==
                                                    1 else 0x200) * 16

                                        tempFileTemp.write(data)
                                        spareBuf += spare

                                    elif NANDC is not None:
                                        data, spare, bbm = NANDC.read(
                                            cOffset
                                            >> (
                                                (
                                                    11
                                                    if NANDC._page_size == 1
                                                    else 9
                                                )
                                                if selPlat["mode"] not in [7, 10]
                                                else (
                                                    12
                                                    if NANDC._page_size == 1
                                                    else 11
                                                )
                                            )
                                        )

                                        tempFileTemp.write(data)
                                        spareBuf += spare
                                        bbBuf += bbm

                                        cOffset += (
                                            (
                                                0x800
                                                if NANDC._page_size == 1
                                                else 0x200
                                            )
                                            if selPlat["mode"] not in [7, 10]
                                            else (
                                                0x1000
                                                if NANDC._page_size == 1
                                                else 0x800
                                            )
                                        )

                                    else:
                                        raise NotImplementedError()

                                    readTimeEnd = time.perf_counter()

                                    read_times.append(
                                        readTimeEnd-readTimeStart)
                                    if len(read_times) > 50:
                                        read_times.pop(0)

                                    self._progMsgQueue.put(
                                        [cOffset / eOffset, f"Read {hex(cOffset)} of {hex(eOffset)}, average time of last 50 commands: {round(sum(read_times)/len(read_times), 4)}"])

                                if self._isReadCanceled:
                                    break

                                end = tempFileTemp.tell()

                                tempFileTemp.seek(0)
                                tempHashInst = hashlib.sha256(tempData)

                                while tempFileTemp.tell() < end:
                                    tempHashInst.update(
                                        tempFileTemp.read(0x200))

                                tempHash = tempHashInst.hexdigest()
                                tempFilesHash.append(tempHash)

                                if (
                                    tempFilesHash.count(tempHash)
                                    >= self.max_identical_read
                                ):
                                    self._logThreadQueue.put(
                                        f"This dump is consistent for {self.max_identical_read} consecutive times"
                                    )
                                    tempFileTemp.seek(0)
                                    while tempFileTemp.tell() < end:
                                        tempFile.write(
                                            tempFileTemp.read(0x8000))
                                    break

                                elif c >= (self.max_read_pass - 1):
                                    tempFileTemp.seek(0)
                                    while tempFileTemp.tell() < end:
                                        tempFile.write(
                                            tempFileTemp.read(0x8000))

                if self.nand_format == 0:
                    spare_start_offset = tempFile.tell()
                    tempFile.write(spareBuf)

                    if not self.metadata["ignore_metadata"]:
                        bbm_start_offset = tempFile.tell()
                        tempFile.write(bbBuf)

                elif self.nand_format == 2:
                    open(f'{os.path.splitext(name)[0]}_spare{os.path.splitext(name)[1]}', "wb").write(
                        spareBuf)
                    if len(bbBuf) > 0:
                        open(f'{os.path.splitext(name)[0]}_additional{os.path.splitext(name)[1]}', "wb").write(
                            bbBuf)

                self._logThreadQueue.put(
                    f"Dump flash finished {datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}"
                )

                if not self.metadata["ignore_metadata"] and self.nand_format == 0:
                    tempFile.write(
                        self._generateMetadata(
                            [
                                {
                                    "name": "FLASH",
                                    "flash_offset": sOffset,
                                    "data_offset": 0x00,
                                    "data_size": spare_start_offset,
                                    "spare_offset": spare_start_offset,
                                    "spare_size": len(spareBuf),
                                    "bbm_offset": bbm_start_offset,
                                    "bbm_size": len(bbBuf),
                                }
                            ],
                            self.metadata["device_name"],
                            self.metadata["device_manufacturer"],
                            0x200 if NANDC is None else (
                                (0x800 if NANDC._page_size == 1 else 0x200)
                                if selPlat["mode"] not in [7, 10]
                                else (
                                    0x1000
                                    if NANDC._page_size == 1
                                    else 0x800
                                )
                            ),
                            self.idcode,
                            (
                                0
                                if NANDC is None
                                else (1 if selPlat["mode"] not in [7, 10] else 2)
                            ),
                            self.remotePerformer
                            if self._isConnectRemote
                            else self.metadata["performer"],
                            self.metadata["device_version"],
                            self.remoteAssistant if self._isConnectRemote else "",
                            self.remoteLender
                            if self._isConnectRemote
                            else self.metadata["lender"],
                        )
                    )

        except Exception as e:
            traceback.print_exc()
            self._doAnalytics("error", error=str(
                e), traceback=traceback.format_exc())
            self._errMsgQueue.put(str(e))

        finally:
            time.sleep(1)
            self._btnMsgQueue.put(False)
            self._isRead = False
            self._isReadCanceled = False
            if self._isConnectRemote and self._sio:
                self._sio.emit("command", {"c": "isRead", "d": False})
            self._logSupressed = False
            if self._isConnectRemote and self._sio:
                self._sio.emit("command", {"c": "isSupressed", "d": False})

            self._doAnalytics(
                "dump_end", addr_start=cOffset, addr_end=eOffset, is_memory=False
            )

    def _generateMetadata(
        self,
        regions: typing.List[dict],
        device_name: str,
        manufacturer: str,
        chip_size: int,
        idcode: int,
        flash_type: int,
        performer: str,
        device_version: str = "",
        assistant: str = "",
        lender: str = "",
    ):
        tempDump = io.BytesIO(bytes(4096))
        tempDump.seek(0)

        tempDump.write(b"DUMPINFO")
        tempDump.write(struct.pack("<LL", 1, len(regions)))

        def _packString(data: str):
            tempDump.write(
                struct.pack("<L", len(data.encode("utf-8"))) +
                data.encode("utf-8")
            )

        for r in regions:
            _packString(r["name"])
            tempDump.write(
                struct.pack(
                    "<LLLLLLLLLL",
                    idcode,
                    chip_size,
                    flash_type,
                    r["flash_offset"],
                    r["data_offset"],
                    r["data_size"],
                    r["spare_offset"],
                    r["spare_size"],
                    r["bbm_offset"],
                    r["bbm_size"],
                )
            )

        _packString(manufacturer)
        _packString(device_name)
        _packString(device_version)
        _packString(performer)
        _packString(assistant)
        _packString(lender)

        return tempDump.getvalue()

    def doReadFlash(self, event):
        if (not self._isConnect and not self._isConnectRemote) or self._isRead:
            return

        cOffset = int(self.tStart.Value, 16)
        eOffset = int(self.tEnd.Value, 16)

        if cOffset >= eOffset:
            return wx.MessageBox(
                f"start offset must be less than end offset",
                "Dumpit",
                wx.OK | wx.CENTER | wx.ICON_ERROR,
                self,
            )

        flash_div = 1 if self.cNandSize.Selection == 2 else (
            (0x800 if self.cNandSize.Selection == 1 else 0x200)
            if const._platforms[self.cChipset.Selection]["mode"] not in [7, 10]
            else (0x1000 if self.cNandSize.Selection == 1 else 0x800)
        )

        if (cOffset % flash_div) != 0 or (eOffset % flash_div) != 0:
            return wx.MessageBox(
                f"offset not divisible by {hex(flash_div)} is not supported",
                "Dumpit",
                wx.OK | wx.CENTER | wx.ICON_ERROR,
                self,
            )

        with wx.FileDialog(
            self, "Dump flash", wildcard="Binary file|*.bin", style=wx.FD_SAVE
        ) as fd:
            fd: wx.FileDialog
            if fd.ShowModal() != wx.ID_CANCEL:
                self.progress.Value = 0
                if self._isConnectRemote and self._sio:
                    self._sio.emit("command", {"c": "progress", "d": 0})

                O1N_INPUT_OFFSET = -1

                if (
                    const._platforms[self.cChipset.Selection]["mode"] == 7
                    and "o1n_offset" not in const._platforms[self.cChipset.Selection]
                ):
                    try:
                        with wx.TextEntryDialog(
                            self, "Enter OneNAND base offset", "Dumpit"
                        ) as t:
                            t: wx.TextEntryDialog
                            if t.ShowModal() == wx.ID_CANCEL:
                                return

                            O1N_INPUT_OFFSET = int(t.Value, 16)

                    except Exception as e:
                        wx.MessageBox(
                            str(e), "Dumpit", wx.OK | wx.CENTER | wx.ICON_ERROR, self
                        )
                        return

                self._dumpThread = threading.Thread(
                    target=self.doReadFlashThread,
                    args=(fd.GetPath(), cOffset, eOffset, O1N_INPUT_OFFSET),
                )
                self._dumpThread.daemon = True

                self._dumpThread.start()

    def doStop(self, event):
        self._isReadCanceled = True
        if self._isConnectRemote and self._sio:
            self._sio.emit("command", {"c": "doStopRead"})
        self.bStop.Enable(False)

    def doGo(self, event):
        if not self._isConnect and not self._isConnectRemote:
            return
        self._ocdSendCommand("resume")

    def doHalt(self, event):
        if not self._isConnect and not self._isConnectRemote:
            return
        self._ocdSendCommand("halt")

    def doReset(self, event):
        if not self._isConnect and not self._isConnectRemote:
            return
        self._isInitDone = False
        if self._isConnectRemote and self._sio:
            self._sio.emit("command", {"c": "initUndone"})
        _msleep(self.reset_delay * 1000)
        self._ocdSendCommand("soft_reset_halt")

    def doHardReset(self, event):
        if not self._isConnect and not self._isConnectRemote:
            return
        self._isInitDone = False
        if self._isConnectRemote and self._sio:
            self._sio.emit("command", {"c": "initUndone"})
        _msleep(self.reset_delay * 1000)
        self._ocdSendCommand("reset init")

    def doLoader(self, event):
        with wx.FileDialog(
            self, "Load DCC", wildcard="DCC Hex file|*.hex", style=wx.FD_OPEN
        ) as fd:
            fd: wx.FileDialog
            if fd.ShowModal() != wx.ID_CANCEL:
                self._loaded_dcc = fd.GetPath()
            else:
                self._loaded_dcc = None

            self.lCurrentDCC.SetLabel(f"DCC Loader: {self._loaded_dcc}")

            path_escaped = pathlib.Path(self._loaded_dcc).as_posix()
            self._ocdSendCommand(
                "set _DCC_PATH {"
                + path_escaped
                + "}; "
                + f"set _DCC_START_OFFSET {hex(intelhex.IntelHex(self._loaded_dcc).minaddr())}"
            )

    def doScript(self, event):
        if not self._isConnect:
            return  # No way to execute scripts in Remote

        with wx.FileDialog(
            self, "Load Script", wildcard="JIM TCL Script|*.tcl", style=wx.FD_OPEN
        ) as fd:
            fd: wx.FileDialog
            if fd.ShowModal() != wx.ID_CANCEL:
                path_escaped = pathlib.Path(fd.GetPath()).as_posix()
                self._ocdSendCommand("script {" + path_escaped + "}")

    def doDisableMMU(self, event):
        if not self._isConnect and not self._isConnectRemote:
            return
        cp15 = self.cmd_read_cp15(1, 0, 0, 0)
        self.cmd_write_cp15(1, 0, 0, 0, cp15 & 0xFFFFFFFE)

    def doEnableMMU(self, event):
        if not self._isConnect and not self._isConnectRemote:
            return
        cp15 = self.cmd_read_cp15(1, 0, 0, 0)
        self.cmd_write_cp15(1, 0, 0, 0, cp15 | 1)

    def doExecAddress(self, event):
        if not self._isConnect and not self._isConnectRemote:
            return
        offsetDialog = wx.TextEntryDialog(self, "Execute Address")
        offsetDialog.Bind(wx.EVT_TEXT, self.doHexCheck)

        if offsetDialog.ShowModal() == wx.ID_CANCEL:
            return
        self._ocdSendCommand(f"resume 0x{offsetDialog.Value}")

    def loadNoteBook(self, event):
        self.pSettingsNull.Hide()
        self.pSettingsFT232R.Hide()
        self.pSettingsFT232H.Hide()
        self.pSettingsGPIOD.Hide()
        self.pSettingsParPort.Hide()
        self.pSettingsRemoteBitbang.Hide()

        if self.cInterface.Selection == 0:
            self.pSettingsFT232R.Show()

        elif self.cInterface.Selection == 1:
            self.pSettingsFT232H.Show()

        elif self.cInterface.Selection == 3:
            self.pSettingsGPIOD.Show()

        elif self.cInterface.Selection == 4:
            self.pSettingsParPort.Show()

        elif self.cInterface.Selection == 5:
            self.pSettingsRemoteBitbang.Show()

        else:
            self.pSettingsNull.Show()

        temp_analytics = "Tracking count:\n"

        for k in _PTRACKCOUNT:
            temp_analytics += f"{k}: {_PTRACKCOUNT[k]}\n"

        self.analytics_stat.Value = temp_analytics

        self.Layout()

    def doOpenFT232RConfig(self, event):
        FT232RConfig(self).ShowModal()

    def doOpenFT232HConfig(self, event):
        FT232HConfig(self).ShowModal()

    def doOpenGPIODConfig(self, event):
        wx.MessageBox(
            "Not implemented", "Dumpit", wx.OK | wx.CENTER | wx.ICON_ERROR, self
        )

    def doFT232AdapterChange(self, event):
        event.Skip()

    def doIDCODE(self, event):
        if self._isConnect or self._isConnectRemote:
            return
        self.finderStatus.Value = ""

        try:
            if self.cInterface.Selection == 0:
                p = libfindit.find_jtag_idcode(f"ftdi://{self.tUSBID.Value}/1")

            elif self.cInterface.Selection == 1:
                p = libfindit.find_jtag_idcode(
                    f"ftdi://{self.tUSBID1.Value}/{self.cChannel.Selection+1}",
                    mpsse=self.bUseMPSSE.Value,
                )

            elif self.cInterface.Selection == len(const._interfaces) - 1:
                p = libfindit.find_jtag_idcode("", True)

            else:
                return

            if len(p) >= 1:
                self.finderStatus.Value = f"IDCODE: {' '.join(p[0]['idcodes'])}\nTDO: {p[0]['tdo']}\nTCK: {p[0]['tck']}\nTMS: {p[0]['tms']}\n#TRST: {' '.join(str(x) for x in p[0]['possible_ntrst'])}"
                self._known_tdo = p[0]["tdo"]
                self._known_tck = p[0]["tck"]
                self._known_tms = p[0]["tms"]

            else:
                self.finderStatus.Value = "No JTAG Found!"

        except Exception as e:
            traceback.print_exc()
            self._doAnalytics("error", error=str(
                e), traceback=traceback.format_exc())
            wx.MessageBox(str(e), "Dumpit", wx.OK |
                          wx.CENTER | wx.ICON_ERROR, self)

    def doBYPASS(self, event):
        if self._isConnect or self._isConnectRemote:
            return
        self.finderStatus.Value = ""

        try:
            if self.cInterface.Selection == 0:
                p = libfindit.find_jtag_bypass(
                    f"ftdi://{self.tUSBID.Value}/1",
                    known_tdo=self._known_tdo,
                    known_tck=self._known_tck,
                    known_tms=self._known_tms,
                )

            elif self.cInterface.Selection == 1:
                p = libfindit.find_jtag_bypass(
                    f"ftdi://{self.tUSBID1.Value}/{self.cChannel.Selection+1}",
                    mpsse=self.bUseMPSSE.Value,
                    known_tdo=self._known_tdo,
                    known_tck=self._known_tck,
                    known_tms=self._known_tms,
                )

            elif self.cInterface.Selection == len(const._interfaces) - 1:
                p = libfindit.find_jtag_bypass(
                    "",
                    True,
                    known_tdo=self._known_tdo,
                    known_tck=self._known_tck,
                    known_tms=self._known_tms,
                )

            else:
                return

            if len(p) >= 1:
                self.finderStatus.Value = f"TDI: {p[0]['tdi']}\nTDO: {p[0]['tdo']}\nTCK: {p[0]['tck']}\nTMS: {p[0]['tms']}\n#TRST: {' '.join(str(x) for x in p[0]['possible_ntrst'])}"

                self._known_tdi = p[0]["tdi"]
                self._known_tdo = p[0]["tdo"]
                self._known_tck = p[0]["tck"]
                self._known_tms = p[0]["tms"]

            else:
                self.finderStatus.Value = "No JTAG Found!"

        except Exception as e:
            traceback.print_exc()
            self._doAnalytics("error", error=str(
                e), traceback=traceback.format_exc())
            wx.MessageBox(str(e), "Dumpit", wx.OK |
                          wx.CENTER | wx.ICON_ERROR, self)

    def doRTCK(self, event):
        if self._isConnect or self._isConnectRemote:
            return
        self.finderStatus.Value = ""

        try:
            if self.cInterface.Selection == 0:
                p = libfindit.find_jtag_rtck(
                    f"ftdi://{self.tUSBID.Value}/1", known_tck=self._known_tck
                )

            elif self.cInterface.Selection == 1:
                p = libfindit.find_jtag_rtck(
                    f"ftdi://{self.tUSBID1.Value}/{self.cChannel.Selection+1}",
                    mpsse=self.bUseMPSSE.Value,
                    known_tck=self._known_tck,
                )

            elif self.cInterface.Selection == len(const._interfaces) - 1:
                p = libfindit.find_jtag_rtck(
                    "", True, known_tck=self._known_tck)

            else:
                return

            if len(p) >= 1:
                self.finderStatus.Value = f"#RTCK: {' '.join(str(x) for x in p)}"

            else:
                self.finderStatus.Value = "No RTCK Found!"

        except Exception as e:
            traceback.print_exc()
            self._doAnalytics("error", error=str(
                e), traceback=traceback.format_exc())
            wx.MessageBox(str(e), "Dumpit", wx.OK |
                          wx.CENTER | wx.ICON_ERROR, self)

    def doQuit(self, event: wx.CloseEvent):
        if (
            wx.MessageBox(
                "Exit Dumpit?", "Dumpit", wx.YES_NO | wx.CENTER | wx.ICON_QUESTION, self
            )
            == wx.YES
        ):
            if self._isConnect:
                self._isConnect = False
                self._ocd.terminate()
                if self._isForward and self._isConnectRemote:
                    self._isConnectRemote = False
                    self._isForward = False
                    if self._sio and self._sio.connected:
                        try:
                            self._sio.call("bye", "", timeout=30)
                        except Exception:
                            pass
                        self._sio.disconnect()

            elif self._isConnectRemote:
                self._isConnectRemote = False
                if self._sio and self._sio.connected:
                    try:
                        self._sio.call("bye", "", timeout=30)
                    except Exception:
                        pass
                    self._sio.disconnect()

            cfg = {}

            cfg["interface"] = self.cInterface.Selection
            cfg["speed"] = self.nSpeed.Value
            cfg["chipset"] = self.cChipset.Selection
            cfg["target"] = self.cTarget.Selection
            cfg["tap"] = self.cTap.Selection
            cfg["ir"] = self.nIR.Value
            cfg["reset_mode"] = self.cResetMode.Selection
            cfg["trst_reset_pulse"] = self.ntrst_reset_pulse
            cfg["srst_reset_pulse"] = self.nsrst_reset_pulse
            cfg["trst_reset_delay"] = self.ntrst_reset_delay
            cfg["srst_reset_delay"] = self.nsrst_reset_delay
            cfg["reset_delay"] = self.reset_delay
            cfg["custom_reset"] = self.custom_reset
            cfg["skip_init"] = self.bSkipInit.Value
            cfg["start"] = self.tStart.Value
            cfg["end"] = self.tEnd.Value
            cfg["nand_size"] = self.cNandSize.Selection
            cfg["ecc_disabled"] = self.bECCDisable.Value
            cfg["bad_blocks_in_data"] = self.bBadBlockinData.Value
            cfg["target_remote"] = self.bTargetRemote.Value
            cfg["use_gdb"] = self.bUseGDB.Value

            cfg["ft232r_usb_id"] = self.tUSBID.Value
            cfg["ft232r_restore_serial"] = self.tRestoreSerial.Value
            cfg["ft232r_tdi"] = self._ft232r_tdi
            cfg["ft232r_tdo"] = self._ft232r_tdo
            cfg["ft232r_tms"] = self._ft232r_tck
            cfg["ft232r_tck"] = self._ft232r_tms
            cfg["ft232r_trst"] = self._ft232r_trst
            cfg["ft232r_srst"] = self._ft232r_srst

            cfg["ft232h_adapter"] = self.cFTAdapter.Selection
            cfg["ft232h_usb_id"] = self.tUSBID1.Value
            cfg["ft232h_channel"] = self.cChannel.Selection
            cfg["ft232h_sampling_edge"] = self.rSamplingEdge.Selection
            cfg["ft232h_tdi"] = self._ft232h_tdi
            cfg["ft232h_tdo"] = self._ft232h_tdo
            cfg["ft232h_tck"] = self._ft232h_tck
            cfg["ft232h_tms"] = self._ft232h_tms
            cfg["ft232h_trst"] = self._ft232h_trst
            cfg["ft232h_srst"] = self._ft232h_srst

            cfg["ft232h_pins"] = self._ft232h_pins

            cfg["gpio_chip"] = self.nGPIODChip.Value
            cfg["gpio_tdi"] = self._gpio_tdi
            cfg["gpio_tdo"] = self._gpio_tdo
            cfg["gpio_tck"] = self._gpio_tck
            cfg["gpio_tms"] = self._gpio_tms
            cfg["gpio_trst"] = self._gpio_trst
            cfg["gpio_srst"] = self._gpio_srst

            cfg["parport_cable"] = self.cParCable.Selection
            cfg["parport_port"] = self.tParPort.Value

            cfg["remote_bitbang_host"] = self.tRBBHost.Value
            cfg["remote_bitbang_port"] = self.tRBBPort.Value

            cfg["finder_use_mpsse"] = self.bUseMPSSE.Value

            cfg["enable_analytics"] = self.bEnableAnalytics.Value
            cfg["user_id"] = self.tUserID.Value

            cfg["tracking_count"] = _PTRACKCOUNT
            cfg["debug_log"] = self._debug_logs

            cfg["nand_skip_init"] = self.skip_init
            cfg["nand_skip_init_gpio"] = self.skip_gpio_init
            cfg["nand_custom_cfg1"] = self.custom_cfg1
            cfg["nand_custom_cfg2"] = self.custom_cfg2
            cfg["nand_custom_cfg_common"] = self.custom_cfg_common
            cfg["nand_device_id"] = self.nand_dev_id
            cfg["nand_page_width"] = self.page_width

            cfg["nand_init_code"] = self.nand_init_code
            cfg["msm6550_discrepancy"] = self.msm6550_discrepancy
            cfg["nand_out_format"] = self.nand_format
            cfg["use_fast_api"] = self.fast_api

            cfg["read_size"] = self.nor_read_size
            cfg["max_read_pass"] = self.max_read_pass
            cfg["max_identical"] = self.max_identical_read
            cfg["check_identical"] = self.check_identical_reads
            cfg["disable_platform_options"] = self.disable_platform_options
            cfg["identical_check_mode"] = self.identical_check_mode

            cfg["metadata"] = self.metadata

            cfg["last_updated"] = int(datetime.datetime.today().timestamp())

            json.dump(
                cfg,
                open(
                    os.path.join(os.path.dirname(__file__),
                                 "dumpit_config.json"), "w"
                ),
                indent=4,
            )

            wx.Exit()

    def doOCDCmdExecThread(self, cmd):
        self._logThreadQueue.put(
            f"command returned: {self._ocdSendCommand(cmd)}")

    def doOCDCmdExec(self, event):
        temp = self.tOCDCmd.Value
        self.tOCDCmd.Value = ""
        if not self._isConnect and not self._isConnectRemote:
            return

        t = threading.Thread(target=self.doOCDCmdExecThread, args=(temp,))

        t.daemon = True
        t.start()

        if len(self._command_history) <= 0 or self._command_history[-1] != temp:
            self._command_history.append(temp)
            if len(self._command_history) > 25:
                self._command_history.pop(0)

        self._command_history_index = len(self._command_history)

    def doRegenUUID(self, event):
        global _PTRACKCOUNT
        self.tUserID.Value = str(uuid.uuid4())
        _PTRACKCOUNT = {}

        temp_analytics = "Tracking count:\n"

        for k in _PTRACKCOUNT:
            temp_analytics += f"{k}: {_PTRACKCOUNT[k]}\n"

        self.analytics_stat.Value = temp_analytics

    def bDoConfigureReset(self, event):
        ResetConfig(self).ShowModal()

    def doNANDConfigure(self, event):
        NANDControllerConfig(self).ShowModal()

    def doConfigureRead(self, event):
        TargetReadConfig(self).ShowModal()

    def doEditMetadata(self, event):
        UserMetadataConfig(self).ShowModal()

    def doProcessSpeedEntry(self, event: wx.CommandEvent):
        self._ocdSendCommand(f"adapter speed {self.nSpeed.Value}")

    def doProcessResetMode(self, event: wx.CommandEvent):
        self._ocdSendCommand(
            f"reset_config {const._reset_type[self.cResetMode.Selection][1]}"
        )

    def doProcessCmdArrow(self, event):
        if event.KeyCode == wx.WXK_UP:
            if self._command_history_index <= 0:
                return
            self._command_history_index -= 1

            self.tOCDCmd.Value = self._command_history[self._command_history_index]

            self.tOCDCmd.SetInsertionPointEnd()

        elif event.KeyCode == wx.WXK_DOWN:
            if self._command_history_index >= len(self._command_history):
                return
            self._command_history_index += 1

            if self._command_history_index == len(self._command_history):
                self.tOCDCmd.Value = ""

            else:
                self.tOCDCmd.Value = self._command_history[self._command_history_index]

            self.tOCDCmd.SetInsertionPointEnd()

        else:
            event.Skip()

    def doScanChain(self, event: wx.CommandEvent):
        IC = getInitCmd(self, True)

        self.status.Value = f'Command-line arguments: openocd -c "{IC}"\n\n'
        self._ocd = subprocess.Popen(
            [getOCDExec(), "-c", IC],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # cwd=os.path.dirname(__file__),
        )

        self._logThreadQueue = queue.Queue()

        self._logThread = threading.Thread(target=self._doLogging)
        self._logThread.daemon = True

        self._logThread.start()
        self._ocd.wait()


def getInitCmd(self: MainApp, scanMode: bool = False):
    cInit = (
        const._interfaces[self.cInterface.Selection][1]
        .replace("(FT232R_VID)", self.tUSBID.Value.split(":")[0])
        .replace("(FT232R_PID)", self.tUSBID.Value.split(":")[1])
        .replace("(FT232R_RESTORE_SERIAL)", self.tRestoreSerial.Value)
        .replace("(FT232H_VID)", self.tUSBID1.Value.split(":")[0])
        .replace("(FT232H_PID)", self.tUSBID1.Value.split(":")[1])
        .replace("(FT232H_CHANNEL)", str(self.cChannel.Selection))
        .replace("(FT232H_EDGE)", ["rising", "falling"][self.rSamplingEdge.Selection])
        .replace("(FT232H_PINS)", hex(self._ft232h_pins))
        .replace("(FT232H_DIR)", hex(self._ft232h_dirs))
        .replace(
            "(FT232H_LAYOUT_SIGNAL)",
            f"ftdi layout_signal nTRST -data {hex(1 << self._ft232h_trst)} -oe {hex(1 << self._ft232h_trst)}; ftdi layout_signal nSRST -data {hex(1 << self._ft232h_srst)} -oe {hex(1 << self._ft232h_srst)}; ftdi layout_signal TDI -data {hex(1 << self._ft232h_tdi)}; ftdi layout_signal TDO -data {hex(1 << self._ft232h_tdo)} -oe {hex(1 << self._ft232h_tdo)}; ftdi layout_signal TCK -data {hex(1 << self._ft232h_tck)}; ftdi layout_signal TMS -data {hex(1 << self._ft232h_tms)}",
        )
        .replace("(FT232R_PINS)", "")
        .replace("(GPIOD_CHIP)", str(self.nGPIODChip.Value))
        .replace("(GPIOD_TDI_PIN)", str(self._gpio_tdi))
        .replace("(GPIOD_TDO_PIN)", str(self._gpio_tdo))
        .replace("(GPIOD_TCK_PIN)", str(self._gpio_tck))
        .replace("(GPIOD_TMS_PIN)", str(self._gpio_tms))
        .replace("(GPIOD_TRST_PIN)", str(self._gpio_trst))
        .replace("(GPIOD_SRST_PIN)", str(self._gpio_srst))
        .replace("(PARPORT_CABLE)", ["dlc5", "wiggler"][self.cParCable.Selection])
        .replace("(PARPORT_PORT)", self.tParPort.Value)
        .replace("(REMOTE_BITBANG_HOST)", self.tRBBHost.Value)
        .replace("(REMOTE_BITBANG_PORT)", self.tRBBPort.Value)
    )

    if self.cInterface.Selection == 1:
        if const._ft232h_adapters[self.cFTAdapter.Selection][1] != "":
            cInit = f"{const._ft232h_adapters[self.cFTAdapter.Selection][1]} ftdi tdo_sample_edge {['rising', 'falling'][self.rSamplingEdge.Selection]};"

    if self.custom_reset:
        INIT_CMD = f"{cInit} telnet_port 0; gdb_port 0; tcl_port pipe; reset_config {const._reset_type[self.cResetMode.Selection][1]}; jtag_ntrst_delay {self.ntrst_reset_delay}; adapter srst delay {self.nsrst_reset_delay}; jtag_ntrst_assert_width {self.ntrst_reset_pulse}; adapter srst pulse_width {self.nsrst_reset_pulse}; "

    else:
        INIT_CMD = f"{cInit} telnet_port 0; gdb_port 0; tcl_port pipe; reset_config {const._reset_type[self.cResetMode.Selection][1]}; "

    if int(self.nSpeed.Value) <= 0:
        INIT_CMD += f"jtag_rclk 1000; "
    else:
        INIT_CMD += f"adapter speed {self.nSpeed.Value}; "

    if scanMode:
        INIT_CMD += "init; sleep 2000; shutdown"
        return INIT_CMD

    t = -1
    isBig = False

    targets = []
    endianTargets = []

    if self.cTarget.Selection >= 1:
        t = self.cTarget.Selection

        if t >= self._beTarget:
            isBig = True
            t -= self._beTarget

        else:
            t -= 1

        targets.append(t)
        endianTargets.append(isBig)

    elif "platform" in const._platforms[self.cChipset.Selection]:
        if isinstance(const._platforms[self.cChipset.Selection]["platform"], str):
            isBig = const._platforms[self.cChipset.Selection]["platform"].endswith(
                "-be")
            t = const._targets.index(
                const._platforms[self.cChipset.Selection]["platform"].rstrip("-be"))

            targets.append(t)
            endianTargets.append(isBig)

        else:
            for p in const._platforms[self.cChipset.Selection]["platform"]:
                isBig = p.endswith("-be")
                t = const._targets.index(p.rstrip("-be"))

                targets.append(t)
                endianTargets.append(isBig)

    if len(targets) <= 0:
        raise Exception("You must manually specify the target")

    for k, t in enumerate(targets):
        fixedIR = 0
        for v in const._force_ir:
            if const._targets[t] in const._force_ir[v]:
                fixedIR = v

        additionalCFG = ""
        if not self.disable_platform_options:
            for v in const._additional_config:
                if const._targets[t] in const._additional_config[v]:
                    additionalCFG = v + "; "
                    break

        if const._targets[t] in const._dap_required:
            INIT_CMD += (
                const._init_dap.replace(
                    "(IR)", str(fixedIR) if fixedIR != 0 else str(self.nIR.Value)
                )
                .replace("(XPARAM)", "")
                .replace("(TYPE)", const._targets[t])
                .replace("(ENDIAN)", "big" if endianTargets[k] else "little")
                .replace("(TARGETID)", str(k))
            )

        else:
            INIT_CMD += (
                const._init_normal.replace(
                    "(IR)", str(fixedIR) if fixedIR != 0 else str(self.nIR.Value)
                )
                .replace("(XPARAM)", "")
                .replace("(TYPE)", const._targets[t])
                .replace("(ENDIAN)", "big" if endianTargets[k] else "little")
                .replace("(TARGETID)", str(k))
            )

    self._cfi_start_offset = 0

    if self._loaded_dcc is not None:
        path_escaped = pathlib.Path(self._loaded_dcc).as_posix()
        INIT_CMD += (
            "flash bank target.dcc ocl 0 0 0 0 target0.cpu; set _DCC_PATH {"
            + path_escaped
            + "}; "
            + f"set _DCC_START_OFFSET {hex(intelhex.IntelHex(self._loaded_dcc).minaddr())}; "
        )
        INIT_CMD += 'proc test_flash {} { flash probe 0; for {set i 0} {$i < 0x04000000} {incr i 0x10000} { set v [flash read_bank_memory 0 $i 0x10000 0x200]; echo "Flash read on: 0x[format %X $i]"; }; echo "read is all done"; }; '

    elif const._platforms[self.cChipset.Selection]["mode"] == -1:
        INIT_CMD += "flash bank target.dcc dummy_flash 0 0 0 0 target0.cpu; "
        INIT_CMD += 'proc test_flash {} { flash probe 0; for {set i 0} {$i < 0x04000000} {incr i 0x10000} { set v [flash read_bank_memory 0 $i 0x10000 0x200]; echo "Flash read on: 0x[format %X $i]"; }; echo "read is all done"; }; '

    elif const._platforms[self.cChipset.Selection]["mode"] == 1:
        INIT_CMD += "nand device 0 msm6250 target0.cpu; "

    elif const._platforms[self.cChipset.Selection]["mode"] == 2:
        INIT_CMD += "nand device 0 msm6800 target0.cpu; "

    elif const._platforms[self.cChipset.Selection]["mode"] == 3:
        INIT_CMD += "nand device 0 msm7200 target0.cpu; "

    elif const._platforms[self.cChipset.Selection]["mode"] == 5:
        INIT_CMD += f"nand device 0 generic target0.cpu {hex(const._platforms[self.cChipset.Selection]['flash_addr'])} {hex(const._platforms[self.cChipset.Selection]['flash_cmd'])} {hex(const._platforms[self.cChipset.Selection]['flash_buffer'])}; "

    elif const._platforms[self.cChipset.Selection]["mode"] == 9:
        INIT_CMD += f"nand device 0 generic target0.cpu {hex(const._platforms[self.cChipset.Selection]['flash_latch'])} {hex(const._platforms[self.cChipset.Selection]['flash_latch'])} {hex(const._platforms[self.cChipset.Selection]['flash_buffer'])}; nand_generic is_gpio 0 enable; "

    elif const._platforms[self.cChipset.Selection]["mode"] == 12:
        INIT_CMD += f"nand device 0 {const._platforms[self.cChipset.Selection]['controller']} target0.cpu; {(const._platforms[self.cChipset.Selection]['controller_args'] + '; ') if 'controller_args' in const._platforms[self.cChipset.Selection] else ''}"

    elif const._platforms[self.cChipset.Selection]["mode"] == 4:
        INIT_CMD += f"flash bank target.nor cfi 0x{self.tStart.Value} {hex(int(self.tEnd.Value, 16) - int(self.tStart.Value, 16))} {const._platforms[self.cChipset.Selection]['chip_width']} {const._platforms[self.cChipset.Selection]['bus_width']} target0.cpu; flash bank target.dcc ocl 0 0 0 0 target0.cpu; "
        INIT_CMD += 'proc test_flash {} { flash probe 0; for {set i 0} {$i < 0x04000000} {incr i 0x10000} { set v [flash read_bank_memory 0 $i 0x10000 0x200]; echo "Flash read on: 0x[format %X $i]"; }; echo "read is all done"; }; '
        self._cfi_start_offset = int(self.tStart.Value, 16)

    INIT_CMD += additionalCFG

    INIT_CMD += "target0.cpu configure -event examine-end { halt; sleep 2000; "
    if not self.bSkipInit.Value:
        for i in const._platforms[self.cChipset.Selection]["init"]:
            if i["type"] == 1:
                INIT_CMD += f"mwb 0x{i['address']} {i['value']}; "

            elif i["type"] == 2:
                INIT_CMD += f"mwh 0x{i['address']} {i['value']}; "

            elif i["type"] == 4:
                INIT_CMD += f"mww 0x{i['address']} {i['value']}; "

            elif i["type"] == 8:
                INIT_CMD += f"mwd 0x{i['address']} {i['value']}; "

    INIT_CMD += "}; "
    for i in range(len(targets) - 1):
        INIT_CMD += f"target{i + 1}.cpu configure -event examine-end " + \
            "{ halt; sleep 2000; }; "

    return INIT_CMD


if __name__ == "__main__":
    requests.packages.urllib3.util.connection.HAS_IPV6 = (
        os.environ.get("DUMPIT_IPV4_ONLY", "0") == "1"
    )

    # if len(sys.argv) <= 1:
    try:
        app = wx.App(True)

    except SystemExit as e:
        if isinstance(e.code, str):
            print("wxWidgets has failed to initialize:")

        raise

    m = MainApp(None)
    m.Show()
    app.MainLoop()

    # else:
    #     if sys.argv[1] == "quickdump":
    #         if len(sys.argv) <= 2:
    #             print(f"{sys.argv[0]} quickdump [target_id] [start] [size] [output]")
    #             print("supported targets:\n")
    #             for i, c in enumerate(const._platforms):
    #                 if c["mode"] in [1, 2, 4, 3, 5, 9] and "platform" in c:
    #                     print(f"  {i}: {c['name']}")

    #         else:
    #             tid, start, size, output = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]

    #             if tid >= 0 and tid < len(const._platforms):
    #                 curPlat = const._platforms[tid]
    #                 if curPlat["mode"] in [1, 2, 4, 3, 5, 9] and "platform" in curPlat:
    #                     sys.exit(0)

    #             print(f"Target {tid} is not on the platform list/unsupported for quickdump")
    #             sys.exit(1)

    #     else:
    #         print(f"Unknown type {sys.argv[1]}. Run Dumpit without any arguments to use a GUI, or quickdump [target_id] [start] [size] [output] to perform dump via OpenOCD NAND API")
    #         sys.exit(1)
