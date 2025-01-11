#!/usr/bin/env python3

import config
from wsgiref.handlers import CGIHandler
from app import app

import sys

try:
    CGIHandler().run(app)
except Exception as e:
    print(e)
