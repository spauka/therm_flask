import asyncio
import argparse
import logging
from datetime import datetime, timedelta
from asyncio import create_task

import httpx

from .config import CONFIG_FILE, config
from .uploaders.uploader import Uploader
from .uploaders.AVS47 import AVS47Monitor
from .uploaders.bluefors_upload import BlueForsMonitor
from .uploaders.lakeshore_336 import Lakeshore336Monitor
from .uploaders.cryomech import CryomechMonitor
from .uploaders.pfeiffer_maxigauge import PfeifferMaxiGaugeMonitor
from .utility.retry import retry
from .utility.logging import set_logging

logger = logging.getLogger(__name__)

UPLOADERS: dict[str, type[Uploader]] = {
    "BlueFors": BlueForsMonitor,
    "Lakeshore336": Lakeshore336Monitor,
    "Cryomech": CryomechMonitor,
    "MaxiGauge": PfeifferMaxiGaugeMonitor,
    "AVS47": AVS47Monitor,
    # "Leiden": LeidenMonitor,
}
VALID_UPLOADERS = list(UPLOADERS.keys())


@retry()
async def schedule_poll(uploader: Uploader):
    """
    Schedule a poll to run every <interval> seconds. In order to ensure that
    two poll's don't run over the top of each other, we don't schedule the next
    iteration until the first is complete, and calculate the correct interval.
    """
    interval = timedelta(seconds=uploader.poll_interval)
    logger.debug(
        "Setting up uploader %s with interval %.2f s",
        uploader.__class__.__name__,
        interval.total_seconds(),
    )
    next_time: datetime = datetime.now()

    try:
        while True:
            result = True
            while result:
                next_time = datetime.now() + interval
                logger.debug(
                    "Polling %s at time %s", uploader.__class__.__name__, datetime.now().isoformat()
                )
                result = await uploader.poll()
                logger.debug("Poll result for %s was %r.", uploader.__class__.__name__, result)
                # Allow other uploaders to run if necessary
                await asyncio.sleep(0)

            # Check if we need to sleep before the next poll, and sleep until we're ready for
            # the next poll
            next_interval = next_time - datetime.now()
            if next_interval.total_seconds() < 0:
                logger.warning(
                    "Polling %s faster than it can run. The next poll is running %f seconds slow.",
                    uploader.__class__.__name__,
                    next_interval.seconds,
                )
                continue
            await asyncio.sleep(next_interval.total_seconds())

    except asyncio.CancelledError:
        logger.warning("Shutting down uploader: %s", uploader.__class__.__name__)


async def main():
    """
    Create uploaders and schedule them all to run.
    """
    # Create a httpx client
    client = httpx.AsyncClient(http2=True)

    # Create all the uploaders
    create_uploaders: list[asyncio.Task] = []
    for uploader in config.UPLOAD.ENABLED_UPLOADERS:
        if uploader.ENABLED is False:
            logger.debug("Skipping disabled uploader: %s", uploader.TYPE)
            continue

        if uploader.TYPE in UPLOADERS:
            uploader_type = UPLOADERS[uploader.TYPE]
            create_uploaders.append(
                create_task(uploader_type.create_uploader(uploader, client=client))
            )
        else:
            raise KeyError(
                (
                    f"Invalid uploader {uploader.TYPE} specified. "
                    f"Valid uploaders are: {', '.join(VALID_UPLOADERS)}"
                )
            )

    uploaders: list[Uploader] = await asyncio.gather(*create_uploaders)

    # Create polls
    poll_tasks: list[asyncio.Task] = []
    for uploader_inst in uploaders:
        poll_tasks.append(create_task(schedule_poll(uploader_inst)))

    # Create infinite loop
    while True:
        await asyncio.sleep(20)


if __name__ == "__main__":
    # If we are here - override the name of the default logger
    logger = logging.getLogger("labmon.upload")

    # Parse command line arguments
    cmd_args = argparse.ArgumentParser("LabMon Monitoring Upload Script")
    cmd_args.add_argument("-v", "--verbose", action="store", default=".")
    args = cmd_args.parse_args(namespace=argparse.Namespace(verbose=None))

    if args.verbose is not None:
        if args.verbose == ".":
            # Set log level debug on labmon
            set_logging(logging.DEBUG)
        else:
            set_logging(logging.DEBUG, args.verbose)

    # Check that uploading is enabled
    if not config.UPLOAD.ENABLED:
        raise RuntimeError(
            (
                "Uploading not enabled in config file. Please enable and try again. "
                f"The config file can be found at {CONFIG_FILE}."
            )
        )

    # Check that fridge is filled in
    if config.UPLOAD.FRIDGE == "?":
        raise RuntimeError(
            (
                "Fridge is not set in config file. "
                "Please set the name of the fridge and try again. "
                "The config file can be found at {CONFIG_FILE}."
            )
        )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        logger.warning("Ended all tasks. Exiting...")
