import argparse
import logging
import time
from collections import deque

import httpx

from .config import CONFIG_FILE, config
from .uploaders.bluefors_upload import BlueForsMonitor
from .uploaders.lakeshore_336 import Lakeshore336Monitor
from .uploaders.cryomech import CryomechMonitor
from .utility.logging import set_logging

logger = logging.getLogger(__name__)

UPLOADERS = {
    "BlueFors": BlueForsMonitor,
    "Lakeshore336": Lakeshore336Monitor,
    "Cryomech": CryomechMonitor,
    # "Leiden": LeidenMonitor,
}

if __name__ == "__main__":
    cmd_args = argparse.ArgumentParser("LabMon Monitoring Upload Script")
    cmd_args.add_argument("-v", "--verbose", action="store_true")
    args = cmd_args.parse_args()

    if args.verbose:
        set_logging(logging.DEBUG)

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

    # Create a shared httpx client
    client = httpx.Client(http2=True)

    # Check which loggers are configured
    uploaders = []
    for uploader in config.UPLOAD.ENABLED_UPLOADERS:
        uploaders.append(UPLOADERS[uploader](client=client))

    # And start a poll
    try:
        while True:
            to_poll = deque(range(len(uploaders)))
            while to_poll:
                next_poll = to_poll.popleft()
                if uploaders[next_poll].poll():
                    to_poll.append(next_poll)

            # Wait 1 second then see if there is more data
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("Exiting")
        client.close()
