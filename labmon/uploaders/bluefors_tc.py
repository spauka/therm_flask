import dataclasses
import logging
import re
from datetime import datetime, timedelta
from io import FileIO
from pathlib import Path
from typing import Optional

from ..config import config
from .upload import Uploader

MAX_AGE = timedelta(seconds=config.UPLOAD.BLUEFORS_CONFIG.MAX_AGE)
LOG_DIR = Path(config.UPLOAD.BLUEFORS_CONFIG.LOG_DIR)
FILE_PATTERN = "CH{n} T {date}.log"
FOLDER_PATTERN = re.compile(r"([0-9]{2})-([0-9]{2})-([0-9]{2})")
DATE_FORMAT = "%d-%m-%y %H:%M:%S"

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SensorReading:
    value: Optional[float]
    last_read: datetime
    uploaded: bool

    def is_stale(self):
        return (datetime.now - self.last_read) > MAX_AGE


class BlueForsLogFile:
    def __init__(self, filename):
        logger.debug("Opening sensor file %s", filename)
        self.filename = filename
        self._fhandle = None

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

    def return_next(self) -> Optional[tuple[datetime, float]]:
        """
        Return next sensor reading.
        """
        if self.fhandle is not None:
            next_line = self.fhandle.readline()
            if next_line:
                date, time, value = next_line.split(",")
                time = datetime.strptime(f"{date} {time}", DATE_FORMAT).astimezone()
                return time, float(value)
        return None


class BlueForsTempMonitor(Uploader):
    def __init__(self):
        super().__init__()

        # Load sensors
        self._sensors = config.UPLOAD.BLUEFORS_CONFIG.SENSORS
        self._values = {}
        for sensor in self._sensors:
            self._values[sensor] = SensorReading(None, datetime.now(), True)

        # Find the latest folder and open each file
        self.cwd = self.latest_folder()
        self._sensor_files: dict[str, BlueForsLogFile] = {}
        for sensor in self._sensors:
            fname = FILE_PATTERN.format(n=self._sensors[sensor], date=self.cwd.name)
            self._sensor_files[sensor] = BlueForsLogFile(self.cwd / fname)

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

    def upload(self, _values=None):
        """
        Update status of all sensors to uploaded and upload
        """
        # And upload all values
        super().upload(
            {
                sensor: value.value
                for sensor, value in self._values.items()
                if not value.is_stale()
            }
        )

        # Update status of all sensors to uploaded
        for sensor in self._values:
            self._values[sensor] = dataclasses.replace(
                self._values[sensor], **{"uploaded": True}
            )

    def set_value(self, sensor, value):
        if sensor not in self._values:
            raise KeyError(
                (
                    f"Unknown sensor: {sensor}. "
                    f"Valid sensors are {', '.join(self._sensors)}"
                )
            )

        if not self._values[sensor].uploaded:
            self.upload(self._values)

        self._values[sensor] = dataclasses.replace(
            self._values[sensor], **{sensor: value}
        )
