import logging
from datetime import datetime, timedelta
from typing import Optional
import random

from ..utility.retry import retry
from ..config import SampleUploadConfig
from .uploader import Uploader

logger = logging.getLogger(__name__)


class SampleInstrConn:
    """
    This is a sample instrument connection class. If the uploader is paired
    with an instrument driver, then it can be implemented here
    """

    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name

    def get_value(self, _field: str, min_val: float = 0, max_val: float = 1) -> float:
        assert min_val < max_val
        rand_range = max_val - min_val
        return min_val + (rand_range * random.random())


class SampleMonitor(Uploader[SampleUploadConfig]):
    def __init__(self, config: SampleUploadConfig, **kwargs):
        super().__init__(config, **kwargs)

        self._instr_conn: Optional[SampleInstrConn] = None
        self.upload_interval = timedelta(seconds=config.UPLOAD_INTERVAL)

    @retry(multiplier=1.2, max_wait=15, exception=RuntimeError)
    def open_connection(self) -> SampleInstrConn:
        """
        Try opening a connection to the sample instrument
        """
        instr = SampleInstrConn("Sample_Instrument")
        logger.info("Connected to sample instrument: %s", instr.get_name())
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
                    data[field] = self._instr_conn.get_value(field)
                await self.upload(data)
                return True
        except ValueError as e:
            logger.error("Failed to retrieve value", exc_info=e)
            self._instr_conn = None

        return False
