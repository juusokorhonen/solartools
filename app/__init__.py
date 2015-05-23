# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from flask import Flask, url_for, render_template, abort, flash, redirect, session, request, g, current_app
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from jinja2 import TemplateNotFound
from app.errorhandler import register_errorhandlers 
from app.grapher import grapher 

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
    
    # Development-specific functions 
    if (app.debug):
        pass
    # Testing-specifig functions
    if (app.config.get('TESTING')):
        pass
    # Production-specific functions
    if (app.config.get('PRODUCTION')):
        pass

    # Add blueprints
    app.register_blueprint(grapher)

    # Add errorhandler
    register_errorhandlers(app)
   
    # Add frontpage
    @app.route('/')
    def index():
        try:
            return render_template('index.html')
        except TemplateNotFound:
            abort(404)

    return app

