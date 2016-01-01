# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from flask import Flask, Blueprint, current_app, request, render_template, redirect, flash, url_for, abort, request
from jinja2 import TemplateNotFound
import numpy as np
import pygal


restapi = Blueprint(u'restapi', __name__, template_folder='templates')

@restapi.route('/rest')
def rest_method():
    return abort(500)
