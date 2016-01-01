# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from flask import Flask, Blueprint, current_app, request, render_template, redirect, flash, url_for, abort, request
from jinja2 import TemplateNotFound
import numpy as np
from bokeh.resources import CDN
from bokeh.plotting import figure
from bokeh.embed import autoload_static

testplot_bp = Blueprint(u'testplot', __name__)

@testplot_bp.route('/testplot', methods=['GET', 'POST'])
def testplot():
    x = np.arange(0,10) 
    y = np.sin(x/10*np.pi)
    plot = figure()
    plot.circle(x,y)
    js, tag = autoload_static(plot, CDN, "dynamic/js/testplot.js")

    fp = open(current_app.config.get('BASE_DIR', '') + "/app/dynamic/js/testplot.js", 'w+')
    if not fp:
        return abort(500)
    fp.write(js)
    fp.close()

    try:
        return render_template('static_plot.html', bokeh_tag=tag)
    except TemplateNotFound:
        return abort(404)
