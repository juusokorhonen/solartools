# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from flask import Flask, Blueprint, current_app, request, render_template, redirect, flash, url_for, abort, request
from flask_restful import Resource, Api, reqparse
from jinja2 import TemplateNotFound
import numpy as np
import pygal
from solarcalculator import SolarCalculator, SolarStats

restapi_bp = Blueprint('restapi', __name__)
restapi = Api(restapi_bp)

class LocationCalculator(Resource):
    def get(self):
      try:
        sc = SolarCalculator((request.args['lat'], request.args['lon']))
      except Exception as e:
        abort(400)
      return sc.dict()

class StatsCalculator(Resource):
    def get(self):
      try:
        sc = SolarCalculator((request.args['lat'], request.args['lon']))
        st = SolarStats(sc)
      except Exception as e:
        print("Exception! {}".format(e))
        abort(400)
      return st.daily_stats()


restapi.add_resource(LocationCalculator, '/location')
restapi.add_resource(StatsCalculator, '/stats')

