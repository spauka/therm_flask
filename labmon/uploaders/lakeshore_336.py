import logging
from datetime import datetime, timedelta
from typing import Optional

import pyvisa as visa

from ..utility.retry import retry
from ..config import Lakeshore336Config
from .uploader import Uploader

logger = logging.getLogger(__name__)


class Lakeshore336Monitor(Uploader[Lakeshore336Config]):
    def __init__(self, config: Lakeshore336Config, **kwargs):
        super().__init__(config, **kwargs)

        self._instr_conn: Optional[visa.resources.MessageBasedResource] = None
        self.upload_interval = timedelta(seconds=config.UPLOAD_INTERVAL)

    @retry(multiplier=1.2, max_wait=15, exception=(RuntimeError, visa.errors.VisaIOError))
    def open_connection(self) -> visa.resources.MessageBasedResource:
        """
        Try opening a connection to the lakeshore
        """
        rm = visa.ResourceManager()
        t336 = rm.open_resource(self.config.ADDRESS)
        if not isinstance(t336, visa.resources.MessageBasedResource):
            raise RuntimeError(
                (
                    "Invalid connection to Lakeshore. Can't query instrument. "
                    f"Check the instrument address: {self.config.ADDRESS}"
                )
            )
        t336.write_termination = "\n"
        t336.read_termination = "\r\n"

        # Check response
        resp = t336.query("*IDN?")
        logger.info("Connected to Lakeshore: %s", resp)

        return t336

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
                for channel, sensor in self.config.SENSORS.items():
                    sensor_value = ""
                    try:
                        sensor_value = self._instr_conn.query(f"KRDG? {channel}").strip(";")
                        data[sensor] = float(sensor_value)
                        if self.config.UPLOAD_MILLIKELVIN:
                            data[sensor] *= 1000
                    except ValueError:
                        logger.warning(
                            "Failed to parse value for sensor %s: %s", sensor, sensor_value
                        )
                await self.upload(data)
                return True
        except visa.errors.VisaIOError as e:
            logger.error(
                "Communication with lakeshore failed. Will try to reconnect...", exc_info=e
            )
            self._instr_conn = None

        return False
