# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from flask import Flask, url_for, render_template, abort, flash, redirect, session, request, g, current_app
from flask_bootstrap import Bootstrap, StaticCDN, WebCDN
from flask_appconfig import AppConfig
from jinja2 import TemplateNotFound
from .errorhandler import register_errorhandlers
from .rest import restapi, restapi_bp
from database.rediscon import rc

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
    AppConfig(app, default_settings=config, configfile=configfile)
    Bootstrap(app) # Use flask-bootstrap
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    # Development-specific functions
    if (app.debug):
        pass
    # Testing-specifig functions
    if (app.config.get('TESTING')):
        pass
    # Production-specific functions
    if (app.config.get('PRODUCTION')):
        pass

    # Initialize redis connection
    rc.init_app(app)

    # Add REST api
    app.register_blueprint(restapi_bp)

    # Add errorhandler
    register_errorhandlers(app)

    return app
