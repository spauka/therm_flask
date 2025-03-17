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
from typing import Optional

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
    LOG_WARNING_INTERVAL: int = 1_800  # Warn missing files every 30 minutes
    MAX_AGE: float = 180.0  # Maximum age of data in seconds
    SENSORS: dict[str, int] = field(
        default_factory=lambda: {
            "Fifty_K": 1,
            "Four_K": 2,
            "Magnet": 3,
            "Still": 5,
            "MC": 6,
        }
    )
    UPLOAD_COMPRESSORS: bool = True
    NUM_COMPRESSORS: int = 1
    # The number of points to use when calculating the bounce on the
    # compressor pressure
    COMPRESSOR_BOUNCE_N: int = 15
    UPLOAD_MAXIGAUGE: bool = True


@dataclass(frozen=True)
class LeidenUploadConfig:
    LOG_DIR: str = "C:\\avs-47\\"
    TC_FILE_PATTERN: str = (
        r"LogAVS_Reilly-DR__([0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2})\.dat"
    )
    # Check for a new log file after this many seconds with no new data
    NEW_LOG_CHECK_INTERVAL: int = 300
    SENSORS: dict[str, int] = field(
        default_factory=lambda: {
            "Four_K_RuO": 10,
            "Still_RuO": 11,
            "Fifty_mK_RuO": 12,
            "MC_CMN": 13,
            "MC_PT": 14,
        }
    )


@dataclass(frozen=True)
class Lakeshore336Config:
    ADDRESS: str = "TCPIP0::10.1.1.10::7777::SOCKET"
    UPLOAD_INTERVAL: float = 20.0
    UPLOAD_MILLIKELVIN: bool = False
    SENSORS: dict[str, str] = field(
        default_factory=lambda: {
            "A": "Four_K_Pt",
            "B": "Fifty_K_Pt",
            "C": "Four_K_RuO",
            "D": "Sample",
        }
    )


@dataclass(frozen=True)
class MaxigaugeConfig:
    ADDRESS: str = "ASRL4"
    # If this maxigauge is attached to a fridge, give the supplementary
    # table name
    SUPP: Optional[str] = None
    BAUD_RATE: Optional[int] = 9600
    UPLOAD_INTERVAL: float = 20.0
    SENSORS: dict[str, str] = field(
        default_factory=lambda: {
            "3": "OVC",
            "4": "IVC",
            "5": "STILL",
        }
    )


@dataclass(frozen=True)
class CryomechConfig:
    ADDRESS: str = "ASRL4"
    # If this compressor is attached to a fridge, give the supplementary
    # table name
    SUPP: Optional[str] = None
    # Note: Old version with the 7x3 display is v1,
    # New version with the graphical screen is v2
    COMPRESSOR_VERSION: str = "v1"
    COMPRESSOR_ADDRESS: int = 16
    BAUD_RATE: Optional[int] = 115200
    UPLOAD_INTERVAL: float = 20.0
    # Read the value of bounce from the compressor if false
    # otherwise attempt to calculate ourselves. If true, use COMPRESSOR_BOUNCE_N
    # points to calculate bounce
    USE_CALCULATED_BOUNCE: bool = False
    COMPRESSOR_BOUNCE_N: int = 15


@dataclass(frozen=True)
class UploadConfig:
    ENABLED: bool = False
    MOCK: bool = False  # Simulate upload only, don't actually upload
    BASE_URL: str = "https://qsyd.sydney.edu.au/data"
    FRIDGE: str = "?"  # Fill in with fridge name
    ENABLED_UPLOADERS: list[str] = field(default_factory=lambda: ["BlueFors"])  # Can also be Leiden
    BLUEFORS_CONFIG: BlueForsUploadConfig = BlueForsUploadConfig()
    LEIDEN_CONFIG: LeidenUploadConfig = LeidenUploadConfig()
    LAKESHORE_CONFIG: Lakeshore336Config = Lakeshore336Config()
    CRYOMECH_CONFIG: CryomechConfig = CryomechConfig()
    MAXIGAUGE_CONFIG: MaxigaugeConfig = MaxigaugeConfig()


@dataclass(frozen=True)
class Config(JSONFileWizard, JSONWizard):
    class _(JSONWizard.Meta):
        key_transform_with_dump = "NONE"

    SERVER: ServerConfig = ServerConfig()
    UPLOAD: UploadConfig = UploadConfig()
    LOGGING: bool = True
    LOG_LEVEL: str = "INFO"


if not CONFIG_FILE.exists():
    logger.warning("Config file doesn't exist. Creating new file at %s.", str(CONFIG_FILE))
    config: Config = Config()
    config.to_json_file(CONFIG_FILE, indent=2)

    # Print message and exit
    message = f"Created config file at {CONFIG_FILE}.\nPlease fill in details and start again."
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
