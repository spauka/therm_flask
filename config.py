import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from dataclass_wizard import JSONFileWizard

if "THERM_CONFIG" in os.environ:
    CONFIG_FILE = os.environ["THERM_CONFIG"]
else:
    CONFIG_FILE = Path(__file__).parent / "config.json"

@dataclass
class Config(JSONFileWizard):
    db: str
    uri_base: str

    debug: bool
    track_modifications: bool
    record_queries: bool
config = Config.from_json_file(CONFIG_FILE)

# Pass config accesses to the config file
def __getattr__(name):
    return getattr(config, name)

