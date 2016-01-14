# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from flask import Flask, url_for, abort, flash, redirect, session, request, g, current_app
from flask_appconfig import AppConfig, HerokuConfig
from flask.ext.cors import CORS
from .errorhandler import register_errorhandlers
from .rest import restapi, restapi_bp

def create_app(config=None, configfile=None):
    """
    Creates a Flask app using the provided configuration.

    Keyword arguments:
    :param config:  Config object or None (default: None)
    :param configfile: - Name and path to configfile (default: None)
    :returns: Flask application
    """
    app = Flask(__name__)

    # Configure app
    HerokuConfig(app, default_settings=config, configfile=configfile)

    # Set up CORS
    CORS(app)

    # Development-specific functions
    if (app.debug):
        pass
    # Testing-specifig functions
    if (app.config.get('TESTING')):
        pass
    # Production-specific functions
    if (app.config.get('PRODUCTION')):
        pass

    # Add REST api
    app.register_blueprint(restapi_bp)

    return app

