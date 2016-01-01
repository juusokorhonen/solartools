# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from flask import Flask, Blueprint, current_app, request, render_template, redirect, flash, url_for, abort, request
from flask_restful import Resource, Api, reqparse
from jinja2 import TemplateNotFound
import numpy as np
import pygal

restapi_bp = Blueprint('restapi', __name__)
restapi = Api(restapi_bp)

class LocationCalculator(Resource):
    def get(self):
        return {'lat': request.args['lat'], 'lon': request.args['lon']}

restapi.add_resource(LocationCalculator, '/location')

