import logging
from datetime import datetime, timedelta
from typing import Optional
from enum import IntEnum

import pyvisa as visa

from ..utility.retry import retry
from ..config import config
from .uploader import Uploader

logger = logging.getLogger(__name__)

ACK = 0x06
NAK = 0x15
ENQ = 0x05


class SensorStatus(IntEnum):
    OK = 0
    UNDERRANGE = 1
    OVERRANGE = 2
    SENS_ERROR = 3
    SENS_OFF = 4
    SENS_NONE = 5
    SENS_UNIDENT = 6


class PfeifferMaxiGaugeMonitor(Uploader):
    def __init__(self, *args, **kwargs):
        if config.UPLOAD.MAXIGAUGE_CONFIG.SUPP is not None:
            # If this is a supplementary uploader, add the table name
            kwargs["supp"] = config.UPLOAD.MAXIGAUGE_CONFIG.SUPP
        super().__init__(*args, **kwargs)

        self._instr_conn: Optional[visa.resources.MessageBasedResource] = None
        self.upload_interval = timedelta(seconds=config.UPLOAD.MAXIGAUGE_CONFIG.UPLOAD_INTERVAL)

    def query(self, query: str, handle: Optional[visa.resources.MessageBasedResource] = None):
        """
        Query value from MaxiGauge
        """
        if handle is None and self._instr_conn is None:
            raise RuntimeError("Unable to query instrument: Not connected.")
        elif handle is None:
            assert self._instr_conn is not None
            handle = self._instr_conn

        # Send query and check for acknowledgement
        handle.write(query)
        ack = handle.read_bytes(3, break_on_termchar=True)
        if ack[0] == NAK:
            raise RuntimeError(f"Query error. Invalid query: {query}.")
        handle.write_raw(bytes((ENQ,)))
        resp = handle.read()
        return resp

    @retry(multiplier=1.2, max_wait=15, exception=(RuntimeError, visa.errors.VisaIOError))
    def open_connection(self) -> visa.resources.MessageBasedResource:
        """
        Try opening a connection to the MaxiGauge
        """
        rm = visa.ResourceManager()
        maxigauge = rm.open_resource(config.UPLOAD.MAXIGAUGE_CONFIG.ADDRESS)
        if not isinstance(maxigauge, visa.resources.MessageBasedResource):
            raise RuntimeError(
                (
                    "Invalid connection to Maxigauge. Can't query instrument. "
                    f"Check the instrument address: {config.UPLOAD.MAXIGAUGE_CONFIG.ADDRESS}"
                )
            )

        # Set baud rate if given
        if (
            isinstance(maxigauge, visa.resources.SerialInstrument)
            and config.UPLOAD.MAXIGAUGE_CONFIG.BAUD_RATE is not None
        ):
            maxigauge.baud_rate = config.UPLOAD.MAXIGAUGE_CONFIG.BAUD_RATE

        maxigauge.write_termination = "\r"
        maxigauge.read_termination = "\r\n"

        # Check response
        sensors = self.query("CID", maxigauge)
        logger.info("Connected to MaxiGauge. Sensors are: %s", sensors)

        return maxigauge

    def poll(self):
        """
        Upload if the appropriate interval has passed

        Returns true if a new value is read or data is uploaded, otherwise false.
        """
        # If we aren't connected to the MaxiGauge, try opening the connection
        if self._instr_conn is None:
            self._instr_conn = self.open_connection()

        try:
            if (datetime.now().astimezone() - self.latest) > self.upload_interval:
                # We're ready to upload the next dataset
                data = {}
                for channel, sensor in config.UPLOAD.MAXIGAUGE_CONFIG.SENSORS.items():
                    sensor_value = ""
                    try:
                        sensor_value = self.query(f"PR{channel}")
                        status_str, value = sensor_value.split(",")
                        status = SensorStatus(int(status_str))
                        if status is SensorStatus.OK:
                            data[sensor] = float(value)
                        elif status is SensorStatus.SENS_ERROR:
                            logger.warning("Sensor %s has an error.", sensor)
                    except ValueError:
                        logger.warning(
                            "Failed to parse value for sensor %s: %s", sensor, sensor_value
                        )
                self.upload(data)
                return True
        except visa.errors.VisaIOError as e:
            logger.error(
                "Communication with MaxiGauge failed. Will try to reconnect...", exc_info=e
            )
            self._instr_conn = None

        return False
