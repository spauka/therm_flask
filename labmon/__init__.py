from logging import getLevelName
from typing import TYPE_CHECKING

from .config import CONFIG_FILE, config
from .utility.logging import set_logging


if TYPE_CHECKING:
    from flask import Flask

# Check and enable logging if set
if config.LOGGING:
    level = getLevelName(config.LOG_LEVEL)
    set_logging(level)


def create_app() -> "Flask":
    """
    Create flask app if enabled, load the config and setup routes.
    Otherwise throw an error.
    """
    # Ensure that the server is enabled
    if not config.SERVER.ENABLED:
        raise RuntimeError(
            (
                "Server is not enabled in the config file. "
                f"Please enable the server in {CONFIG_FILE} and try again."
            )
        )

    # Load server modules
    # pylint: disable=import-outside-toplevel
    from flask import Flask, render_template

    # pylint: disable=import-outside-toplevel
    from . import db, fridge_data

    # Create and configure the app
    app = Flask(__name__)

    # Load config file
    app.config.from_object(config.SERVER)

    # Initialize db
    db.db.init_app(app)

    # Create a blank homepage
    @app.route("/")
    def blank():
        return render_template("blank.html", title=app.name)

    app.register_blueprint(fridge_data.fridge_bp)

    return app
