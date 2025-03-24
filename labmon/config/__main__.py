import pprint
from .config import UploaderConfig, config

"""
Print configuration if loaded directly
"""

pprint.pprint(config)
print(UploaderConfig._CONFIG_CLASSES)
