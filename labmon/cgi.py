#!/usr/bin/env python3

from wsgiref.handlers import CGIHandler

from . import create_app

try:
    app = create_app()
    CGIHandler().run(app)
except Exception as e:
    print(e)
