import logging
from collections import deque
from datetime import datetime, timedelta
from typing import Optional
import struct

import pyvisa as visa

from ..utility.hilbert import hilbert_amplitude
from ..utility.retry import retry
from ..config import CryomechConfig
from .uploader import Uploader

logger = logging.getLogger(__name__)


CPA_FIELD_MAP = {
    "Bounce": "bounce",
    "Current": "motor_current",
    "Helium": "helium_temp",
    "Oil": "oil_temp",
    "WaterIn": "input_water_temp",
    "WaterOut": "output_water_temp",
    "Delta": "average_delta_pressure",
    "High": "average_high_pressure",
    "Low": "average_low_pressure",
}


class Cryomech:
    @property
    def state(self) -> bool:
        raise NotImplementedError()

    @property
    def run_time(self) -> float:
        raise NotImplementedError()

    @property
    def motor_current(self) -> float:
        raise NotImplementedError()

    @property
    def input_water_temp(self) -> float:
        raise NotImplementedError()

    @property
    def output_water_temp(self) -> float:
        raise NotImplementedError()

    @property
    def oil_temp(self) -> float:
        raise NotImplementedError()

    @property
    def helium_temp(self) -> float:
        raise NotImplementedError()

    @property
    def high_pressure(self) -> float:
        raise NotImplementedError()

    @property
    def low_pressure(self) -> float:
        raise NotImplementedError()

    @property
    def average_high_pressure(self) -> float:
        raise NotImplementedError()

    @property
    def average_low_pressure(self) -> float:
        raise NotImplementedError()

    @property
    def average_delta_pressure(self) -> float:
        raise NotImplementedError()

    @property
    def bounce(self) -> float:
        raise NotImplementedError()


class CryomechV1(Cryomech):
    CPA_PARAMETERS: dict[str, bytes] = {
        "RUNTIME": bytes([0x45, 0x4C, 0x00]),
        "MOTOR_CURRENT": bytes([0x63, 0x8B, 0x00]),
        "INPUT_WATER_TEMP_dC": bytes([0x0D, 0x8F, 0x00]),
        "OUTPUT_WATER_TEMP_dC": bytes([0x0D, 0x8F, 0x01]),
        "HELIUM_TEMP_dC": bytes([0x0D, 0x8F, 0x02]),
        "OIL_TEMP_dC": bytes([0x0D, 0x8F, 0x03]),
        "PRES_HIGH_dPSI": bytes([0xAA, 0x50, 0x00]),
        "PRES_LOW_dPSI": bytes([0xAA, 0x50, 0x00]),
        "AVERAGE_PRES_LOW_dPSI": bytes([0xBB, 0x94, 0x00]),
        "AVERAGE_PRES_HIGH_dPSI": bytes([0x7E, 0x90, 0x00]),
        "AVERAGE_PRES_DELTA_dPSI": bytes([0x31, 0x9C, 0x00]),
        "AVERAGE_BOUNCE_dPSI": bytes([0x66, 0xFA, 0x00]),
        "STATE": bytes([0x5F, 0x95, 0x00]),
    }
    ESCAPE_SEQ = {0x02: 0x30, 0x0D: 0x31, 0x07: 0x32}
    UNESCAPE_SEQ = {v: k for k, v in ESCAPE_SEQ.items()}
    HOST_ADDR = 0x80
    CMD_READ = 0x63
    CMD_WRITE = 0x61
    COMMAND_STRUCT = struct.Struct(">BBB3sB")
    RESULT_STRUCT = struct.Struct(">BBB3siB")

    def __init__(
        self,
        handle: visa.resources.MessageBasedResource,
        address: int,
        baud_rate: Optional[int] = None,
    ):
        self.handle = handle
        self.address = address
        self.seq = 0x10

        # Set communication params.
        handle.write_termination = ""
        handle.read_termination = "\r"
        if isinstance(handle, visa.resources.SerialInstrument) and baud_rate is not None:
            handle.baud_rate = baud_rate

    @staticmethod
    def checksum(b):
        x = sum(b) & 0xFF
        return ((x >> 4) + 0x40) << 8 | ((x & 0x0F) + 0x40)

    @staticmethod
    def escape(by):
        escaped_bytes = bytearray()
        for b in by:
            if b in CryomechV1.ESCAPE_SEQ:
                escaped_bytes.extend((0x07, CryomechV1.ESCAPE_SEQ[b]))
            else:
                escaped_bytes.append(b)
        return escaped_bytes

    @staticmethod
    def unescape(by):
        unescaped_bytes = bytearray()
        i = iter(by)
        for b in i:
            if b == 0x07:
                unescaped_bytes.append(CryomechV1.UNESCAPE_SEQ[next(i)])
            else:
                unescaped_bytes.append(b)
        return unescaped_bytes

    @staticmethod
    def construct_packet(command):
        escaped = CryomechV1.escape(command)
        return struct.pack(
            f">B{len(escaped)}sHB",
            0x02,  # Header
            escaped,
            CryomechV1.checksum(command),
            0x0D,  # EOL
        )

    @staticmethod
    def parse_packet(by):
        if not by:
            raise ValueError("No response from compressor")
        data_len = len(by) - 4
        header, data, chk, EOL = struct.unpack(f">B{data_len}sHB", by)
        if header != 0x02 or EOL != 0x0D:
            raise ValueError("Malformed packet")
        data = CryomechV1.unescape(data)
        verify = CryomechV1.checksum(data)
        if chk != verify:
            raise ValueError(f"Checksum verification failed. {chk:04x} != {verify:04x}")
        return data

    def query(self, command: bytes):
        """
        Query a value from the compressor
        """
        command = self.COMMAND_STRUCT.pack(
            self.address,  # Compressor Address
            self.HOST_ADDR,  # Host address? Must be 0x80
            self.CMD_READ,  # Command
            command,  # register Address
            self.seq,  # S/N (0x10 - 0xFF)
        )
        b = self.construct_packet(command)

        # Send value to compressor and read result
        self.handle.write_raw(b)
        raw_packet = self.handle.read_raw()
        data = self.parse_packet(raw_packet)
        res = self.RESULT_STRUCT.unpack(data)

        # Check that the result matches the query
        if self.seq != res[5]:
            raise ValueError(
                f"Comms out of sync. Sequence numbers don't match ({self.seq} != {res[5]})."
            )

        # Increment sequence number
        self.seq += 1
        if self.seq > 0xFF:
            self.seq = 0x10

        # Return result
        return res[4]

    @property
    def state(self):
        return bool(self.query(self.CPA_PARAMETERS["STATE"]))

    @property
    def run_time(self):
        return self.query(self.CPA_PARAMETERS["RUNTIME"]) / 60

    @property
    def motor_current(self) -> float:
        return self.query(self.CPA_PARAMETERS["MOTOR_CURRENT"])

    @property
    def input_water_temp(self):
        return 0.1 * self.query(self.CPA_PARAMETERS["INPUT_WATER_TEMP_dC"])

    @property
    def output_water_temp(self) -> float:
        return 0.1 * self.query(self.CPA_PARAMETERS["OUTPUT_WATER_TEMP_dC"])

    @property
    def oil_temp(self) -> float:
        return 0.1 * self.query(self.CPA_PARAMETERS["OIL_TEMP_dC"])

    @property
    def helium_temp(self) -> float:
        return 0.1 * self.query(self.CPA_PARAMETERS["HELIUM_TEMP_dC"])

    @property
    def high_pressure(self) -> float:
        return 0.1 * self.query(self.CPA_PARAMETERS["PRES_HIGH_dPSI"])

    @property
    def low_pressure(self) -> float:
        return 0.1 * self.query(self.CPA_PARAMETERS["PRES_LOW_dPSI"])

    @property
    def average_high_pressure(self) -> float:
        return 0.1 * self.query(self.CPA_PARAMETERS["AVERAGE_PRES_HIGH_dPSI"])

    @property
    def average_low_pressure(self) -> float:
        return 0.1 * self.query(self.CPA_PARAMETERS["AVERAGE_PRES_LOW_dPSI"])

    @property
    def average_delta_pressure(self) -> float:
        return 0.1 * self.query(self.CPA_PARAMETERS["AVERAGE_PRES_DELTA_dPSI"])

    @property
    def bounce(self) -> float:
        return 0.1 * self.query(self.CPA_PARAMETERS["AVERAGE_BOUNCE_dPSI"])


class CryomechMonitor(Uploader[CryomechConfig]):
    def __init__(self, config: CryomechConfig, **kwargs):
        if config.SUPP is not None:
            # If this is a supplementary uploader, add the table name
            kwargs["supp"] = config.SUPP
        super().__init__(config, **kwargs)

        self._instr_conn: Optional[Cryomech] = None
        self.upload_interval = timedelta(seconds=config.UPLOAD_INTERVAL)

        if config.USE_CALCULATED_BOUNCE:
            self.high_bounce: Optional[deque[float]] = deque(maxlen=config.COMPRESSOR_BOUNCE_N)
            self.low_bounce: Optional[deque[float]] = deque(maxlen=config.COMPRESSOR_BOUNCE_N)
        else:
            self.high_bounce = None
            self.low_bounce = None

    @retry(multiplier=1.2, max_wait=15, exception=visa.errors.VisaIOError)
    def open_connection(self) -> Cryomech:
        """
        Try opening a connection to the lakeshore
        """
        rm = visa.ResourceManager()
        handle = rm.open_resource(self.config.ADDRESS)
        if not isinstance(handle, visa.resources.MessageBasedResource):
            raise RuntimeError(
                (
                    "Invalid connection to Cryomech. Can't query instrument. "
                    f"Check the instrument address: {self.config.ADDRESS}"
                )
            )
        if self.config.COMPRESSOR_VERSION == "v1":
            cryomech = CryomechV1(handle, self.config.COMPRESSOR_ADDRESS, self.config.BAUD_RATE)
        else:
            raise RuntimeError(f"Invalid cryomech version. Got {self.config.COMPRESSOR_VERSION}")

        # Check response
        logger.info("Connected to Compressor. Total runtime: %.1f h", cryomech.run_time)

        return cryomech

    async def poll(self):
        """
        Upload if the appropriate interval has passed

        Returns true if a new value is read or data is uploaded, otherwise false.
        """
        # If we aren't connected to the lakeshore, try opening the connection
        if self._instr_conn is None:
            self._instr_conn = self.open_connection()

            if self.low_bounce is not None and self.high_bounce is not None:
                self.low_bounce.clear()
                self.high_bounce.clear()

        try:
            if (datetime.now().astimezone() - self.latest) > self.upload_interval:
                data = {}
                # Pull all parameters from the compressor
                for field, param_name in CPA_FIELD_MAP.items():
                    data[field] = getattr(self._instr_conn, param_name)

                # Check if we want to manually calculate bounce
                if self.low_bounce is not None and self.high_bounce is not None:
                    self.low_bounce.append(self._instr_conn.low_pressure)
                    self.high_bounce.append(self._instr_conn.high_pressure)

                    low_bounce = hilbert_amplitude(self.low_bounce)
                    high_bounce = hilbert_amplitude(self.high_bounce)
                    data["Bounce"] = (low_bounce + high_bounce) / 2

                # And upload the data
                await self.upload(data)
                return True
        except (RuntimeError, ValueError, visa.errors.VisaIOError) as e:
            logger.error("Communication with cryomech failed. Will try to reconnect...", exc_info=e)
            self._instr_conn = None

        return False
