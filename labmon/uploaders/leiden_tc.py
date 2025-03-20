import logging
import re
from datetime import datetime, timedelta
from io import TextIOWrapper
from pathlib import Path
from typing import Optional, TypeAlias

from ..config import config
from .uploader import Uploader

LOG_DIR = Path(config.UPLOAD.LEIDEN_CONFIG.LOG_DIR)
FILE_PATTERN = re.compile(config.UPLOAD.LEIDEN_CONFIG.TC_FILE_PATTERN)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger(__name__)

LeidenLogFileReading: TypeAlias = dict[str, datetime | float]


class LeidenLogFile:
    def __init__(self, filename):
        logger.debug("Opening sensor file %s", filename)
        self.filename = filename
        self._fhandle = None
        self._peek = None

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
                for sensor, column in config.UPLOAD.LEIDEN_CONFIG.SENSORS.items():
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


class LeidenTempMonitor(Uploader):
    logfile: Optional[LeidenLogFile]
    last_check: datetime

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            for filename in LOG_DIR.iterdir()
            if filename.is_file() and (m := FILE_PATTERN.match(str(filename)))
        )
        self.last_check = datetime.now().astimezone()

        if newest_file:
            filename = newest_file[1]
            # Check if the filename is new
            if self.logfile is None or filename != self.logfile.filename:
                self.logfile = LeidenLogFile(filename)
            return filename

        return None

    def poll(self):
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
                self.upload(next_value)
                return True

        # If we're at the end of the file, double check every NEW_LOG_CHECK_INTERVAL that there isn't
        # a new log file
        if (datetime.now().astimezone() - self.last_check) > timedelta(
            seconds=config.UPLOAD.LEIDEN_CONFIG.NEW_LOG_CHECK_INTERVAL
        ):
            if self.find_latest():
                return True
            return False
        # End of all files, and nothing new
        return False
