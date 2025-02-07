#!/usr/bin/env python3

from wsgiref.handlers import CGIHandler

from . import create_app

app = create_app()
CGIHandler().run(app)
