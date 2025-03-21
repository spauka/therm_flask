import logging
from datetime import datetime

from .bluefors_common import BlueForsLogFile, BlueForsSensorMonitor

FILE_PATTERN = "maxigauge {date}.log"
GAUGE_MAP = {
    "CH1": "VC",
    "CH2": "PStill",
    "CH3": "Condensing",
    "CH4": "Backing",
    "CH5": "Tank",
    "CH6": "AirBacking",
}

logger = logging.getLogger(__name__)


class BlueForsMaxiGaugeMonitor(BlueForsSensorMonitor):
    def __init__(self, *args, **kwargs):
        # Derive the name of the supplementary sensor if not explicitly overriden
        if "supp" not in kwargs or kwargs["supp"] is None:
            kwargs["supp"] = "MaxiGauge"

        super().__init__(*args, **kwargs)

        # Find the latest folder and open the status file
        self.cwd = self.latest_folder()
        self._fname = FILE_PATTERN.format(date=self.cwd.name)
        self._status_log: BlueForsLogFile = BlueForsLogFile(self.cwd / self._fname)

    async def poll(self):
        """
        Check log files for new data.

        Returns true if a new value is read or data is uploaded, otherwise false.
        """
        # Check if there is a new sensor reading
        next_reading = self._status_log.return_next()
        if next_reading:
            time, next_val = next_reading

            # Check if the dataset is old, if it is, don't upload
            if time < self.latest:
                return True

            # Split up sensors. The maxi gauge file has the following fields
            # channel, display_name, enabled, value, error, ?
            # so we iterate in sixes
            values = {}
            values["time"] = time
            for ch, _disp, enabled, value, err, _unk in zip(*[iter(next_val.split(","))] * 6):
                enabled = int(enabled)
                value = float(value)
                err = int(err)

                if enabled and err == 0:
                    values[GAUGE_MAP[ch]] = value

            # Upload values
            await self.upload(values)
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
            self._fname = FILE_PATTERN.format(date=self.cwd.name)
            self._status_log = BlueForsLogFile(self.cwd / self._fname)
            return True

        # End of all files, and nothing new
        return False
