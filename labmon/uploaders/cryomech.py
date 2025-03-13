import logging
from datetime import datetime, timedelta
from typing import Optional
import struct

import pyvisa as visa

from ..utility.retry import retry
from ..config import config
from .uploader import Uploader

logger = logging.getLogger(__name__)


class Cryomech:
    @property
    def run_time(self):
        raise NotImplementedError()

    @property
    def input_water_temp(self):
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
    RESULT_STRUCT = struct.Struct(">BBB3sIB")

    def __init__(self, handle: visa.resources.MessageBasedResource, address: int):
        self.handle = handle
        self.address = address
        self.seq = 0x10

        # Set communication params.
        handle.write_termination = ""
        handle.read_termination = "\r"
        if (
            isinstance(handle, visa.resources.SerialInstrument)
            and config.UPLOAD.CRYOMECH_CONFIG.BAUD_RATE is not None
        ):
            handle.baud_rate = config.UPLOAD.CRYOMECH_CONFIG.BAUD_RATE

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
    def run_time(self):
        return self.query(self.CPA_PARAMETERS["RUNTIME"]) / 60

    @property
    def input_water_temp(self):
        return 0.1 * self.query(self.CPA_PARAMETERS["INPUT_WATER_TEMP_dC"])


class CryomechMonitor(Uploader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._instr_conn: Optional[Cryomech] = None
        self.upload_interval = timedelta(seconds=config.UPLOAD.LAKESHORE_CONFIG.UPLOAD_INTERVAL)

    @retry(multiplier=1.2, max_wait=15, exception=visa.errors.VisaIOError)
    def open_connection(self) -> Cryomech:
        """
        Try opening a connection to the lakeshore
        """
        rm = visa.ResourceManager()
        handle = rm.open_resource(config.UPLOAD.CRYOMECH_CONFIG.ADDRESS)
        if not isinstance(handle, visa.resources.MessageBasedResource):
            raise RuntimeError(
                (
                    "Invalid connection to Cryomech. Can't query instrument. "
                    f"Check the instrument address: {config.UPLOAD.LAKESHORE_CONFIG.ADDRESS}"
                )
            )
        if config.UPLOAD.CRYOMECH_CONFIG.COMPRESSOR_VERSION == "v1":
            cryomech = CryomechV1(handle, config.UPLOAD.CRYOMECH_CONFIG.COMPRESSOR_ADDRESS)
        else:
            raise RuntimeError(
                f"Invalid cryomech version. Got {config.UPLOAD.CRYOMECH_CONFIG.COMPRESSOR_VERSION}"
            )

        # Check response
        logger.info("Connected to Compressor. Total runtime: ", cryomech.run_time)

        return cryomech

    def poll(self):
        """
        Upload if the appropriate interval has passed

        Returns true if a new value is read or data is uploaded, otherwise false.
        """
        # If we aren't connected to the lakeshore, try opening the connection
        if self._instr_conn is None:
            self._instr_conn = self.open_connection()

        try:
            if (datetime.now().astimezone() - self.latest) > self.upload_interval:
                logger.warning("Water temp: %.1f", self._instr_conn.input_water_temp)
                self.latest = datetime.now().astimezone()
                # We're ready to upload the next dataset
                return True
        except (RuntimeError, ValueError, visa.errors.VisaIOError) as e:
            logger.error("Communication with cryomech failed. Will try to reconnect...", exc_info=e)
            self._instr_conn = None

        return False
