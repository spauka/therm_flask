import logging
import re
from datetime import datetime, timedelta
from io import TextIOWrapper
from pathlib import Path
from typing import Optional, TypeAlias

from ..config import LeidenUploadConfig
from .uploader import Uploader

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger(__name__)

LeidenLogFileReading: TypeAlias = dict[str, datetime | float]


class LeidenLogFile:
    def __init__(self, filename: str | Path, sensors: dict[str, int]):
        logger.debug("Opening sensor file %s", filename)
        self.sensors = sensors
        self.filename = filename
        self._fhandle: Optional[TextIOWrapper] = None
        self._peek: Optional[LeidenLogFileReading] = None

    @property
    def fhandle(self) -> Optional[TextIOWrapper]:
        if self._fhandle is None:
            try:
                self._fhandle = open(self.filename, "r", encoding="utf-8")
            except FileNotFoundError:
                logger.warning(
                    "Sensor file %s not found. May not exist yet. Will try again later.",
                    self.filename,
                )
        return self._fhandle

    def return_next(self) -> Optional[LeidenLogFileReading]:
        """
        Return next sensor reading.
        """

        # We can reuse the code for peeking if we don't already have the value
        # such that the parsing logic only needs to be implemented once. If
        # there is no next value, then peek is set to None anyway so the behaviour
        # is the same as expected.
        if not self._peek:
            self.peek_next()
        next_val = self._peek
        self._peek = None
        return next_val

    def peek_next(self) -> Optional[LeidenLogFileReading]:
        """
        Return the next sensor reading but do not advance
        """
        if self._peek:
            return self._peek

        if self.fhandle is not None:
            next_line = self.fhandle.readline()
            if next_line:
                values: dict[str, float | datetime] = {}
                date, raw_values = next_line.split("\t")
                values["time"] = datetime.strptime(date, DATE_FORMAT).astimezone()
                for sensor, column in self.sensors.items():
                    try:
                        values[sensor] = float(raw_values[column])
                    except ValueError:
                        logger.warning(
                            ("Unable to parse value for sensor %s. Value was: %s. Leaving blank"),
                            sensor,
                            raw_values[column],
                        )

                self._peek = values
                return self._peek
        # There's no new sensor reading in the log file
        return None


class LeidenTempMonitor(Uploader[LeidenUploadConfig]):
    logfile: Optional[LeidenLogFile]
    last_check: datetime

    def __init__(self, config: LeidenUploadConfig, **kwargs):
        super().__init__(config, **kwargs)

        # Store paths
        self.log_dir = Path(config.LOG_DIR)
        self.file_pattern = re.compile(config.TC_FILE_PATTERN)

        # Find the latest log file and open it
        self.logfile = None
        self.find_latest()

    def find_latest(self) -> Optional[Path]:
        """
        Find the latest log file and open it
        """
        # Iterate through all files in the log directory and open the latest one
        newest_file = max(
            (datetime.strptime(DATE_FORMAT, m.groups()[0]), filename)
            for filename in self.log_dir.iterdir()
            if filename.is_file() and (m := self.file_pattern.match(str(filename)))
        )
        self.last_check = datetime.now().astimezone()

        if newest_file:
            filename = newest_file[1]
            # Check if the filename is new
            if self.logfile is None or filename != self.logfile.filename:
                self.logfile = LeidenLogFile(filename, self.config.SENSORS)
            return filename

        return None

    async def poll(self):
        """
        Check log files for new data.

        Returns true if a new value is read or data is uploaded, otherwise false.
        """
        if self.logfile:
            next_value = self.logfile.return_next()

            # Check if there are any new values
            if next_value:
                # Upload and return true
                logger.debug("Next sensor reading for fridge %s: %r", self.fridge, next_value)
                await self.upload(next_value)
                return True

        # If we're at the end of the file, double check every NEW_LOG_CHECK_INTERVAL
        # that there isn't a new log file
        if (datetime.now().astimezone() - self.last_check) > timedelta(
            seconds=self.config.NEW_LOG_CHECK_INTERVAL
        ):
            if self.find_latest():
                return True
            return False
        # End of all files, and nothing new
        return False
