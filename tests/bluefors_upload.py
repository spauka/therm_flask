from datetime import datetime, timedelta, timezone
from pprint import pprint

from labmon.uploaders.bluefors_cp import BlueForsCompressorMonitor
from labmon.uploaders.bluefors_tc import BlueForsTempMonitor
from labmon.utility.logging import logging, set_logging

if __name__ == "__main__":
    set_logging(logging.DEBUG)
    fs = BlueForsTempMonitor()
    cp = BlueForsCompressorMonitor(supp="Compressor")

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
    cp.latest = fs.latest

    # Go through all the datasets
    poll = True
    while poll:
        poll = cp.poll()
