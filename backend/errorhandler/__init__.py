# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)
from flask import Flask, Blueprint, current_app, request, render_template, redirect, flash, url_for, abort
from jinja2 import TemplateNotFound

def register_errorhandlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        flash('Access was forbidden.')
        return redirect(url_for('index'))

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('page_not_found.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('server_error.html'), 500

