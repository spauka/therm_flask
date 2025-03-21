from asyncio import Task, create_task, gather
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

    @classmethod
    async def create_uploader(cls, *args, supp=None, client=None, **kwargs):
        new_inst = await super().create_uploader(*args, supp=supp, client=client, **kwargs)

        monitors: list[Task] = []

        # Enable temperature monitoring
        monitors.append(
            create_task(BlueForsTempMonitor.create_uploader(*args, client=client, **kwargs))
        )

        # Check if compressor monitoring is enabled and how many there are
        if config.UPLOAD.BLUEFORS_CONFIG.UPLOAD_COMPRESSORS:
            num_comp = config.UPLOAD.BLUEFORS_CONFIG.NUM_COMPRESSORS
            if num_comp > 1:
                for i in range(1, num_comp + 1):
                    monitors.append(
                        create_task(
                            BlueForsCompressorMonitor.create_uploader(
                                *args, compressor_num=i, client=client, **kwargs
                            )
                        )
                    )
            else:
                monitors.append(
                    create_task(
                        BlueForsCompressorMonitor.create_uploader(*args, client=client, **kwargs)
                    )
                )

        # Check if maxigauge monitoring is enabled
        if config.UPLOAD.BLUEFORS_CONFIG.UPLOAD_MAXIGAUGE:
            monitors.append(
                create_task(
                    BlueForsMaxiGaugeMonitor.create_uploader(*args, client=client, **kwargs)
                )
            )

        # Add all the new monitors to the parent
        new_inst.monitor.extend(await gather(*monitors))

        return new_inst

    async def poll(self):
        """
        Check each of the monitors to see if they have any data
        """
        results: list[Task] = [create_task(monitor.poll()) for monitor in self.monitor]
        return any(await gather(*results))

    async def upload(self, raw_values):
        """
        Override base upload method, since this is just a collection of
        other uploaders. We should never call this method on this class.
        """
        raise NotImplementedError("Upload not implemented on BlueForsUploader")
