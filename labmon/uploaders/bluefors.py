from ..utility.logging import logging, set_logging
from .bluefors_tc import BlueForsTempMonitor

if __name__ == "__main__":
    set_logging(logging.DEBUG)
    fs = BlueForsTempMonitor()
