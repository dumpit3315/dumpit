import wx
import wx.richtext
from res import main
from res import forwardDialog
from res import ft232r_pinconfig
from res import ft232h_pinconfig
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

os.environ["WXSUPPRESS_SIZER_FLAGS_CHECK"] = "1"
_PTRACKING = queue.Queue()
_PTRACKCOUNT = {}

# Unix, Windows and old Macintosh end-of-line
newlines = [b'\n', b'\r\n', b'\r']


def _unbuffered(proc, stream='stdout'):
    stream = getattr(proc, stream)
    with contextlib.closing(stream):
        while True:
            out = []
            last = stream.read(1)
            # Don't loop forever
            if last == b'' and proc.poll() is not None:
                break
            while last not in newlines:
                # Don't loop forever
                if last == b'' and proc.poll() is not None:
                    break
                out.append(last)
                last = stream.read(1)
            out = b''.join(out)
            yield out


def getOCDExec():
    return os.path.join(os.path.dirname(__file__), f"ocd/{sys.platform}/bin/openocd")


def _msleep(dur: int):
    s = time.perf_counter_ns()
    while time.perf_counter_ns() < (s+(dur*1000)):
        pass


def doTrackThread(user_id, action, openocd_version, config, **kwargs):
    try:        
        res = requests.post("https://dumpit.ucomsite.my.id/analytics/track", json={
            "user_id": user_id,
            "action": action,
            "dumpit_version": const.DUMPIT_VERSION,
            "python_version": sys.version,
            "openocd_version": openocd_version,
            "os": f"{platform.system()} {platform.version()}",
            "config": config,
            **kwargs
        }, timeout=5)
        
        assert res.status_code >= 200 and res.status_code <= 299, f"{res.status_code} {res.reason}"
        _PTRACKING.put(action)

    except Exception:
        if True:
            print("unable to track:")
            traceback.print_exc()

'''
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
                self._wsThreadQueue.put(self._ws_parent._sio.receive(0))

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

                self.Sizer.Layout()

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
                    self._ws_parent._sio.emit("bye")
                    self._ws_parent._sio.disconnect()

    def doStop(self, event):
        self._ws_parent._sio.emit("bye")
        self._ws_parent._sio.disconnect()
'''

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
                self._wsThreadQueue.put(self._ws_parent._sio.receive(0))

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
                return self.EndModal(0)

            q = self._wsThreadQueue.get_nowait()

            if q[0] == "forward_client_connected":
                self.Unbind(wx.EVT_IDLE)
                self._loop_running = False
                return self.EndModal(1)
            
            elif q[1] == "bye":
                #print("bye event")
                self._ws_parent._sio.disconnect()

        except queue.Empty:
            pass        

    def doStop(self, event):        
        self._ws_parent._sio.emit("bye")
        self._ws_parent._sio.disconnect()

class FT232HConfig(ft232h_pinconfig.FT232H_Pin_Config):
    def __init__(self, parent):
        super().__init__(parent)
        for name, img, flip in const._ft232h_boards:
            self.c_Board.Append(name)

        self.base_parent: MainApp = parent
        self.c_Board.Selection = 0

        self.board.Bitmap = wx.Bitmap(
            const._ft232h_boards[self.c_Board.Selection][1], wx.BITMAP_TYPE_ANY)
        self.isFlip = const._ft232h_boards[self.c_Board.Selection][2]

        self.Sizer.Layout()
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
                    [u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low"])
                getattr(self, f"cfg_p2{i}").Selection = 0
                getattr(self, f"cfg_p2{i}").Enable(True)

            for i in range(8):
                self.pins_layout.append(getattr(self, f"cfg_p1{i}"))
                getattr(self, f"cfg_p1{i}").Clear()
                getattr(self, f"cfg_p1{i}").Append(
                    [u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low"])
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
                    [u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low"])
                getattr(self, f"cfg_p1{i}").Selection = 0
                getattr(self, f"cfg_p1{i}").Enable(True)

            for i in range(8):
                self.pins_layout.append(getattr(self, f"cfg_p2{i}"))
                getattr(self, f"cfg_p2{i}").Clear()
                getattr(self, f"cfg_p2{i}").Append(
                    [u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low"])
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
            const._ft232h_boards[self.c_Board.Selection][1], wx.BITMAP_TYPE_ANY)
        self.isFlip = const._ft232h_boards[self.c_Board.Selection][2]

        self.Sizer.Layout()
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

        if not hasTDI or not hasTDO or not hasTCK or not hasTMS or not hasTRST or not hasSRST:
            return

        self.base_parent._ft232h_pins = 0xffff
        self.base_parent._ft232h_dirs = 0xffff

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
            const._ft232r_boards[self.c_Board.Selection][1], wx.BITMAP_TYPE_ANY)
        self.Sizer.Layout()

        self.cfg_tdi.Selection = self.base_parent._ft232r_tdi
        self.cfg_tdo.Selection = self.base_parent._ft232r_tdo
        self.cfg_tck.Selection = self.base_parent._ft232r_tck
        self.cfg_tms.Selection = self.base_parent._ft232r_tms
        self.cfg_trst.Selection = self.base_parent._ft232r_trst
        self.cfg_srst.Selection = self.base_parent._ft232r_srst

        self.pin_layout = [self.cfg_tdi, self.cfg_tdo,
                           self.cfg_tck, self.cfg_tms, self.cfg_trst, self.cfg_srst]

    def doChangeBoard(self, event):
        self.board.Bitmap = wx.Bitmap(
            const._ft232r_boards[self.c_Board.Selection][1], wx.BITMAP_TYPE_ANY)
        self.Sizer.Layout()

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


class MainApp(main.main):
    def __init__(self, parent):
        global _PTRACKCOUNT

        super().__init__(parent)
        
        print("Dumpit started")
        self.status.Value = ""
        self.finderStatus.Value = ""
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

        self._resetDelays = []

        for e in const._reset_delays:
            for c in const._reset_delays:
                for d in const._reset_delays:
                    self._resetDelays.append((d, c, e))

        for rt, rs, sr in self._resetDelays:
            self.cResetDelay.Append(
                f"{rt}ms TRST / {rs}ms SRST / {sr}ms RST delay")

        self.cResetDelay.Selection = 0

        for p in const._platforms:
            self.cChipset.Append(p["name"])

        self.cChipset.Selection = 0
        self.progress.Value = 0

        self._ocd_version = subprocess.check_output([getOCDExec(
        ), "--version"], encoding="utf-8", stderr=subprocess.STDOUT).splitlines()[0].rstrip()

        self.status.Value += f"Dumpit v{const.DUMPIT_VERSION}\nOpenOCD: {self._ocd_version}"

        for name, parm in const._ft232h_adapters:
            self.cFTAdapter.Append(name)

        self.cFTAdapter.Selection = 0

        ''' Start dumpit stuff '''
        self._isConnect = False
        self._isConnectRemote = False
        self._isForward = False

        self._ocd = None
        self._sio = None
        self._logThread = None
        self._logThreadQueue = None

        self._sioThread = None
        self._sioMsgQueue = None

        self._errMsgQueue = None
        self._progMsgQueue = None
        self._btnMsgQueue = None
        self._pong_flag = threading.Event()

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

        self._ft232h_pins = 0xffff & ~(
            1 << self._ft232h_tdi | 1 << self._ft232h_tdo | 1 << self._ft232h_tck)
        self._ft232h_dirs = 0xffff & ~(1 << self._ft232h_tdo)

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

        if os.path.exists(os.path.join(os.path.dirname(__file__), "dumpit_config.json")):
            cfg = json.load(
                open(os.path.join(os.path.dirname(__file__), "dumpit_config.json"), "r"))
            self.cInterface.Selection = cfg["interface"]
            self.nSpeed.Value = cfg["speed"]
            self.cChipset.Selection = cfg["chipset"]
            self.cTarget.Selection = cfg["target"]
            self.cTap.Selection = cfg["tap"]
            self.nIR.Value = cfg["ir"]
            self.cResetMode.Selection = cfg["reset_mode"]
            self.cResetDelay.Selection = cfg["reset_delay"]
            self.bSkipInit.Value = cfg["skip_init"]
            self.tStart.Value = cfg["start"]
            self.tEnd.Value = cfg["end"]
            self.cNandSize.Selection = cfg["nand_size"]
            self.bECCDisable.Value = cfg["ecc_disabled"]
            self.bBadBlockinData.Value = cfg["bad_blocks_in_data"]
            self.bTargetRemote.Value = cfg["target_remote"]
            self.bUseGDB.Value = cfg["use_gdb"]

            self.tUSBID.Value = cfg["ft232r_usb_id"]
            self.tRestoreSerial.Value = cfg["ft232r_restore_serial"]
            self._ft232r_tdi = cfg["ft232r_tdi"]
            self._ft232r_tdo = cfg["ft232r_tdo"]
            self._ft232r_tck = cfg["ft232r_tms"]
            self._ft232r_tms = cfg["ft232r_tck"]
            self._ft232r_trst = cfg["ft232r_trst"]
            self._ft232r_srst = cfg["ft232r_srst"]

            self.cFTAdapter.Selection = cfg["ft232h_adapter"]
            self.tUSBID1.Value = cfg["ft232h_usb_id"]
            self.cChannel.Selection = cfg["ft232h_channel"]
            self.rSamplingEdge.Selection = cfg["ft232h_sampling_edge"]
            self._ft232h_tdi = cfg["ft232h_tdi"]
            self._ft232h_tdo = cfg["ft232h_tdo"]
            self._ft232h_tck = cfg["ft232h_tck"]
            self._ft232h_tms = cfg["ft232h_tms"]
            self._ft232h_trst = cfg["ft232h_trst"]
            self._ft232h_srst = cfg["ft232h_srst"]

            self._ft232h_pins = (cfg["ft232h_pins"] & ~(1 << self._ft232h_tdi | 1 << self._ft232h_tdo | 1 <<
                                 self._ft232h_tck)) | 1 << self._ft232h_tms | 1 << self._ft232h_trst | 1 << self._ft232h_srst
            self._ft232h_dirs = 0xffff & ~(1 << self._ft232h_tdo)

            self.nGPIODChip.Value = cfg["gpio_chip"]
            self._gpio_tdi = cfg["gpio_tdi"]
            self._gpio_tdo = cfg["gpio_tdo"]
            self._gpio_tck = cfg["gpio_tck"]
            self._gpio_tms = cfg["gpio_tms"]
            self._gpio_trst = cfg["gpio_trst"]
            self._gpio_srst = cfg["gpio_srst"]

            self.cParCable.Selection = cfg["parport_cable"]
            self.tParPort.Value = cfg["parport_port"]

            self.tRBBHost.Value = cfg["remote_bitbang_host"]
            self.tRBBPort.Value = cfg["remote_bitbang_port"]

            self.bUseMPSSE.Value = cfg["finder_use_mpsse"]

            self.bEnableAnalytics.Value = cfg["enable_analytics"]
            self.tUserID.Value = cfg["user_id"]

            _PTRACKCOUNT = cfg["tracking_count"]
            self._debug_logs = cfg["debug_log"]

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
            cfg["reset_delay"] = self.cResetDelay.GetString(
                self.cResetDelay.Selection)
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
                self.rSamplingEdge.Selection)
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

            pAnalyticsThread = threading.Thread(target=doTrackThread, args=(
                self.tUserID.Value, action, self._ocd_version, cfg), kwargs=kwargs)
            pAnalyticsThread.daemon = True

            pAnalyticsThread.start()

    def _doLogging(self):
        for l in _unbuffered(self._ocd, "stderr"):
            try:
                if not self._logSupressed:
                    self._logThreadQueue.put(l.decode("utf-8"))
                    if self._isForward: self._sio.emit("log", l.decode("utf-8"))

            except Exception:
                pass

    def _doWSLoop(self):
        while self._sio.connected:
            try:
                p = self._sio.receive(0)

                if p[0] == "data":
                    self._sioMsgQueue.put(p[1])

                elif p[0] == "log" and not self._logSupressed:
                    self._logThreadQueue.put(p[1])
                    
                elif p[0] == "bye":
                    #print("bye event")
                    self._sio.disconnect()
                
                elif p[0] == "ping_remote":
                    self._sio.emit("pong_remote")
                    
                elif p[0] == "pong_remote":
                    self._pong_flag.set()

            except socketio.exceptions.TimeoutError:
                pass

            except Exception:
                pass
            
    def _doWSLoop_Forward(self):
        while self._ocd and self._ocd.poll() is None:
            try:
                p = self._sio.receive(0)

                if p[0] == "data":
                    self._sio.emit("data", self._ocdSendCommand(p[1]))
                    
                elif p[0] == "command":
                    pass
                
                elif p[0] == "bye":
                    #print("bye event")
                    self._sio.disconnect()
                    
                elif p[0] == "ping_remote":
                    self._sio.emit("pong_remote")
                    
                elif p[0] == "pong_remote":
                    self._pong_flag.set()

            except socketio.exceptions.TimeoutError:
                pass

            except Exception:
                pass

    def doLoop(self, event):
        global _PTRACKCOUNT

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
                    self.progress.Range, int(p * self.progress.Range))

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

        if self._isForward and self._ocd and self._isConnect and self._ocd.poll() is not None:
            self._sio.emit("bye")
            self._sio.disconnect()
            self._isConnect = False
            self._isForward = False

        if self._ocd and self._isConnect and self._ocd.poll() is not None and not self._isForward:
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
            
            if self._isForward and self._ocd and self._isConnect and self._ocd.poll() is None:
                self._ocd.terminate()
                self._isConnect = False
                self._isForward = False
                        

    def _ocdSendCommand(self, cmd: str, _return: bool=True):
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

            if _return: 
                return resTemp.decode("latin-1")
            
            else:
                print(f"SINK: {resTemp}")
                return ""

        elif self._sio and self._sio.connected:
            self._sio.emit("data", cmd)
            if _return: 
                return self._sioMsgQueue.get(timeout=10)
            
            else:
                print(f"SINK: {self._sioMsgQueue.get(timeout=10)}")
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
                    self._sio.emit("bye")
                    self._sio.disconnect()
            
            self._doAnalytics("disconnect", reason=0)        

        elif self._isConnectRemote:
            self._isConnectRemote = False
            
            if self._sio and self._sio.connected:
                self._sio.emit("bye")
                self._sio.disconnect()

            self.bConnect.Label = "Connect"
            self.bConnectRemote.Enable(True)
            self.bForwardRemote.Enable(True)
            self._doAnalytics("disconnect", reason=0)

        else:
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
            self._ocd = subprocess.Popen([getOCDExec(
            ), "-c", INIT_CMD], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

            self._doAnalytics("idcode", idcode=self.cmd_get_idcode())

    def doConnectRemote(self, event):
        try:
            if self._sio:
                self._sio.disconnect()

            self._sio = socketio.SimpleClient()
            gc.collect()

            self._doAnalytics("connect", type=2)

            self._sio.connect(f"http://{self.bTargetRemote.Value}/" if self.bTargetRemote.Value.startswith("localhost") or self.bTargetRemote.Value.startswith("127.0.0.1") or self.bTargetRemote.Value.startswith(
                "::1") or self.bTargetRemote.Value.startswith("[::1]") else f"https://{self.bTargetRemote.Value}/", transports=["websocket"], socketio_path="dumpit_remote")

            p = self._sio.receive(5)
            if p[0] != "protocol" or p[1] != "dumpit":
                raise Exception("Not a valid Dumpit remote protocol.")

            rep = wx.TextEntryDialog(self, "Enter interface token")
            if rep.ShowModal() == wx.ID_CANCEL:
                self._sio.emit("bye")
                self._sio.disconnect()

                return

            res = self._sio.call("forward_connect", rep.GetValue(), timeout=5)
            if res["error"]:
                raise Exception(res["error"])
                        
            self._logThreadQueue = queue.Queue()
            self._sioMsgQueue = queue.Queue()

            self._errMsgQueue = queue.Queue()
            self._progMsgQueue = queue.Queue()
            self._btnMsgQueue = queue.Queue()

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
                self._sio.emit("bye")
                self._sio.disconnect()

            self._doAnalytics("error", error=str(
                e), traceback=traceback.format_exc())
            wx.MessageBox(str(e), "Dumpit", wx.OK |
                          wx.CENTER | wx.ICON_ERROR, self)

    def doForwardRemote(self, event):
        try:
            if self._sio:
                self._sio.disconnect()
            
            self._sio = socketio.SimpleClient()
            gc.collect()

            self._sio.connect(f"http://{self.bTargetRemote.Value}/" if self.bTargetRemote.Value.startswith("localhost") or self.bTargetRemote.Value.startswith("127.0.0.1") or self.bTargetRemote.Value.startswith(
                "::1") or self.bTargetRemote.Value.startswith("[::1]") else f"https://{self.bTargetRemote.Value}/", transports=["websocket"], socketio_path="dumpit_remote")

            p = self._sio.receive(5)
            if p[0] != "protocol" or p[1] != "dumpit":
                raise Exception("Not a valid Dumpit remote protocol.")            

            token = self._sio.call("forward_request", timeout=5)
            forward_wait = ForwardApp(self, token["token"]).ShowModal()
            if forward_wait:
                if self._ocd and self._ocd.poll() is None:
                    self._ocd.kill()
                    
                gc.collect()

                INIT_CMD = getInitCmd(self)

                self._doAnalytics("connect", type=1)

                # print(INIT_CMD)

                self._isConnect = True
                self._isForward = True
                self._isConnectRemote = True
                
                self.status.Value = f'Command-line arguments: openocd -c "{INIT_CMD}"\n\n'
                self._sio.emit("log", f'Command-line arguments: openocd -c "{INIT_CMD}"\n\n')
                
                self._ocd = subprocess.Popen([getOCDExec(
                ), "-c", INIT_CMD], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                self._ocdSendCommand("")

                self._logThreadQueue = queue.Queue()
                self._sioMsgQueue = queue.Queue()

                self._errMsgQueue = queue.Queue()
                self._progMsgQueue = queue.Queue()
                self._btnMsgQueue = queue.Queue()

                self._logThread = threading.Thread(target=self._doLogging)
                self._logThread.daemon = True

                self._sioThread = threading.Thread(target=self._doWSLoop_Forward)
                
                self._logThread.start()
                self._sioThread.start()

                self.bConnect.Label = "Disconnect"
                self.bConnectRemote.Enable(False)
                self.bForwardRemote.Enable(False)

                self._doAnalytics("idcode", idcode=self.cmd_get_idcode())

        except Exception as e:
            if self._sio and self._sio.connected:
                self._sio.emit("bye")
                self._sio.disconnect()

            self._doAnalytics("error", error=str(
                e), traceback=traceback.format_exc())
            wx.MessageBox(str(e), "Dumpit", wx.OK |
                          wx.CENTER | wx.ICON_ERROR, self)

    def doHexCheck(self, event: wx.CommandEvent):
        event.EventObject.ChangeValue(
            re.sub("([^0-9a-fA-F]+)", "", event.EventObject.GetValue()))

    def cmd_get_idcode(self):
        if not self._isConnect and not self._isConnectRemote:
            return b""
        try:
            return int(self._ocdSendCommand("jtag cget target.cpu -idcode"))

        except Exception:
            return 0

    def cmd_read_u8(self, offset: int, size: int = 1):
        if not self._isConnect and not self._isConnectRemote:
            return 0 if size <= 1 else b""
        if self._debug_logs:
            print(f"RDB {hex(offset)} {size}")

        c = self._ocdSendCommand(f"read_memory {hex(offset)} 8 {size}")

        if c.startswith("0x"):
            return int(c, 16) if size <= 1 else bytes([int(x, 16) for x in c.split(" ")])

        else:
            return 0xff if size <= 1 else b"\xff" * size

    def cmd_read_u16(self, offset: int, size: int = 1):
        if not self._isConnect and not self._isConnectRemote:
            return 0 if size <= 1 else []
        if self._debug_logs:
            print(f"RDH {hex(offset)} {size}")

        c = self._ocdSendCommand(f"read_memory {hex(offset)} 16 {size}")

        if c.startswith("0x"):
            return int(c, 16) if size <= 1 else [int(x, 16) for x in c.split(" ")]

        else:
            return 0xffff if size <= 1 else b"\xff\xff" * size

    def cmd_read_u32(self, offset: int, size: int = 1):
        if not self._isConnect and not self._isConnectRemote:
            return 0 if size <= 1 else []
        if self._debug_logs:
            print(f"RDW {hex(offset)} {size}")

        c = self._ocdSendCommand(f"read_memory {hex(offset)} 32 {size}")

        if c.startswith("0x"):
            return int(c, 16) if size <= 1 else [int(x, 16) for x in c.split(" ")]

        else:
            return 0xffffffff if size <= 1 else b"\xff\xff\xff\xff" * size

    def cmd_read_flash(self, offset: int, size: int = 1):
        if not self._isConnect and not self._isConnectRemote:
            return 0 if size <= 1 else b""
        if self._debug_logs:
            print(f"RDF {hex(offset)} {size}")

        c = self._ocdSendCommand(
            f"flash read_bank_memory 0 {hex(offset)} {size}")

        if c.startswith("0x"):
            return bytes([int(x, 16) for x in c.split(" ")])

        else:
            return b"\xff" * size

    def cmd_read_cp15(self, cr_n, op_1, cr_m, op_2):
        if not self._isConnect and not self._isConnectRemote:
            return 0
        try:
            return int(self._ocdSendCommand(f"arm mrc 15 {op_1} {cr_n} {cr_m} {op_2}"), 16)

        except Exception:
            return 0

    def cmd_write_cp15(self, cr_n, op_1, cr_m, op_2, value):
        if not self._isConnect and not self._isConnectRemote:
            return 0
        self._ocdSendCommand(
            f"arm mcr 15 {hex(op_1)} {hex(cr_n)} {hex(cr_m)} {hex(op_2)} {hex(value)}")

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
        self._doAnalytics("dump_start", addr_start=cOffset,
                          addr_end=eOffset, is_memory=True)

        self._logSupressed = True
        self._logThreadQueue.put(f"Dump memory started {datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            with open(name, "wb") as tempFile:
                while cOffset < eOffset and not self._isReadCanceled:
                    tempFile.write(self.cmd_read_u8(
                        cOffset, min(0x200, eOffset - cOffset)))
                    cOffset += min(0x200, eOffset - cOffset)

                    self._progMsgQueue.put(cOffset/eOffset)

            self._logThreadQueue.put(f"Dump memory finished {datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}")

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
            self._logSupressed = False

            self._doAnalytics("dump_end", addr_start=cOffset,
                              addr_end=eOffset, is_memory=True)

    def doReadMemory(self, event):
        if (not self._isConnect and not self._isConnectRemote) or self._isRead:
            return

        cOffset = int(self.tStart.Value, 16)
        eOffset = int(self.tEnd.Value, 16)

        if cOffset >= eOffset:
            return wx.MessageBox(f"start offset must be less than end offset", "Dumpit", wx.OK | wx.CENTER | wx.ICON_ERROR, self)

        with wx.FileDialog(self, "Dump memory", wildcard="Binary file|*.bin", style=wx.FD_SAVE) as fd:
            fd: wx.FileDialog
            if fd.ShowModal() != wx.ID_CANCEL:
                self.progress.Value = 0

                self._dumpThread = threading.Thread(
                    target=self.doReadMemoryThread, args=(fd.GetPath(), cOffset, eOffset))
                self._dumpThread.daemon = True

                self._dumpThread.start()

    def doReadFlashThread(self, name, cOffset, eOffset, baseO1N=-1):
        spareBuf = bytearray()
        bbBuf = bytearray()

        self._isRead = True
        self._isReadCanceled = False

        O1N_isDDP = False
        O1N_Density = 0

        QSC_NAND_CFG1 = 0

        self._btnMsgQueue.put(True)
        self._doAnalytics("dump_start", addr_start=cOffset,
                          addr_end=eOffset, is_memory=False)

        try:
            if self._loaded_dcc is not None:
                self._ocdSendCommand("soft_reset_halt")                
                self._ocdSendCommand(f"load_image $_DCC_PATH", False)
                self._ocdSendCommand(
                    f"resume $_DCC_START_OFFSET")

                if not self._ocdSendCommand("flash probe 0").startswith("flash 'ocl' found at"):
                    raise Exception("Flash probe failed!")
                self._ocdSendCommand("flash info 0")

            elif const._platforms[self.cChipset.Selection]["mode"] in [1, 2]:
                self.cmd_write_u32(
                    int(const._platforms[self.cChipset.Selection]["flash_cmd"], 16), 7)
                _msleep(const._jtag_init_delay)

                if self.bECCDisable.Value:
                    self.cmd_write_u32(int(const._platforms[self.cChipset.Selection]["flash_cfg"], 16), self.cmd_read_u32(
                        int(const._platforms[self.cChipset.Selection]["flash_cfg"], 16)) | 1)

                else:
                    self.cmd_write_u32(int(const._platforms[self.cChipset.Selection]["flash_cfg"], 16), self.cmd_read_u32(
                        int(const._platforms[self.cChipset.Selection]["flash_cfg"], 16)) & 0xfffffffe)

            elif const._platforms[self.cChipset.Selection]["mode"] == 3:
                self.cmd_write_u32(
                    int(const._platforms[self.cChipset.Selection]["flash_cmd"], 16), 0x31)
                self.cmd_write_u32(
                    int(const._platforms[self.cChipset.Selection]["flash_exec_cmd"], 16), 1)
                _msleep(const._jtag_init_delay)

                self.cmd_write_u32(
                    int(const._platforms[self.cChipset.Selection]["flash_cmd"], 16), 0xD)
                self.cmd_write_u32(
                    int(const._platforms[self.cChipset.Selection]["flash_exec_cmd"], 16), 1)
                _msleep(const._jtag_init_delay)

                if self.bECCDisable.Value:
                    self.cmd_write_u32(int(const._platforms[self.cChipset.Selection]["flash_cfg1"], 16), self.cmd_read_u32(
                        int(const._platforms[self.cChipset.Selection]["flash_cfg1"], 16)) | 1)

                else:
                    self.cmd_write_u32(int(const._platforms[self.cChipset.Selection]["flash_cfg1"], 16), self.cmd_read_u32(
                        int(const._platforms[self.cChipset.Selection]["flash_cfg1"], 16)) & 0xfffffffe)

                _msleep(const._jtag_init_delay)
                QSC_NAND_CFG1 = self.cmd_read_u32(
                    int(const._platforms[self.cChipset.Selection]["flash_cfg1"], 16))

            elif const._platforms[self.cChipset.Selection]["mode"] == 4:
                assert cOffset >= self._cfi_start_offset, f"Read address must be greater or equal than {hex(self._cfi_start_offset)}"

                if not self._ocdSendCommand("flash probe 0").startswith("flash 'cfi' found at"):
                    raise Exception("Flash probe failed!")
                self._ocdSendCommand("flash info 0")

            elif const._platforms[self.cChipset.Selection]["mode"] == -1:
                assert cOffset >= self._cfi_start_offset, f"Read address must be greater or equal than {hex(self._cfi_start_offset)}"

                self._ocdSendCommand("flash probe 0")
                self._ocdSendCommand("flash info 0")

            elif const._platforms[self.cChipset.Selection]["mode"] == 5:
                if const._platforms[self.cChipset.Selection]["reg_width"] in [0, 1]:
                    self.cmd_write_u8(
                        const._platforms[self.cChipset.Selection]["flash_cmd"], 0xff)

                elif const._platforms[self.cChipset.Selection]["reg_width"] == 2:
                    self.cmd_write_u16(
                        const._platforms[self.cChipset.Selection]["flash_cmd"], 0xff)

                elif const._platforms[self.cChipset.Selection]["reg_width"] == 4:
                    self.cmd_write_u32(
                        const._platforms[self.cChipset.Selection]["flash_cmd"], 0xff)

                _msleep(const._jtag_init_delay)

            elif const._platforms[self.cChipset.Selection]["mode"] == 7:
                O1N_BASE = int(const._platforms[self.cChipset.Selection]["o1n_offset"],
                               16) if "o1n_offset" in const._platforms[self.cChipset.Selection] else baseO1N
                print("start dumping O1N from", hex(O1N_BASE))

                O1N_DevID = self.cmd_read_u16(O1N_BASE + 0x1E002)

                O1N_isDDP = bool(O1N_DevID & 8)
                O1N_Density = 2 << (
                    (5 if O1N_isDDP else 6) + ((O1N_DevID >> 4) & 0xf))

            time.sleep(1)
            self._logSupressed = True            
            self._logThreadQueue.put(f"Dump flash started {datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}")

            with open(name, "wb") as tempFile:
                while cOffset < eOffset and not self._isReadCanceled:
                    if self._loaded_dcc is not None or const._platforms[self.cChipset.Selection]["mode"] in [-1, 4]:
                        tempFile.write(self.cmd_read_flash(
                             cOffset - self._cfi_start_offset, 0x200))
                        cOffset += 0x200

                    elif const._platforms[self.cChipset.Selection]["mode"] == 1:
                        self.cmd_write_u32(
                            int(const._platforms[self.cChipset.Selection]["flash_addr"], 16), cOffset)

                        for _ in range(4 if self.cNandSize.Selection == 1 else 1):
                            self.cmd_write_u32(
                                int(const._platforms[self.cChipset.Selection]["flash_cmd"], 16), 1)

                            for _ in range(0x2500):
                                _msleep(const._jtag_sleep_delay)
                                if self.cmd_read_u32(int(const._platforms[self.cChipset.Selection]["flash_wait_status"], 16)) & 8192:
                                    break

                            tempFile.write(self.cmd_read_u8(
                                int(const._platforms[self.cChipset.Selection]["flash_buffer"], 16), 0x200))

                            spareBuf += self.cmd_read_u8(
                                int(const._platforms[self.cChipset.Selection]["flash_buffer"], 16) + 0x200, 0x10)

                            cOffset += 0x200
                            if cOffset >= eOffset:
                                break

                    elif const._platforms[self.cChipset.Selection]["mode"] == 2:
                        self.cmd_write_u32(
                            int(const._platforms[self.cChipset.Selection]["flash_addr"], 16), cOffset)

                        for _ in range(4 if self.cNandSize.Selection == 1 else 1):
                            self.cmd_write_u32(
                                int(const._platforms[self.cChipset.Selection]["flash_cmd"], 16), 1)

                            for _ in range(0x2500):
                                _msleep(const._jtag_sleep_delay)
                                if self.cmd_read_u32(int(const._platforms[self.cChipset.Selection]["flash_wait_status"], 16)) & 2:
                                    break

                            tempFile.write(self.cmd_read_u8(
                                int(const._platforms[self.cChipset.Selection]["flash_buffer"], 16), 0x200))

                            spareBuf += self.cmd_read_u8(
                                int(const._platforms[self.cChipset.Selection]["flash_buffer"], 16) + 0x200, 0x10)

                            cOffset += 0x200
                            if cOffset >= eOffset:
                                break

                    elif const._platforms[self.cChipset.Selection]["mode"] == 3:
                        self.cmd_write_u32(
                            int(const._platforms[self.cChipset.Selection]["flash_cmd"], 16), 0x34)

                        flash_write = ((cOffset >> 11) << 16) | (((cOffset >> 1) & 0x3ff) if QSC_NAND_CFG1 & 2 else (
                            cOffset & 0x7ff)) if self.cNandSize.Selection == 1 else ((cOffset >> 9) << 8) | ((cOffset >> 1) & 0xff)

                        self.cmd_write_u32(int(
                            const._platforms[self.cChipset.Selection]["flash_addr0"], 16), flash_write & 0xffffffff)
                        self.cmd_write_u32(int(
                            const._platforms[self.cChipset.Selection]["flash_addr1"], 16), (flash_write >> 32) & 0xffffffff)

                        for _ in range(4 if self.cNandSize.Selection == 1 else 1):
                            self.cmd_write_u32(
                                int(const._platforms[self.cChipset.Selection]["flash_exec_cmd"], 16), 1)

                            for _ in range(0x2500):
                                _msleep(const._jtag_sleep_delay)
                                if (self.cmd_read_u32(int(const._platforms[self.cChipset.Selection]["flash_status"], 16)) & 0xf) == 0:
                                    break

                            tempChunk = self.cmd_read_u8(
                                int(const._platforms[self.cChipset.Selection]["flash_buffer"], 16), 0x210)

                            if self.bBadBlockinData:
                                tempFile.write(
                                    tempChunk[:0x1d0] + tempChunk[0x1d2:0x202])
                                spareBuf += tempChunk[0x202:] + b"\xff\xff"
                                bbBuf += tempChunk[0x1d0:0x1d2]

                            else:
                                tempFile.write(tempChunk[:0x200])
                                spareBuf += tempChunk[0x200:]

                            cOffset += 0x200
                            if cOffset >= eOffset:
                                break

                    elif const._platforms[self.cChipset.Selection]["mode"] == 5:
                        if const._platforms[self.cChipset.Selection]["reg_width"] == 0:
                            if self.cNandSize.Selection == 1:
                                self.cmd_write_u8(
                                    const._platforms[self.cChipset.Selection]["flash_cmd"], 0x00)

                                self.cmd_write_u8(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], cOffset & 0xff)
                                self.cmd_write_u8(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], (cOffset >> 8) & 0xf)

                                self.cmd_write_u8(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], (cOffset >> 11) & 0xff)
                                self.cmd_write_u8(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 11) >> 8) & 0xff)
                                self.cmd_write_u8(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 11) >> 16) & 0xff)

                                self.cmd_write_u8(
                                    const._platforms[self.cChipset.Selection]["flash_cmd"], 0x30)

                            else:
                                self.cmd_write_u8(
                                    const._platforms[self.cChipset.Selection]["flash_cmd"], (cOffset >> 8) & 1)

                                self.cmd_write_u8(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], cOffset & 0xff)

                                self.cmd_write_u8(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], (cOffset >> 9) & 0xff)
                                self.cmd_write_u8(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 9) >> 8) & 0xff)
                                self.cmd_write_u8(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 9) >> 16) & 0xff)

                            for _ in range(0x2500):
                                _msleep(const._jtag_sleep_delay)
                                if const._platforms[self.cChipset.Selection]["wait_mask"] is not None:
                                    if self.cmd_read_u32(const._platforms[self.cChipset.Selection]["flash_wait"]) & const._platforms[self.cChipset.Selection]["wait_mask"]:
                                        break

                            temp_buf = []
                            for _ in range(0x800 if self.cNandSize.Selection == 1 else 0x200):
                                temp_buf.append(self.cmd_read_u8(
                                    const._platforms[self.cChipset.Selection]["flash_buffer"]))
                                cOffset += 1

                                if cOffset >= eOffset:
                                    break

                            tempFile.write(bytes(temp_buf))
                            if cOffset >= eOffset:
                                break

                        elif const._platforms[self.cChipset.Selection]["reg_width"] == 1:
                            self.cmd_write_u8(
                                const._platforms[self.cChipset.Selection]["flash_cmd"], 0)

                            self.cmd_write_u8(
                                const._platforms[self.cChipset.Selection]["flash_addr"], (cOffset >> 1) & 0xff)

                            self.cmd_write_u8(
                                const._platforms[self.cChipset.Selection]["flash_addr"], (cOffset >> 9) & 0xff)
                            self.cmd_write_u8(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                cOffset >> 9) >> 8) & 0xff)
                            self.cmd_write_u8(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                cOffset >> 9) >> 16) & 0xff)

                            for _ in range(0x2500):
                                _msleep(const._jtag_sleep_delay)
                                if const._platforms[self.cChipset.Selection]["wait_mask"] is not None:
                                    if self.cmd_read_u32(const._platforms[self.cChipset.Selection]["flash_wait"]) & const._platforms[self.cChipset.Selection]["wait_mask"]:
                                        break

                            temp_buf = []
                            for _ in range(0x400 if self.cNandSize.Selection == 1 else 0x100):
                                temp_buf.append(self.cmd_read_u16(
                                    const._platforms[self.cChipset.Selection]["flash_buffer"]))
                                cOffset += 2

                                if cOffset >= eOffset:
                                    break

                            tempFile.write(b"".join([x.to_bytes(
                                2, "big" if self.cTarget.Selection >= self._beTarget else "little") for x in temp_buf]))
                            if cOffset >= eOffset:
                                break

                        elif const._platforms[self.cChipset.Selection]["reg_width"] == 2:
                            if self.cNandSize.Selection == 1:
                                self.cmd_write_u16(
                                    const._platforms[self.cChipset.Selection]["flash_cmd"], 0x00)

                                self.cmd_write_u16(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], cOffset & 0xff)
                                self.cmd_write_u16(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], (cOffset >> 8) & 0xf)

                                self.cmd_write_u16(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], (cOffset >> 11) & 0xff)
                                self.cmd_write_u16(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 11) >> 8) & 0xff)
                                self.cmd_write_u16(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 11) >> 16) & 0xff)

                                self.cmd_write_u16(
                                    const._platforms[self.cChipset.Selection]["flash_cmd"], 0x30)

                            else:
                                self.cmd_write_u16(
                                    const._platforms[self.cChipset.Selection]["flash_cmd"], (cOffset >> 8) & 1)

                                self.cmd_write_u16(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], cOffset & 0xff)

                                self.cmd_write_u16(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], (cOffset >> 9) & 0xff)
                                self.cmd_write_u16(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 9) >> 8) & 0xff)
                                self.cmd_write_u16(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 9) >> 16) & 0xff)

                            for _ in range(0x2500):
                                _msleep(const._jtag_sleep_delay)
                                if const._platforms[self.cChipset.Selection]["wait_mask"] is not None:
                                    if self.cmd_read_u32(const._platforms[self.cChipset.Selection]["flash_wait"]) & const._platforms[self.cChipset.Selection]["wait_mask"]:
                                        break

                            temp_buf = []
                            for _ in range(0x400 if self.cNandSize.Selection == 1 else 0x100):
                                temp_buf.append(self.cmd_read_u16(
                                    const._platforms[self.cChipset.Selection]["flash_buffer"]))
                                cOffset += 2

                                if cOffset >= eOffset:
                                    break

                            tempFile.write(b"".join([x.to_bytes(
                                2, "big" if self.cTarget.Selection >= self._beTarget else "little") for x in temp_buf]))
                            if cOffset >= eOffset:
                                break

                        elif const._platforms[self.cChipset.Selection]["reg_width"] == 4:
                            if self.cNandSize.Selection == 1:
                                self.cmd_write_u32(
                                    const._platforms[self.cChipset.Selection]["flash_cmd"], 0x00)

                                self.cmd_write_u32(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], cOffset & 0xff)
                                self.cmd_write_u32(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], (cOffset >> 8) & 0xf)

                                self.cmd_write_u32(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], (cOffset >> 11) & 0xff)
                                self.cmd_write_u32(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 11) >> 8) & 0xff)
                                self.cmd_write_u32(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 11) >> 16) & 0xff)

                                self.cmd_write_u32(
                                    const._platforms[self.cChipset.Selection]["flash_cmd"], 0x30)

                            else:
                                self.cmd_write_u32(
                                    const._platforms[self.cChipset.Selection]["flash_cmd"], (cOffset >> 8) & 1)

                                self.cmd_write_u32(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], cOffset & 0xff)

                                self.cmd_write_u32(
                                    const._platforms[self.cChipset.Selection]["flash_addr"], (cOffset >> 9) & 0xff)
                                self.cmd_write_u32(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 9) >> 8) & 0xff)
                                self.cmd_write_u32(const._platforms[self.cChipset.Selection]["flash_addr"], ((
                                    cOffset >> 9) >> 16) & 0xff)

                            for _ in range(0x2500):
                                _msleep(const._jtag_sleep_delay)
                                if const._platforms[self.cChipset.Selection]["wait_mask"] is not None:
                                    if self.cmd_read_u32(const._platforms[self.cChipset.Selection]["flash_wait"]) & const._platforms[self.cChipset.Selection]["wait_mask"]:
                                        break

                            temp_buf = []
                            for _ in range(0x400 if self.cNandSize.Selection == 1 else 0x100):
                                temp_buf.append(self.cmd_read_u32(
                                    const._platforms[self.cChipset.Selection]["flash_buffer"]))
                                cOffset += 2

                                if cOffset >= eOffset:
                                    break

                            tempFile.write(b"".join([x.to_bytes(
                                2, "big" if self.cTarget.Selection >= self._beTarget else "little") for x in temp_buf]))
                            if cOffset >= eOffset:
                                break

                    elif const._platforms[self.cChipset.Selection]["mode"] == 6:
                        raise NotImplementedError()

                    elif const._platforms[self.cChipset.Selection]["mode"] == 7:
                        O1N_BASE = int(const._platforms[self.cChipset.Selection]["o1n_offset"],
                                       16) if "o1n_offset" in const._platforms[self.cChipset.Selection] else baseO1N

                        self.cmd_write_u16(
                            O1N_BASE + 0x1E202, 0x8000 if O1N_isDDP and (cOffset >> 17) >= O1N_Density else 0x0)
                        self.cmd_write_u16(O1N_BASE + 0x1E200, (0x8000 if O1N_isDDP and (
                            cOffset >> 17) >= O1N_Density else 0x0) | ((cOffset >> 17) & (O1N_Density - 1)))
                        self.cmd_write_u16(
                            O1N_BASE + 0x1E20E, (cOffset >> 9) & 0xff)

                        self.cmd_write_u16(O1N_BASE + 0x1E400, 0x800)

                        if self.bECCDisable.Value:
                            self.cmd_write_u16(
                                O1N_BASE + 0x1E442, self.cmd_read_u16(O1N_BASE + 0x1E442) | (1 << 8))

                        else:
                            self.cmd_write_u16(
                                O1N_BASE + 0x1E442, self.cmd_read_u16(O1N_BASE + 0x1E442) & 0xfeff)

                        self.cmd_write_u16(O1N_BASE + 0x1E482, 0)
                        self.cmd_write_u16(O1N_BASE + 0x1E440, 0)

                        for _ in range(0x2500):
                            _msleep(const._jtag_sleep_delay)
                            if self.cmd_read_u16(O1N_BASE + 0x1E482) & 0x8000:
                                break

                        for x in range(8 if self.cNandSize.Selection == 1 else 4):
                            tempFile.write(self.cmd_read_u8(
                                O1N_BASE + 0x400 + (0x200 * x), 0x200))
                            spareBuf += self.cmd_read_u8(O1N_BASE +
                                                         0x10020 + (0x10 * x), 0x10)

                            cOffset += 0x200
                            if cOffset >= eOffset:
                                break

                    else:
                        raise Exception(
                            "The read flash code should not reach there")

                    self._progMsgQueue.put(cOffset/eOffset)

                tempFile.write(spareBuf + bbBuf)
                self._logThreadQueue.put(f"Dump flash finished {datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}")
                # tempFile.write() # TODO: Write Dumpit Device Footer format

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
            self._logSupressed = False

            self._doAnalytics("dump_end", addr_start=cOffset,
                              addr_end=eOffset, is_memory=False)

    def doReadFlash(self, event):
        if (not self._isConnect and not self._isConnectRemote) or self._isRead:
            return

        cOffset = int(self.tStart.Value, 16)
        eOffset = int(self.tEnd.Value, 16)

        if cOffset >= eOffset:
            return wx.MessageBox(f"start offset must be less than end offset", "Dumpit", wx.OK | wx.CENTER | wx.ICON_ERROR, self)

        flash_div = (0x800 if self.cNandSize.Selection == 1 else 0x200) if const._platforms[self.cChipset.Selection]["mode"] != 7 else (
            0x1000 if self.cNandSize.Selection == 1 else 0x800)

        if (cOffset % flash_div) != 0 or (eOffset % flash_div) != 0:
            return wx.MessageBox(f"offset not divisible by {hex(flash_div)} is not supported", "Dumpit", wx.OK | wx.CENTER | wx.ICON_ERROR, self)

        with wx.FileDialog(self, "Dump flash", wildcard="Binary file|*.bin", style=wx.FD_SAVE) as fd:
            fd: wx.FileDialog
            if fd.ShowModal() != wx.ID_CANCEL:
                self.progress.Value = 0
                O1N_INPUT_OFFSET = -1

                if const._platforms[self.cChipset.Selection]["mode"] == 7 and "o1n_offset" not in const._platforms[self.cChipset.Selection]:
                    try:
                        with wx.TextEntryDialog(self, "Enter OneNAND base offset", "Dumpit") as t:
                            t: wx.TextEntryDialog
                            if t.ShowModal() == wx.ID_CANCEL:
                                return

                            O1N_INPUT_OFFSET = int(t.Value, 16)

                    except Exception as e:
                        wx.MessageBox(str(e), "Dumpit", wx.OK |
                                      wx.CENTER | wx.ICON_ERROR, self)
                        return

                self._dumpThread = threading.Thread(target=self.doReadFlashThread, args=(
                    fd.GetPath(), cOffset, eOffset, O1N_INPUT_OFFSET))
                self._dumpThread.daemon = True

                self._dumpThread.start()

    def doStop(self, event):
        self._isReadCanceled = True
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
        _msleep(self._resetDelays[self.cResetDelay.Selection][1] * 1000)
        self._ocdSendCommand("soft_reset_halt")

    def doHardReset(self, event):
        if not self._isConnect and not self._isConnectRemote:
            return
        _msleep(self._resetDelays[self.cResetDelay.Selection][1] * 1000)
        self._ocdSendCommand("reset init")

    def doLoader(self, event):
        with wx.FileDialog(self, "Load DCC", wildcard="DCC Hex file|*.hex", style=wx.FD_OPEN) as fd:
            fd: wx.FileDialog
            if fd.ShowModal() != wx.ID_CANCEL:                
                self._loaded_dcc = fd.GetPath()
            else:                
                self._loaded_dcc = None
                
            self.lCurrentDCC.SetLabel(f"DCC Loader: {self._loaded_dcc}")

    def doScript(self, event):
        event.Skip()

    def doDisableMMU(self, event):
        if not self._isConnect and not self._isConnectRemote:
            return
        cp15 = self.cmd_read_cp15(1, 0, 0, 0)
        self.cmd_write_cp15(1, 0, 0, 0, cp15 & 0xfffffffe)

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

        self.Sizer.Layout()

    def doOpenFT232RConfig(self, event):
        FT232RConfig(self).ShowModal()

    def doOpenFT232HConfig(self, event):
        FT232HConfig(self).ShowModal()

    def doOpenGPIODConfig(self, event):
        wx.MessageBox("Not implemented", "Dumpit", wx.OK |
                      wx.CENTER | wx.ICON_ERROR, self)

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
                    f"ftdi://{self.tUSBID1.Value}/{self.cChannel.Selection+1}", mpsse=self.bUseMPSSE.Value)

            elif self.cInterface.Selection == len(const._interfaces) - 1:
                p = libfindit.find_jtag_idcode("", True)

            else:
                return

            if len(p) >= 1:
                self.finderStatus.Value = f"IDCODE: {' '.join(p[0]['idcodes'])}\nTDO: {p[0]['tdo']}\nTCK: {p[0]['tck']}\nTMS: {p[0]['tms']}\n#TRST: {' '.join(str(x) for x in p[0]['possible_ntrst'])}"
                self._known_tdo = p[0]['tdo']
                self._known_tck = p[0]['tck']
                self._known_tms = p[0]['tms']

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
                    f"ftdi://{self.tUSBID.Value}/1", known_tdo=self._known_tdo, known_tck=self._known_tck, known_tms=self._known_tms)

            elif self.cInterface.Selection == 1:
                p = libfindit.find_jtag_bypass(f"ftdi://{self.tUSBID1.Value}/{self.cChannel.Selection+1}", mpsse=self.bUseMPSSE.Value,
                                               known_tdo=self._known_tdo, known_tck=self._known_tck, known_tms=self._known_tms)

            elif self.cInterface.Selection == len(const._interfaces) - 1:
                p = libfindit.find_jtag_bypass(
                    "", True, known_tdo=self._known_tdo, known_tck=self._known_tck, known_tms=self._known_tms)

            else:
                return

            if len(p) >= 1:
                self.finderStatus.Value = f"TDI: {p[0]['tdi']}\nTDO: {p[0]['tdo']}\nTCK: {p[0]['tck']}\nTMS: {p[0]['tms']}\n#TRST: {' '.join(str(x) for x in p[0]['possible_ntrst'])}"

                self._known_tdi = p[0]['tdi']
                self._known_tdo = p[0]['tdo']
                self._known_tck = p[0]['tck']
                self._known_tms = p[0]['tms']

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
                    f"ftdi://{self.tUSBID.Value}/1", known_tck=self._known_tck)

            elif self.cInterface.Selection == 1:
                p = libfindit.find_jtag_rtck(
                    f"ftdi://{self.tUSBID1.Value}/{self.cChannel.Selection+1}", mpsse=self.bUseMPSSE.Value, known_tck=self._known_tck)

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
        if wx.MessageBox("Exit Dumpit?", "Dumpit", wx.YES_NO | wx.CENTER | wx.ICON_QUESTION, self) == wx.YES:
            if self._isConnect:
                self._isConnect = False
                self._ocd.terminate()
                if self._isForward and self._isConnectRemote:
                    self._isConnectRemote = False
                    self._isForward = False
                    if self._sio and self._sio.connected:
                        self._sio.emit("bye")
                        self._sio.disconnect()

            elif self._isConnectRemote:
                self._isConnectRemote = False
                if self._sio and self._sio.connected:
                    self._sio.emit("bye")
                    self._sio.disconnect()

            cfg = {}

            cfg["interface"] = self.cInterface.Selection
            cfg["speed"] = self.nSpeed.Value
            cfg["chipset"] = self.cChipset.Selection
            cfg["target"] = self.cTarget.Selection
            cfg["tap"] = self.cTap.Selection
            cfg["ir"] = self.nIR.Value
            cfg["reset_mode"] = self.cResetMode.Selection
            cfg["reset_delay"] = self.cResetDelay.Selection
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

            json.dump(cfg, open(os.path.join(os.path.dirname(
                __file__), "dumpit_config.json"), "w"), indent=4)
            
            wx.Exit()

    def doOCDCmdExec(self, event):
        temp = self.tOCDCmd.Value
        self.tOCDCmd.Value = ""
        if not self._isConnect and not self._isConnectRemote:
            return

        self._logThreadQueue.put(
            f"command returned: {self._ocdSendCommand(temp)}")

    def doRegenUUID(self, event):
        global _PTRACKCOUNT
        self.tUserID.Value = str(uuid.uuid4())
        _PTRACKCOUNT = {}

        temp_analytics = "Tracking count:\n"

        for k in _PTRACKCOUNT:
            temp_analytics += f"{k}: {_PTRACKCOUNT[k]}\n"

        self.analytics_stat.Value = temp_analytics


def getInitCmd(self: MainApp):
    cInit = const._interfaces[self.cInterface.Selection][1].replace('(FT232R_VID)', self.tUSBID.Value.split(':')[0]).replace('(FT232R_PID)', self.tUSBID.Value.split(':')[1]).replace('(FT232R_RESTORE_SERIAL)', self.tRestoreSerial.Value).replace('(FT232H_VID)', self.tUSBID1.Value.split(':')[0]).replace('(FT232H_PID)', self.tUSBID1.Value.split(':')[1]).replace('(FT232H_CHANNEL)', str(self.cChannel.Selection)).replace('(FT232H_EDGE)', ['rising', 'falling'][self.rSamplingEdge.Selection]).replace('(FT232H_PINS)', hex(self._ft232h_pins)).replace('(FT232H_DIR)', hex(self._ft232h_dirs)).replace(
        '(FT232H_LAYOUT_SIGNAL)', f'ftdi layout_signal nTRST -data {hex(1 << self._ft232h_trst)} -oe {hex(1 << self._ft232h_trst)}; ftdi layout_signal nSRST -data {hex(1 << self._ft232h_srst)} -oe {hex(1 << self._ft232h_srst)}; ftdi layout_signal TDI -data {hex(1 << self._ft232h_tdi)}; ftdi layout_signal TDO -data {hex(1 << self._ft232h_tdo)} -oe {hex(1 << self._ft232h_tdo)}; ftdi layout_signal TCK -data {hex(1 << self._ft232h_tck)}; ftdi layout_signal TMS -data {hex(1 << self._ft232h_tms)}').replace("(FT232R_PINS)", "").replace("(GPIOD_CHIP)", str(self.nGPIODChip.Value)).replace('(GPIOD_TDI_PIN)', str(self._gpio_tdi)).replace('(GPIOD_TDO_PIN)', str(self._gpio_tdo)).replace('(GPIOD_TCK_PIN)', str(self._gpio_tck)).replace('(GPIOD_TMS_PIN)', str(self._gpio_tms)).replace('(GPIOD_TRST_PIN)', str(self._gpio_trst)).replace('(GPIOD_SRST_PIN)', str(self._gpio_srst)).replace('(PARPORT_CABLE)', ["dlc5", "wiggler"][self.cParCable.Selection]).replace('(PARPORT_PORT)', self.tParPort.Value).replace('(REMOTE_BITBANG_HOST)', self.tRBBHost.Value).replace('(REMOTE_BITBANG_PORT)', self.tRBBPort.Value)

    if self.cInterface.Selection == 1:
        if const._ft232h_adapters[self.cFTAdapter.Selection][1] != "":
            cInit = f"{const._ft232h_adapters[self.cFTAdapter.Selection][1]} ftdi tdo_sample_edge {['rising', 'falling'][self.rSamplingEdge.Selection]};"

    INIT_CMD = f"{cInit} telnet_port 0; gdb_port 0; tcl_port pipe; reset_config {const._reset_type[self.cResetMode.Selection][1]}; jtag_ntrst_delay {self._resetDelays[self.cResetDelay.Selection][0]}; adapter srst delay {self._resetDelays[self.cResetDelay.Selection][1]}; "

    if int(self.nSpeed.Value) <= 0:
        INIT_CMD += f"jtag_rclk 1000; "
    else:
        INIT_CMD += f"adapter speed {self.nSpeed.Value}; "

    if self.cTarget.Selection >= 1:
        t = self.cTarget.Selection
        isBig = False

        if t >= self._beTarget:
            isBig = True
            t -= self._beTarget

        else:
            t -= 1

        fixedIR = 0
        for v in const._force_ir:
            if const._targets[t] in const._force_ir[v]:
                fixedIR = v

        if const._targets[t] in const._dap_required:
            INIT_CMD += const._init_dap.replace("(IR)", str(fixedIR) if fixedIR != 0 else str(self.nIR.Value)).replace(
                "(XPARAM)", "").replace("(TYPE)", const._targets[t]).replace("(ENDIAN)", "big" if isBig else "little")

        else:
            INIT_CMD += const._init_normal.replace("(IR)", str(fixedIR) if fixedIR != 0 else str(self.nIR.Value)).replace(
                "(XPARAM)", "").replace("(TYPE)", const._targets[t]).replace("(ENDIAN)", "big" if isBig else "little")

        self._cfi_start_offset = 0

        if self._loaded_dcc is not None:
            path_escaped = self._loaded_dcc.replace('\\', '/')
            INIT_CMD += "flash bank target.dcc ocl 0 0 0 0 target.cpu; set _DCC_PATH {" + path_escaped + "}; " + f"set _DCC_START_OFFSET {hex(intelhex.IntelHex(self._loaded_dcc).minaddr())}; "

        elif const._platforms[self.cChipset.Selection]["mode"] == -1:
            INIT_CMD += "flash bank target.dcc dummy_flash 0 0 0 0 target.cpu; "

        elif const._platforms[self.cChipset.Selection]["mode"] == 4:
            INIT_CMD += f"flash bank target.nor cfi 0x{self.tStart.Value} {hex(int(self.tEnd.Value, 16) - int(self.tStart.Value, 16))} {const._platforms[self.cChipset.Selection]['chip_width']} {const._platforms[self.cChipset.Selection]['bus_width']} target.cpu; "
            self._cfi_start_offset = int(self.tStart.Value, 16)

        INIT_CMD += "target.cpu configure -event examine-end { halt; "
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

        INIT_CMD += "}"

    return INIT_CMD


if __name__ == "__main__":
    app = wx.App(True)
    m = MainApp(None)
    m.Show()
    app.MainLoop()
