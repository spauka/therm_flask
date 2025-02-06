"""
Labmon config definition

WARNING: Do not edit the values below, these are just defaults. To change things,
edit the JSON file which is created in your home directory. Be default, this is in
Windows: %HOME%/labmon_config.json
Linux: ~/labmon_config.json
"""

# pylint: disable=invalid-name
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dataclass_wizard import JSONFileWizard, JSONWizard

logger = logging.getLogger(__name__)

DEFAULT_CONF_LOC = Path("~").expanduser()
CONF_LOC = Path(os.environ.get("THERM_CONFIG", DEFAULT_CONF_LOC))
CONFIG_FILE = CONF_LOC / "labmon_config.json"


@dataclass(frozen=True)
class ServerConfig:
    ENABLED: bool = False
    SQLALCHEMY_DATABASE_URI: str = "postgresql+psycopg://therm@/therm"
    APPLICATION_ROOT: str = "/"
    DEBUG: bool = False
    SQLALCHEMY_RECORD_QUERIES: bool = False
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False


@dataclass(frozen=True)
class BlueForsUploadConfig:
    LOG_DIR: str = "C:\\BlueFors_Logs"
    MAX_AGE: float = 180.0  # Maximum age of data in seconds
    SENSORS: dict[str, int] = field(
        default_factory=lambda: {
            "Fifty_K": 1,
            "Four_K": 2,
            "Magnet": 3,
            "Still": 5,
            "MXC": 6,
        }
    )
    UPLOAD_COMPRESSORS: bool = True
    NUM_COMPRESSORS: int = 1
    # The number of points to use when calculating the bounce on the
    # compressor pressure
    COMPRESSOR_BOUNCE_N: int = 15
    UPLOAD_MAXIGAUGE: bool = True


@dataclass(frozen=True)
class UploadConfig:
    ENABLED: bool = False
    MOCK: bool = False  # Simulate upload only, don't actually upload
    BASE_URL: str = "https://qsyd.sydney.edu.au/data"
    FRIDGE: str = "?"  # Fill in with fridge name
    ENABLED_UPLOADERS: list[str] = ["BlueFors"]  # Can also be Leiden
    BLUEFORS_CONFIG: BlueForsUploadConfig = BlueForsUploadConfig()


@dataclass(frozen=True)
class Config(JSONFileWizard, JSONWizard):
    class _(JSONWizard.Meta):
        key_transform_with_dump = "NONE"

    SERVER: ServerConfig = ServerConfig()
    UPLOAD: UploadConfig = UploadConfig()
    LOGGING: bool = False
    LOG_LEVEL: str = "WARNING"


if not CONFIG_FILE.exists():
    logger.warning(
        "Config file doesn't exist. Creating new file at %s.", str(CONFIG_FILE)
    )
    config: Config = Config()
    config.to_json_file(CONFIG_FILE, indent=2)

    # Print message and exit
    message = (
        f"Created config file at {CONFIG_FILE}.\n"
        f"Please fill in details and start again."
    )
    print(message)
    logger.error(message)
    sys.exit(0)
else:
    config: Config = Config.from_json_file(CONFIG_FILE)
logger.info("Loaded config file %s", str(CONFIG_FILE))
logger.debug("Config parameters: %r", config)


# Pass config accesses to the config file
def __getattr__(name):
    return getattr(config, name)


if __name__ == "__main__":
    import pprint

    pprint.pprint(config)
