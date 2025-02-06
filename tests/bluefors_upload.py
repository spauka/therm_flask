from datetime import datetime, timedelta, timezone
from pprint import pprint

from labmon.uploaders.bluefors_upload import BlueForsMonitor

if __name__ == "__main__":
    fs = BlueForsMonitor()

    # For debugging purposes, set the latest time to some value in our dataset
    fs.latest = datetime(
        2025,
        2,
        5,
        23,
        0,
        0,
        tzinfo=timezone(timedelta(seconds=39600)),
    )
    for monitor in fs.monitor:
        monitor.latest = fs.latest

    # Go through all the datasets
    poll = True
    while poll:
        poll = fs.poll()
