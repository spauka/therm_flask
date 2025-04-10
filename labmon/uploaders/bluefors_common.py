import logging
import re
from datetime import datetime, timedelta, timezone
from io import TextIOWrapper
from pathlib import Path
from typing import Optional, TypeAlias, Any

from ..config import BlueForsUploadConfig
from .uploader import Uploader

FOLDER_PATTERN = re.compile(r"([0-9]{2})-([0-9]{2})-([0-9]{2})")
DATE_FORMAT = "%d-%m-%y %H:%M:%S"

logger = logging.getLogger(__name__)

RawLogFileReading: TypeAlias = tuple[datetime, str] | tuple[datetime, Any]
MapLogFileReading: TypeAlias = tuple[datetime, dict[str, float]]


class BlueForsLogFile:
    def __init__(self, filename, log_warning_interval: float = 1800.0):
        logger.debug("Opening sensor file %s", filename)
        self.filename: str = filename
        self.log_warning_interval = timedelta(seconds=log_warning_interval)
        self._fhandle: Optional[TextIOWrapper] = None
        self._peek: Optional[RawLogFileReading] = None
        self._last_warned = datetime.fromtimestamp(0).replace(tzinfo=timezone.utc)

    @property
    def fhandle(self) -> Optional[TextIOWrapper]:
        if self._fhandle is None:
            try:
                self._fhandle = open(self.filename, "r", encoding="utf-8")
                self._last_warned = datetime.fromtimestamp(0).replace(tzinfo=timezone.utc)
            except FileNotFoundError:
                if (datetime.now().astimezone() - self._last_warned) > self.log_warning_interval:
                    logger.warning(
                        "Sensor file %s not found. May not exist yet. Will try again later.",
                        self.filename,
                    )
                    self._last_warned = datetime.now().astimezone()
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
                try:
                    date_str, time_str, value = next_line.split(",", maxsplit=2)
                    time = datetime.strptime(f"{date_str} {time_str}", DATE_FORMAT).astimezone()
                    self._peek = (time, value)
                    return self._peek
                except ValueError:
                    # Incorrectly formatted line
                    logger.error(
                        "Unable to parse line in file %s: %s\nIgnoring line.",
                        self.filename,
                        next_line.strip(),
                    )
                    self._peek = None
        return None


class BlueForsMapLogFile(BlueForsLogFile):
    """
    Extension of BlueForsLogFile for files which return a map of variables.
    """

    def __init__(self, filename, log_warning_interval: float = 1800.0):
        super().__init__(filename, log_warning_interval)
        self._peek: Optional[MapLogFileReading] = None

    def return_next(self) -> Optional[MapLogFileReading]:
        """
        Return next value. Note that this will have been mapped to the right format
        by the peek function.
        """
        if not self._peek:
            self.peek_next()
        next_val = self._peek
        self._peek = None
        return next_val

    def peek_next(self) -> Optional[MapLogFileReading]:
        """
        Return the next value without advancing in the file.
        """
        if self._peek:
            return self._peek

        value = super().peek_next()
        if value:
            time, values = value[0], value[1].split(",")
            # Convert values to a mapping
            mapped_values = {}
            for name, value_str in zip(*[iter(values)] * 2):
                try:
                    mapped_values[name] = float(value_str)
                except ValueError:
                    # If the value is an invalid float, don't map it
                    logger.warning(
                        "Failed to parse sensor %s to a number. Value was %s.", name, value_str
                    )

            self._peek = time, mapped_values  # type: ignore
        return self._peek


class BlueForsSensorMonitor(Uploader[BlueForsUploadConfig]):
    def __init__(
        self,
        config: BlueForsUploadConfig,
        supp=None,
        client=None,
        factory=False,
        **kwargs,
    ):
        super().__init__(config, client=client, supp=supp, factory=factory, **kwargs)

        # Store log dir
        self.log_dir = Path(self.config.LOG_DIR)
        if not self.log_dir.exists():
            raise RuntimeError(f"Bluefors log directory {self.log_dir} not found.")
        if not self.log_dir.is_dir():
            raise RuntimeError(f"Bluefors log directory {self.log_dir} must be a directory.")

    def latest_folder(self):
        """
        Find the latest folder in the BF logs directory
        """
        # As a shortcut, check if the folder exists for today
        today = datetime.now().strftime("%y-%m-%d")
        today_dir = self.log_dir / today
        if today_dir.exists():
            return today_dir

        # Get a list of directories in the log path that match the date format
        newest = max(
            (
                (m.groups(), d)
                for d in self.log_dir.iterdir()
                if d.is_dir() and (m := FOLDER_PATTERN.match(d.name))
            )
        )
        # Return the newest
        return newest[1]

    async def poll(self):
        """
        Check log files for new data.

        Returns true if a new value is read or data is uploaded, otherwise false.
        """
        raise NotImplementedError("Subclasses must define their own poll method.")
