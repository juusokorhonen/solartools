# -*- coding: utf-8 -*-

import os

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "xgq(&#bs)vv@o-hr42dkj4@lx%tn#&b1c=455_-*_t7!5u3q69"
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    SECRET_KEY = "b%#8%%m^we7+p5!3oteipwnhn0oq1e2tjv!@vgq18-_)q@=6xr"
