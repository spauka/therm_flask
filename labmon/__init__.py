import json
import os
from pathlib import Path

from flask import Flask, render_template

from . import db
from .config import CONF_LOC, CONFIG_FILE, config


def create_app() -> Flask:
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

    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True, instance_path=CONF_LOC)

    # Load config file
    app.config.from_file("labmon_config.json", load=json.load)

    # Initialize db
    db.db.init_app(app)

    # Create a blank homepage
    @app.route("/")
    def blank():
        return render_template("blank.html", title=app.name)

    # Load fridge data
    from . import fridge_data  # pylint: disable=import-outside-toplevel

    app.register_blueprint(fridge_data.fridge_bp)

    return app
