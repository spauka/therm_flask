import dataclasses
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, TypeAlias

from ..config import config
from .bluefors_common import BlueForsLogFile, BlueForsSensorMonitor

MAX_AGE = timedelta(seconds=config.UPLOAD.BLUEFORS_CONFIG.MAX_AGE)
FILE_PATTERN = "CH{n} T {date}.log"

logger = logging.getLogger(__name__)


TempSensorReading: TypeAlias = tuple[datetime, float]


@dataclasses.dataclass
class SensorReading:
    value: Optional[float]
    last_read: datetime
    uploaded: bool

    def is_stale(self):
        return (datetime.now().astimezone() - self.last_read) > MAX_AGE


class BlueForsTempLogFile(BlueForsLogFile):
    def return_next(self) -> Optional[TempSensorReading]:
        """
        Return next sensor reading.
        """
        if not self._peek:
            self.peek_next()
        next_val = self._peek
        self._peek = None
        return next_val

    def peek_next(self) -> Optional[TempSensorReading]:
        """
        Return the next sensor reading but do not advance. Convert to sensor reading
        """
        if self._peek:
            return self._peek

        result = super().peek_next()
        if result:
            self._peek = result[0], float(result[1])
        return self._peek


class BlueForsTempMonitor(BlueForsSensorMonitor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load sensors
        self._sensors = config.UPLOAD.BLUEFORS_CONFIG.SENSORS
        self._values = {}
        for sensor in self._sensors:
            self._values[sensor] = SensorReading(
                None, datetime.fromtimestamp(0).replace(tzinfo=timezone.utc), True
            )

        # Find the latest folder and open each file
        self.cwd = self.latest_folder()
        self._sensor_files: dict[str, BlueForsTempLogFile] = {}
        for sensor in self._sensors:
            fname = FILE_PATTERN.format(n=self._sensors[sensor], date=self.cwd.name)
            self._sensor_files[sensor] = BlueForsTempLogFile(self.cwd / fname)

    def poll(self):
        """
        Check log files for new data.

        Returns true if a new value is read or data is uploaded, otherwise false.
        """
        # Get a sorted list of new values for each sensor
        try:
            next_value: Optional[tuple[TempSensorReading, str]] = min(
                (
                    (value, sensor)
                    for sensor in self._sensors
                    if (value := self._sensor_files[sensor].peek_next())
                )
            )
        except ValueError:
            next_value = None

        # Check if there are any new values
        if next_value:
            (time, value), sensor = next_value
            logger.debug("Read next value for sensor %s at %s: %.2f", sensor, time, value)
            # Advance the file
            self._sensor_files[sensor].return_next()

            # Check if we actually have a new reading. If it is, we return true since the file
            # was advanced, but don't update the time/value
            if self._values[sensor].value == value:
                return True

            # Check if the sensor already has a new value in it. If so, then upload
            # those values
            if not self._values[sensor].uploaded:
                self.upload()

            # Store the new reading. If it's reading is older than the latest in the database,
            # we set uploaded true
            self._values[sensor] = SensorReading(
                value=value, last_read=time, uploaded=time < self.latest
            )
            return True

        # If there are any sensor values that haven't been uploaded but are going stale,
        # then upload them here
        if any(sensor.is_stale() and not sensor.uploaded for sensor in self._values.values()):
            logger.warning("Uploading data due to staleness. Is there new data flowing?")
            self.upload()
            return True

        # If we're at the end of all files, double check that we shouldn't move to a new folder
        # There's no point checking if we're already on the directory corresponding to today
        today = datetime.now().strftime("%y-%m-%d")
        if self.cwd.name != today:
            latest_folder = self.latest_folder()
            # The latest folder is the same as the current folder. Nothing newer
            if self.cwd == latest_folder:
                return False

            # We've found a new folder
            logger.info("Advancing log folder to: %s", str(latest_folder))
            self.cwd = latest_folder
            for sensor in self._sensors:
                fname = FILE_PATTERN.format(n=self._sensors[sensor], date=self.cwd.name)
                self._sensor_files[sensor] = BlueForsTempLogFile(self.cwd / fname)
            return True

        # End of all files, and nothing new
        return False

    def upload(self, values=None):
        """
        Upload data and mark all sensor values as uploaded
        """
        # And upload all values, taking the time from the OLDEST not-uploaded sensor reading
        upload_values = {
            sensor: value.value
            for sensor, value in self._values.items()
            if value.uploaded is False or value.is_stale() is False
        }
        upload_values["time"] = min(
            value.last_read for value in self._values.values() if value.uploaded is False
        )
        logger.debug(
            "Stale values are: %r", [value for value in self._values.values() if value.is_stale()]
        )
        res = super().upload(upload_values)

        # Update status of all sensors to uploaded
        for sensor, value in self._values.items():
            if not value.uploaded:
                self._values[sensor] = dataclasses.replace(value, **{"uploaded": True})

        return res
