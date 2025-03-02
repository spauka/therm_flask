import logging
from collections import deque
from datetime import datetime
from typing import Optional

from ..config import config
from ..utility.hilbert import hilbert_amplitude
from .bluefors_common import BlueForsMapLogFile, BlueForsSensorMonitor

FILE_PATTERN = "Status_{date}.log"
CPA_FIELD_MAP = {
    "Low": "cpalpa",
    "High": "cpahpa",
    "Delta": "cpadp",
    "WaterIn": "cpatempwi",
    "WaterOut": "cpatempwo",
    "Oil": "cpatempo",
    "Helium": "cpatemph",
    "Current": "cpacurrent",
}
CPA_BOUNCE_MAP = {"Low": "cpalp", "High": "cpahp"}

logger = logging.getLogger(__name__)


class BlueForsCompressorMonitor(BlueForsSensorMonitor):
    def __init__(self, *args, compressor_num: Optional[int] = None, **kwargs):
        # Derive the name of the supplementary sensor if not explicitly overriden
        if "supp" not in kwargs:
            if compressor_num is None:
                kwargs["supp"] = "Compressor"
            else:
                kwargs["supp"] = f"Compressor_{compressor_num}"

        super().__init__(*args, **kwargs)

        # Save the compressor number
        self.compressor_num = compressor_num

        # Derive the field names

        if compressor_num is not None and compressor_num > 1:
            self._cpa_field_map = {}
            self._cpa_bounce_map = {}
            for site_field, log_field in CPA_FIELD_MAP.items():
                self._cpa_field_map[site_field] = f"{log_field}_{compressor_num}"
            for site_field, log_field in CPA_BOUNCE_MAP.items():
                self._cpa_bounce_map[site_field] = f"{log_field}_{compressor_num}"
        else:
            self._cpa_field_map = CPA_FIELD_MAP
            self._cpa_bounce_map = CPA_BOUNCE_MAP

        # Create a list of previous pressures for calculating the bounce
        self.high_bounce = deque(maxlen=config.UPLOAD.BLUEFORS_CONFIG.COMPRESSOR_BOUNCE_N)
        self.low_bounce = deque(maxlen=config.UPLOAD.BLUEFORS_CONFIG.COMPRESSOR_BOUNCE_N)

        # Find the latest folder and open the status file
        self.cwd = self.latest_folder()
        self._fname = FILE_PATTERN.format(date=self.cwd.name)
        self._status_log: BlueForsMapLogFile = BlueForsMapLogFile(self.cwd / self._fname)

    def bounce(self, lp, hp) -> Optional[float]:
        self.low_bounce.append(lp)
        self.high_bounce.append(hp)

        if len(self.low_bounce) == config.UPLOAD.BLUEFORS_CONFIG.COMPRESSOR_BOUNCE_N:
            low_bounce = hilbert_amplitude(self.low_bounce)
            high_bounce = hilbert_amplitude(self.high_bounce)
            return (low_bounce + high_bounce) / 2
        return None

    def poll(self):
        """
        Check log files for new data.

        Returns true if a new value is read or data is uploaded, otherwise false.
        """
        # Check if there is a new sensor reading
        next_val = self._status_log.return_next()
        if next_val:
            time, next_val = next_val

            # Check if the dataset is old, if it is, don't upload
            if time < self.latest:
                return True

            # Map values into a dictionary
            values = {}
            values["time"] = time
            missing_fields = []
            for name, map_name in self._cpa_field_map.items():
                try:
                    values[name] = next_val[map_name]
                except KeyError:
                    # If the field isn't found we just won't upload it
                    missing_fields.append(name)
            if missing_fields:
                logger.warning(
                    "Failed to read sensors %r from compressor %s.", missing_fields, self.supp
                )

            # Add an estimate of bounce
            try:
                bounce = self.bounce(
                    *[next_val[map_name] for map_name in self._cpa_bounce_map.values()]
                )
                if bounce:
                    values["Bounce"] = bounce
            except KeyError:
                # Similarly if we weren't able to extract a value for the bounce, ignore it
                logger.warning("Failed to calculate bounce for compressor %s.", self.supp)

            self.upload(values)
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
            self._status_log = BlueForsMapLogFile(self.cwd / self._fname)
            return True

        # End of all files, and nothing new
        return False
