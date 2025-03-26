import sys
import logging
from datetime import datetime, timedelta
from typing import Optional
import ctypes
import asyncio

import serial

from ..utility.timers import enable_high_res_timer
from ..utility.retry import retry
from ..config import SampleUploadConfig
from .uploader import Uploader

logger = logging.getLogger(__name__)

EXCITATION: dict[str, int] = {
    "0": 0,
    "3uV": 1,
    "10uV": 2,
    "30uV": 3,
    "100uV": 4,
    "300uV": 5,
    "1mV": 6,
    "3mV": 7,
}
R_EXCITATION: list[str] = list(EXCITATION.keys())

INPUT_RANGE: dict[str, int] = {
    "Open": 0,
    "2R": 1,
    "20R": 2,
    "200R": 3,
    "2K": 4,
    "20K": 5,
    "200K": 6,
    "2M": 7,
}
R_INPUT_RANGE: list[str] = list(INPUT_RANGE.keys())

INPUT_SELECT: dict[str, int] = {"Zero": 0, "Measure": 1, "Calibrate": 2}
R_INPUT_SELECT: list[str] = list(INPUT_SELECT.keys())


class AVS47DataStruct(ctypes.LittleEndianStructure):
    _fields_ = [
        ("address", ctypes.c_uint64, 6),  # 0-6
        ("remote", ctypes.c_uint64, 1),  # 7
        ("_pad", ctypes.c_uint64, 1),  # 8
        ("input_range", ctypes.c_uint64, 3),  # 9-11
        ("excitation", ctypes.c_uint64, 3),  # 12-14
        ("display", ctypes.c_uint64, 3),  # 15-17
        ("channel", ctypes.c_uint64, 3),  # 18-20
        ("input_select", ctypes.c_uint64, 2),  # 21-22
        ("_pad2", ctypes.c_uint64, 2),  # 23-24
        ("digit1", ctypes.c_uint64, 4),  # 25-28
        ("digit2", ctypes.c_uint64, 4),  # 29-32
        ("digit3", ctypes.c_uint64, 4),  # 33-36
        ("digit4", ctypes.c_uint64, 4),  # 37-40
        ("digit5", ctypes.c_uint64, 1),  # 41
        ("_pad3", ctypes.c_uint64, 3),  # 42-44
        ("_pad4", ctypes.c_uint64, 4),  # 45-48
    ]

    def __repr__(self):
        exc = R_EXCITATION[self.excitation]
        inp_range = R_INPUT_RANGE[self.input_range]
        inp_select = R_INPUT_SELECT[self.input_select]

        params = (
            f"address={self.address}, "
            f"remote={self.remote}, "
            f"input_range={inp_range}, "
            f"excitation={exc}, "
            f"channel={self.channel}, "
            f"input_select={inp_select}, "
            f"resistance={self.resistance:.4f}"
        )

        return f"AVS47DataStruct({params})"

    @property
    def readout(self):
        value = 0
        for i in range(5):
            value += getattr(self, f"digit{i + 1}") * (10**i)
        return value

    @property
    def resistance(self):
        return self.readout * 10 ** (self.input_range - 5)


class AVS47Data(ctypes.LittleEndianUnion):
    _fields_ = [("bits", AVS47DataStruct), ("value", ctypes.c_uint64)]


NULL_DATA = AVS47Data(value=0)


class AVS47:
    """
    AVS47 bit-banging driver
    """

    def __init__(self, serial_port: str, address: int = 1, delay: float = 0.001):
        self.port = serial_port
        self.address = address
        self.delay = delay

        # On windows, the maximum timer resolution is 1ms
        if sys.platform.startswith("win32") and delay < 0.001:
            logger.warning(
                (
                    "Maximum timer resolution on windows is 1ms, requested: %.2e. "
                    "Delay will be rounded to the nearest ms."
                ),
                delay,
            )

        self.serial = serial.Serial(self.port)
        self.serial.rts = False

    @property
    def CP(self) -> int:
        return int(self.serial.rts)

    @CP.setter
    def CP(self, value: int):
        self.serial.rts = bool(value)

    @property
    def DC(self) -> int:
        return int(self.serial.dtr)

    @DC.setter
    def DC(self, value: int):
        self.serial.dtr = bool(value)

    @property
    def DI(self):
        return int(self.serial.cts)

    async def send_address(self):
        with enable_high_res_timer():
            # Start comms
            self.CP = 0
            for i in range(8):
                self.DC = (self.address >> (7 - i)) & 0x1
                await self._clock()
            self.DC = 0
            await self._end_comm()

    async def send_and_receive(self, data: AVS47Data = NULL_DATA):
        return_value = 0
        with enable_high_res_timer():
            # Start comms
            self.CP = 0
            for i in range(48):
                self.DC = (data.value >> (47 - i)) & 0x1
                data.value >>= 1
                return_value |= self.DI << (47 - i)
                await self._clock()
            self.DC = 0
            await self._end_comm()

        return AVS47Data(value=return_value)

    async def _clock(self):
        self.CP = 1
        await asyncio.sleep(self.delay)
        self.CP = 0
        await asyncio.sleep(self.delay)

    async def _end_comm(self):
        for _ in range(3):
            self.DC = 1
            await asyncio.sleep(self.delay)
            self.DC = 0
            await asyncio.sleep(self.delay)


class AVS47Monitor(Uploader[SampleUploadConfig]):
    def __init__(self, config: SampleUploadConfig, **kwargs):
        super().__init__(config, **kwargs)

        self._instr_conn: Optional[AVS47] = None
        self.upload_interval = timedelta(seconds=config.UPLOAD_INTERVAL)

    @retry(multiplier=1.2, max_wait=15, exception=RuntimeError)
    def open_connection(self) -> AVS47:
        """
        Try opening a connection to the sample instrument
        """
        instr = AVS47("Sample_Instrument")
        logger.info("Connected to AVS47 with address: %d", instr.address)
        return instr

    async def poll(self):
        """
        Upload if the appropriate interval has passed

        Returns true if a new value is read or data is uploaded, otherwise false.
        """
        # If we aren't connected to the lakeshore, try opening the connection
        if self._instr_conn is None:
            self._instr_conn = self.open_connection()

        try:
            if (datetime.now().astimezone() - self.latest) > self.upload_interval:
                # We're ready to upload the next dataset
                data = {}
                for field in self.config.FIELD_NAMES:
                    data[field] = 0
                await self.upload(data)
                return True
        except ValueError as e:
            logger.error("Failed to retrieve value", exc_info=e)
            self._instr_conn = None

        return False
