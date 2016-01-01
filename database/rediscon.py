# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from flask import current_app
import redis

class Rc(object):
    _rc = None

    def __init__(self, app=None, host=None, port=None, db=None):
        self.host = host or 'localhost'
        self.port = port or 6379
        self.db = db or 0
        self.app = app

    def init_app(self, app):
        self.host = app.config.get('REDIS_HOST', 'localhost')
        self.port = app.config.get('REDIS_PORT', 6379)
        self.db = app.config.get('REDIS_DB', 0)
        self.app = app

    @property
    def connection(self):
        if self._rc is None:
            self._rc = redis.StrictRedis(host=self.host,
                port = self.port,
                db = self.db)
        return self._rc

    def disconnect(self):
        if self._rc is not None:
            self._rc.close()

rc = Rc()
