#!/suphys/spauka/bin/python

import config
from wsgiref.handlers import CGIHandler
from app import app

import sys

try:
    CGIHandler().run(app)
except Exception, e:
    print e
