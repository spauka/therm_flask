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
from typing import Optional, TypeAlias

from dataclass_wizard import JSONPyWizard, JSONFileWizard, JSONWizard

logger = logging.getLogger(__name__)

DEFAULT_CONF_LOC = Path("~").expanduser()
CONF_LOC = Path(os.environ.get("THERM_CONFIG", DEFAULT_CONF_LOC))
CONF_NAME = Path(os.environ.get("THERM_CONFIG_NAME", "labmon_config.json")).name
CONFIG_FILE = CONF_LOC / "labmon_config.json"


@dataclass(frozen=True)
class ServerConfig:
    ENABLED: bool = False
    SQLALCHEMY_DATABASE_URI: str = "postgresql+psycopg://therm@/therm"
    APPLICATION_ROOT: str = "/"
    DEBUG: bool = False
    SQLALCHEMY_RECORD_QUERIES: bool = False
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False


@dataclass()
class UploaderConfig(JSONWizard):
    # The type of the uploader
    TYPE: str = "Sample"
    # Enabled flag - by default false
    ENABLED: bool = False
    # Supplementary sample, if applicable
    SUPP: Optional[str] = None
    # Interval to upload the sample. For log-based uploaders (like BlueFors or Leiden)
    # this is the sample interval
    UPLOAD_INTERVAL: float = 20.0


@dataclass()
class SampleUploadConfig(UploaderConfig, JSONWizard):
    class _(JSONWizard.Meta):
        # This is the name of the uplader as defined in the upload.py file
        tag = "Sample"

    TYPE: str = "Sample"
    # Sample uploader config, that uploads a random value for the field
    # names listed in the FIELD_NAMES config variable
    FIELD_NAMES: list[str] = field(default_factory=lambda: ["Field_1", "Field_2"])


@dataclass()
class BlueForsUploadConfig(UploaderConfig, JSONWizard):
    class _(JSONWizard.Meta):
        # This is the name of the uplader as defined in the upload.py file
        tag = "BlueFors"

    # Check the sensor file every 1.0 seconds
    UPLOAD_INTERVAL: float = 1.0
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


@dataclass()
class LeidenUploadConfig(UploaderConfig, JSONWizard):
    class _(JSONWizard.Meta):
        # This is the name of the uplader as defined in the upload.py file
        tag = "Leiden"

    # Check the sensor file every 1.0 seconds
    UPLOAD_INTERVAL: float = 1.0
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
class AVS47ChannelConfig(JSONWizard):
    SENSOR: str = "Four_K_RuO"
    CALIBRATION: str = "PT1000"
    # Wait this long after reaching the final range
    SETTLE_DELAY: float = 10.0
    # Average points <AVERAGE_COUNT> times with <AVERAGE_DELAY> time between each point
    AVERAGE_COUNT: int = 3
    AVERAGE_DELAY: float = 1.0


@dataclass()
class AVS47Config(UploaderConfig, JSONWizard):
    class _(JSONWizard.Meta):
        # This is the name of the uplader as defined in the upload.py file
        tag = "AVS47"

    # PySerial port
    SERIAL_PORT: str = "COM4"
    # AVS address - used for chained units
    ADDRESS: int = 1
    UPLOAD_INTERVAL: float = 20.0
    UPLOAD_MILLIKELVIN: bool = False
    SENSORS: dict[int, AVS47ChannelConfig] = field(
        default_factory=lambda: {
            0: AVS47ChannelConfig("Four_K_RuO", "RuO_10K"),
            1: AVS47ChannelConfig("Still_RuO", "RuO_10K"),
            2: AVS47ChannelConfig("50mK_RuO", "RuO_1K5"),
            3: AVS47ChannelConfig("MC_Speer", "TT_1326"),
            5: AVS47ChannelConfig("MC_PT", "PT1000"),
        }
    )


@dataclass()
class Lakeshore336Config(UploaderConfig, JSONWizard):
    class _(JSONWizard.Meta):
        # This is the name of the uplader as defined in the upload.py file
        tag = "Lakeshore336"

    # Visa Address
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


@dataclass()
class MaxigaugeConfig(UploaderConfig, JSONWizard):
    class _(JSONWizard.Meta):
        # This is the name of the uplader as defined in the upload.py file
        tag = "MaxiGauge"

    # Visa Address
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
            "5": "Still ",
        }
    )


@dataclass()
class CryomechConfig(UploaderConfig, JSONWizard):
    class _(JSONWizard.Meta):
        # This is the name of the uplader as defined in the upload.py file
        tag = "Cryomech"

    # Visa Address
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


_VALID_UPLOAD_CONFIGS: TypeAlias = (
    BlueForsUploadConfig
    | LeidenUploadConfig
    | Lakeshore336Config
    | MaxigaugeConfig
    | CryomechConfig
    | AVS47Config
    | SampleUploadConfig
)


@dataclass(frozen=True)
class UploadConfig:
    ENABLED: bool = False
    MOCK: bool = False  # Simulate upload only, don't actually upload
    BASE_URL: str = "https://qsyd.sydney.edu.au/data"
    FRIDGE: str = "?"  # Fill in with fridge name

    ENABLED_UPLOADERS: list[_VALID_UPLOAD_CONFIGS] = field(
        default_factory=lambda: [
            SampleUploadConfig(),
            BlueForsUploadConfig(),
            LeidenUploadConfig(),
            AVS47Config(),
            Lakeshore336Config(),
            CryomechConfig(),
            MaxigaugeConfig(),
        ]
    )


@dataclass()
class Config(JSONPyWizard, JSONFileWizard):
    class _(JSONWizard.Meta):
        v1 = True
        v1_key_case = "AUTO"
        tag_key = "TYPE"

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
    loaded_config = Config.from_json_file(CONFIG_FILE)
    assert isinstance(loaded_config, Config)
    config = loaded_config

logger.info("Loaded config file %s", str(CONFIG_FILE))
logger.debug("Config parameters: %r", config)


# Pass config accesses to the config file
def __getattr__(name):
    return getattr(config, name)
