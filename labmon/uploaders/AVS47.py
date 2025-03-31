from dataclasses import dataclass, replace
import sys
import logging
from datetime import datetime, timedelta
from typing import Optional
import ctypes
import asyncio

import serial

from labmon.config.config import AVS47ChannelConfig

from ..utility.calibrations import CALIBRATIONS, VALID_CALS
from ..utility.timers import enable_high_res_timer
from ..utility.retry import retry
from ..utility.si_prefix import si_format
from ..config import AVS47Config
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
    "UNK": -1,
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
    "UNK": -1,
}
R_INPUT_RANGE: list[str] = list(INPUT_RANGE.keys())

INPUT_SELECT: dict[str, int] = {"Zero": 0, "Measure": 1, "Calibrate": 2, "UNK": -1}
R_INPUT_SELECT: list[str] = list(INPUT_SELECT.keys())


class AVS47DataStruct(ctypes.LittleEndianStructure):
    def __init__(
        self,
        address: int = 0,
        remote: int = 1,
        input_range: str | int = 0,
        excitation: str | int = 0,
        display: int = 0,
        channel: int = 0,
        input_select: int | str = 0,
    ):
        if isinstance(input_range, str):
            try:
                input_range = INPUT_RANGE[input_range]
            except KeyError:
                raise KeyError(f"Invalid input range. Valid ranges are: {', '.join(R_INPUT_RANGE)}")

        if isinstance(excitation, str):
            try:
                excitation = EXCITATION[excitation]
            except KeyError:
                raise KeyError(
                    f"Invalid excitation. Valid excitations are: {', '.join(R_EXCITATION)}"
                )

        if isinstance(input_select, str):
            try:
                input_select = INPUT_SELECT[input_select]
            except KeyError:
                raise KeyError(
                    f"Invalid input selection. Valid values are: {', '.join(R_INPUT_SELECT)}"
                )

        super().__init__(
            address, remote, 0, input_range, excitation, display, channel, input_select, *([0] * 8)
        )

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
        return self.readout * (10.0 ** (self.input_range - 5))

    def copy(self):
        new_copy = AVS47DataStruct()
        ctypes.pointer(new_copy)[0] = self  # *new_copy = self
        return new_copy


class AVS47Data(ctypes.LittleEndianUnion):
    _fields_ = [("bits", AVS47DataStruct), ("value", ctypes.c_uint64)]


NULL_DATA = AVS47Data(value=0)


@dataclass
class AVS47ChannelState:
    enabled: bool
    channel: int
    input_range: int
    excitation: int
    resistance: float = 0

    @property
    def channel_change(self) -> tuple[AVS47Data, AVS47Data]:
        # Set to default excitation if not known
        if self.excitation is EXCITATION["UNK"]:
            excitation = EXCITATION["30uV"]
        else:
            excitation = self.excitation

        # Set to default input range if not known
        if self.input_range is INPUT_RANGE["UNK"]:
            input_range = INPUT_RANGE["2R"]
        else:
            input_range = self.input_range

        change_state = AVS47DataStruct(
            remote=1,
            channel=self.channel,
            excitation=excitation,
            input_range=input_range,
            input_select=INPUT_SELECT["Measure"],
        )
        lock_state = change_state.copy()
        lock_state.remote = 0

        return AVS47Data(bits=change_state), AVS47Data(bits=lock_state)


class AVS47:
    """
    AVS47 bit-banging driver
    """

    def __init__(
        self,
        serial_port: str,
        config: dict[int, AVS47ChannelConfig],
        address: int = 1,
        bitbang_delay: float = 0.001,
    ):
        self.port = serial_port
        self.address = address
        self.config = config
        self.bitbang_delay = bitbang_delay

        # Set up the instrument state
        self.active_channel: int = -1
        self.scan_task: Optional[asyncio.Task] = None
        self.scan_complete: bool = False
        self.temperatures: dict[int, float] = {}

        # On windows, the maximum timer resolution is 1ms
        if sys.platform.startswith("win32") and bitbang_delay < 0.001:
            logger.warning(
                (
                    "Maximum timer resolution on windows is 1ms, requested: %ss. "
                    "Delay will be rounded to 0.001 ms."
                ),
                si_format(bitbang_delay),
            )
            self.bitbang_delay = 0.001

        self.serial = serial.Serial(self.port)
        self.serial.rts = False

        # Set up the channel state dictionary, by default set all configured channels enabled
        self.channel_states: list[AVS47ChannelState] = []
        for i in range(8):
            if i in config:
                excitation = EXCITATION[config[i].EXCITATION]
            else:
                excitation = EXCITATION["UNK"]
            self.channel_states.append(
                AVS47ChannelState(
                    enabled=(i in config),
                    channel=i,
                    input_range=INPUT_RANGE["UNK"],
                    excitation=excitation,
                )
            )

    def close(self):
        """
        Close and delete serial connection
        """
        self.serial.close()
        del self.serial

    async def startup(self):
        """
        Query the starting state of the instrument on connection. This is separated out from the
        init function as it must be asynchronous.
        """
        state = await self.send_and_receive()

        if R_INPUT_SELECT[state.bits.input_select] == "Measure":
            # We are on a selected channel
            self.active_channel = state.bits.channel
            channel_state = self.channel_states[self.active_channel]
            self.channel_states[self.active_channel] = replace(
                channel_state,
                input_range=state.bits.input_range,
                excitation=state.bits.excitation,
                resistance=state.bits.resistance,
            )
        else:
            # We are either zero'd or not measuring
            self.active_channel = -1

    def start_scan(self):
        """
        Start auto scan
        """
        # Check if the scan task is already running
        if self.scan_task is not None:
            if self.scan_task.done():
                logger.info("AVS scan task ended with result: %r", self.scan_task.result())
                self.scan_task = None
            else:
                # Scanner is already running
                return

        # Start scan task
        logger.info("Starting AVS scan task")
        self.scan_task = asyncio.create_task(self.scan())

    def check_scan(self) -> bool:
        """
        Check if scan is running
        """
        if self.scan_task is None:
            return False
        if self.scan_task.done():
            logger.info("AVS scan task ended with result: %r", self.scan_task.result())
            self.scan_task = None
            return False
        return True

    def stop_scan(self):
        """
        Stop auto scan
        """
        if self.scan_task is None:
            return

        if not self.scan_task.done():
            self.scan_task.cancel()
            logger.info("Stopping AVS scan task")

    async def scan(self):
        """
        Task that scans through all enabled channels on the AVS, and at the end updates the scan_complete
        flag.
        """
        warned = False
        try:
            while True:
                # Before starting a scan, ensure that there are some enabled channels, giving a warning
                # on the first time this is noticed.
                if all(channel.enabled is False for channel in self.channel_states):
                    if not warned:
                        warned = True
                        logger.warning("All channels on the AVS are disabled.")
                    await asyncio.sleep(5)
                    continue
                warned = False

                # Poll the instrument to make sure we are in a consistent state before starting a scan
                await self.startup()

                # Scan through all channels
                new_temperatures: dict[int, float] = {}
                for channel in self.channel_states:
                    # Skip over disabled channels
                    if channel.enabled is False:
                        continue

                    # Load channel config
                    if channel.channel not in self.config:
                        logger.error(
                            "Channel %d not configured, but is enabled. Please edit the config file. Skipping....",
                            channel.channel,
                        )
                        channel = replace(channel, enabled=False)
                        self.channel_states[channel.channel] = channel
                        continue
                    channel_config = self.config[channel.channel]

                    # Check if we need to change the channel
                    failed = False
                    if self.active_channel != channel.channel:
                        logger.debug("Changing channel to %d", channel.channel)
                        # Set channel to active
                        change, lock = channel.channel_change
                        await self.send_and_receive(change)
                        new_state = await self.send_and_receive(lock)
                        self.active_channel = channel.channel

                        # Wait for the settling delay
                        settling_delay = timedelta(seconds=channel_config.SETTLE_DELAY)
                        settling_start = datetime.now()

                        while (datetime.now() - settling_start) < settling_delay:
                            # Double check that the readout channel is correct. If not, restart the scan
                            # after a few seconds
                            if new_state.bits.channel != channel.channel:
                                logger.error(
                                    "AVS channel changed unexpectedly. Expected: %d, reading: %d",
                                    channel.channel,
                                    new_state.bits.channel,
                                )
                                logger.error("Restarting scan in 5 seconds ")
                                failed = True
                                await asyncio.sleep(5)
                                break

                            # Check if the sensor range has changed, and if so, reset settling time
                            if new_state.bits.input_range != channel.input_range:
                                self.settling_start = datetime.now()

                            # Update the channel config with the latest values
                            channel = replace(
                                channel,
                                input_range=new_state.bits.input_range,
                                resistance=new_state.bits.resistance,
                            )
                            self.channel_states[channel.channel] = channel

                            # Wait some time and read out a new value from the AVS
                            await asyncio.sleep(1)
                            new_state = await self.send_and_receive()

                    # If the scan failed for whatever reason, then don't read value
                    if failed:
                        break

                    # State is settled - readout value
                    resistance = 0.0
                    for count in range(channel_config.AVERAGE_COUNT):
                        # This time we sleep at the start
                        await asyncio.sleep(channel_config.AVERAGE_DELAY)
                        new_state = await self.send_and_receive()

                        # Double check that scan range/channel hasn't changed
                        if (
                            new_state.bits.channel != channel.channel
                            or new_state.bits.input_range != channel.input_range
                        ):
                            logger.warning(
                                "Value for channel %d was unstable during read. Skippping...",
                                channel.channel,
                            )
                            failed = True
                            break

                        channel = replace(channel, resistance=new_state.bits.resistance)
                        self.channel_states[channel.channel] = channel
                        logger.debug(
                            "AVS channel %d resistance is %sΩ",
                            channel.channel,
                            si_format(new_state.bits.resistance, 3),
                        )
                        resistance += new_state.bits.resistance

                    # Don't store value if readout failed
                    if failed:
                        continue

                    # State is read out, convert the value
                    resistance /= channel_config.AVERAGE_COUNT
                    if channel_config.CALIBRATION in CALIBRATIONS:
                        temperature = CALIBRATIONS[channel_config.CALIBRATION](resistance)

                        if temperature is not None:
                            logger.info(
                                "AVS Channel %d Temperature is: %sK (Resistance: %sΩ)",
                                channel.channel,
                                si_format(temperature, 3),
                                si_format(resistance, 3),
                            )
                            new_temperatures[channel.channel] = temperature
                        else:
                            logger.info(
                                "AVS Channel %d Temperature out of range (Resistance: %sΩ)",
                                channel.channel,
                                si_format(resistance, 3),
                            )
                    else:
                        # Invalid calibration
                        logger.warning(
                            "Calibration %s for channel %d is not unknown. Valid values are: %s.",
                            channel_config.CALIBRATION,
                            channel.channel,
                            VALID_CALS,
                        )

                # Mark scan complete
                if self.scan_complete is True:
                    logger.warning("Next AVS scan completed before previous value uploaded.")
                self.temperatures = new_temperatures
                self.scan_complete = True
        # Scan ended
        except asyncio.CancelledError:
            logger.info("AVS Scan task ended")
            raise

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

    async def send_and_receive(self, data: AVS47Data = NULL_DATA) -> AVS47Data:
        """
        Send and receive some data
        """
        if data.value == NULL_DATA.value:
            logger.debug("AVS Sending data: NULL_DATA")
        else:
            logger.debug("AVS Sending data: %r", data.bits)

        # Send the address to select the correct AVS. This must be done each time
        # as it is not stored (presumably to allow chaining?)
        await self._send_address()
        return_value = 0
        # Send out data while simultaneously receiving it
        with enable_high_res_timer():
            # Start comms
            self.CP = 0
            for i in range(48):
                self.DC = (data.value >> (47 - i)) & 0x1
                return_value |= self.DI << (47 - i)
                await self._clock()
            self.DC = 0
            await self._end_comm()

        # Return the result
        res = AVS47Data(value=return_value)
        logger.debug("AVS returned data: %r", res.bits)
        return res

    async def _send_address(self):
        with enable_high_res_timer():
            # Start comms
            self.CP = 0
            for i in range(8):
                self.DC = (self.address >> (7 - i)) & 0x1
                await self._clock()
            self.DC = 0
            await self._end_comm()

    async def _clock(self):
        self.CP = 1
        await asyncio.sleep(self.bitbang_delay)
        self.CP = 0
        await asyncio.sleep(self.bitbang_delay)

    async def _end_comm(self):
        for _ in range(3):
            self.DC = 1
            await asyncio.sleep(self.bitbang_delay)
            self.DC = 0
            await asyncio.sleep(self.bitbang_delay)


class AVS47Monitor(Uploader[AVS47Config]):
    def __init__(self, config: AVS47Config, **kwargs):
        super().__init__(config, **kwargs)

        self._instr_conn: Optional[AVS47] = None
        self.upload_interval = timedelta(seconds=config.UPLOAD_INTERVAL)

    @retry(multiplier=1.2, max_wait=15, exception=RuntimeError)
    async def open_connection(self) -> AVS47:
        """
        Try opening a connection to the sample instrument
        """
        instr = AVS47(self.config.SERIAL_PORT, self.config.SENSORS, address=self.config.ADDRESS)
        await instr.startup()
        logger.info("Connected to AVS47 with address: %d", instr.address)
        instr.start_scan()
        return instr

    async def poll(self):
        """
        Upload if the appropriate interval has passed

        Returns true if a new value is read or data is uploaded, otherwise false.
        """
        # If we aren't connected to the lakeshore, try opening the connection
        if self._instr_conn is None:
            self._instr_conn = await self.open_connection()

        # Check if the scan is still running. If not, try to reopen the connection
        if self._instr_conn.check_scan() is False:
            logger.error("AVS scan failed. Trying to reconnect to instrument...")
            self._instr_conn = None
            return False

        # Check if the AVS has completed the last scan
        if self._instr_conn.scan_complete:
            data = {}
            for channel, value in self._instr_conn.temperatures.items():
                if self.config.UPLOAD_MILLIKELVIN:
                    value *= 1000
                if channel in self.config.SENSORS:
                    data[self.config.SENSORS[channel].SENSOR] = value
                else:
                    logger.error("AVS channel %d has a value but is not configured", channel)
            await self.upload(data)
            self._instr_conn.scan_complete = False
            return True

        return False
