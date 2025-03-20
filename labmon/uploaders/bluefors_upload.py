from logging import getLogger
from pathlib import Path

from ..config import config
from .bluefors_cp import BlueForsCompressorMonitor
from .bluefors_mg import BlueForsMaxiGaugeMonitor
from .bluefors_tc import BlueForsTempMonitor
from .uploader import Uploader

logger = getLogger(__name__)


class BlueForsMonitor(Uploader):
    def __init__(self, *args, **kwargs):
        # Initialize
        super().__init__(*args, **kwargs)

        self.monitor: list[Uploader] = []

        # Check if log directory exists otherwise throw an error
        log_dir = Path(config.UPLOAD.BLUEFORS_CONFIG.LOG_DIR)
        if not log_dir.exists():
            logger.error("Log directory %s doesn't exist.", str(log_dir))
            raise RuntimeError(f"Log directory {log_dir} doesn't exist")
        if not log_dir.is_dir():
            logger.error("Log directory %s is not a directory.", str(log_dir))
            raise RuntimeError(f"Log directory {log_dir} must be a directory")

        # Enable temperature monitoring
        self.monitor.append(BlueForsTempMonitor(*args, **kwargs))

        # Check if compressor monitoring is enabled and how many there are
        if config.UPLOAD.BLUEFORS_CONFIG.UPLOAD_COMPRESSORS:
            num_comp = config.UPLOAD.BLUEFORS_CONFIG.NUM_COMPRESSORS
            if num_comp > 1:
                for i in range(1, num_comp + 1):
                    self.monitor.append(
                        BlueForsCompressorMonitor(*args, compressor_num=i, **kwargs)
                    )
            else:
                self.monitor.append(BlueForsCompressorMonitor(*args, **kwargs))

        # Check if maxigauge monitoring is enabled
        if config.UPLOAD.BLUEFORS_CONFIG.UPLOAD_MAXIGAUGE:
            self.monitor.append(BlueForsMaxiGaugeMonitor(*args, **kwargs))

    async def poll(self):
        """
        Check each of the monitors to see if they have any data
        """
        uploaded = False
        for monitor in self.monitor:
            uploaded |= await monitor.poll()
        return uploaded

    async def upload(self, values):
        """
        Override base upload method, since this is just a collection of
        other uploaders. We should never call this method on this class.
        """
        raise NotImplementedError("Upload not implemented on BlueForsUploader")
