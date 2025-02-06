import logging

from colorama import Fore, Style, init

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


def set_logging(level=logging.INFO):
    root_logger = logging.root

    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = ColoredFormatter("%(asctime)s - %(levelname)s:%(name)s - %(message)s")
    ch.setFormatter(formatter)

    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(ch)
