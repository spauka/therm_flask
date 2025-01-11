import os
import json
from pathlib import Path

from flask import Flask, render_template

from .db import db

DEFAULT_CONF_LOC = Path("~").expanduser()
CONF_LOC = os.environ.get("THERM_CONFIG", DEFAULT_CONF_LOC)

def create_app():
    # Create and configure the app
    app = Flask(
        __name__,
        instance_relative_config=True,
        instance_path=CONF_LOC
    )

    # Load config file
    app.config.from_file("labmon_config.json", load=json.load)

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config["db"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = app.config["track_modifications"]
    app.config['SQLALCHEMY_RECORD_QUERIES'] = app.config["record_queries"]

    # Initialize db
    db.init_app(app)

    # Create a blank homepage
    @app.route("/")
    def blank():
        return render_template("blank.html", title=app.name)

    return app
