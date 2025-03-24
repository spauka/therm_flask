from .config import CONFIG_FILE, config


# Pass config accesses to the config file
def __getattr__(name):
    return getattr(config, name)


__all__ = ["CONFIG_FILE", "config"]
