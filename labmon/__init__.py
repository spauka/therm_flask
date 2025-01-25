import os
import json
from pathlib import Path

from flask import Flask, render_template

import labmon.db as db

DEFAULT_CONF_LOC = Path("~").expanduser()
CONF_LOC = os.environ.get("THERM_CONFIG", DEFAULT_CONF_LOC)


def create_app() -> Flask:
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
    from . import fridge_data

    app.register_blueprint(fridge_data.fridge_bp)

    return app
