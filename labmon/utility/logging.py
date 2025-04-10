import logging

from colorama import Fore, Style, init

root_logger = logging.root
labmon_logger = logging.getLogger("labmon")
ch = logging.StreamHandler()

# Init terminal colors
init(autoreset=True)


# Colored output formatter
class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, Style.RESET_ALL)
        log_message = super().format(record)
        return f"{log_color}{log_message}{Style.RESET_ALL}"


def init_logging(level=logging.INFO):
    ch.setLevel(logging.DEBUG)

    formatter = ColoredFormatter("%(asctime)s - %(levelname)s:%(name)s - %(message)s")
    ch.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(ch)


def set_logging(level=logging.INFO, path=None):
    if path is None:
        labmon_logger.setLevel(level)
    else:
        specified_logger = logging.getLogger(path)
        specified_logger.setLevel(level)
