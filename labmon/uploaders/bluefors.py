from datetime import datetime, timedelta, timezone
from pprint import pprint

from ..utility.logging import logging, set_logging
from .bluefors_tc import BlueForsTempMonitor

if __name__ == "__main__":
    set_logging(logging.DEBUG)
    fs = BlueForsTempMonitor()

    # For debugging purposes, set the latest time to some value in our dataset
    fs.latest = datetime(
        2025,
        2,
        5,
        22,
        0,
        0,
        tzinfo=timezone(timedelta(seconds=39600)),
    )

    # Go through all the datasets
    poll = True
    while poll:
        poll = fs.poll()
