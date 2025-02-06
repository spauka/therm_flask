import logging
import re
from datetime import datetime
from io import FileIO
from pathlib import Path
from typing import Optional, TypeAlias

from ..config import config
from .upload import Uploader

LOG_DIR = Path(config.UPLOAD.BLUEFORS_CONFIG.LOG_DIR)
FOLDER_PATTERN = re.compile(r"([0-9]{2})-([0-9]{2})-([0-9]{2})")
DATE_FORMAT = "%d-%m-%y %H:%M:%S"

logger = logging.getLogger(__name__)

RawLogFileReading: TypeAlias = tuple[datetime, str]


class BlueForsLogFile:
    def __init__(self, filename):
        logger.debug("Opening sensor file %s", filename)
        self.filename = filename
        self._fhandle = None
        self._peek = None

    @property
    def fhandle(self) -> Optional[FileIO]:
        if self._fhandle is None:
            try:
                self._fhandle = open(self.filename, "r", encoding="utf-8")
            except FileNotFoundError:
                logger.warning(
                    "Sensor file %s not found. May not exist yet. Will try again later.",
                    self.filename,
                )
        return self._fhandle

    def return_next(self) -> Optional[RawLogFileReading]:
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

    def peek_next(self) -> Optional[RawLogFileReading]:
        """
        Return the next sensor reading but do not advance
        """
        if self._peek:
            return self._peek

        if self.fhandle is not None:
            next_line = self.fhandle.readline()
            if next_line:
                date, time, value = next_line.split(",", maxsplit=2)
                time = datetime.strptime(f"{date} {time}", DATE_FORMAT).astimezone()
                self._peek = (time, value)
                return self._peek
        return None


class BlueForsSensorMonitor(Uploader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def latest_folder(self):
        """
        Find the latest folder in the BF logs directory
        """
        # As a shortcut, check if the folder exists for today
        today = datetime.now().strftime("%y-%m-%d")
        today_dir = LOG_DIR / today
        if today_dir.exists():
            return today_dir

        # Get a list of directories in the log path that match the date format
        newest = max(
            (
                (m.groups(), d)
                for d in LOG_DIR.iterdir()
                if d.is_dir() and (m := FOLDER_PATTERN.match(d.name))
            )
        )
        # Return the newest
        return newest[1]

    def poll(self):
        """
        Check log files for new data.

        Returns true if a new value is read or data is uploaded, otherwise false.
        """
        raise NotImplementedError("Subclasses must define their own poll method.")
