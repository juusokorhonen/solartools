# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from flask import Flask, Blueprint, current_app, request, render_template, redirect, flash, url_for, abort, request
from jinja2 import TemplateNotFound
import numpy as np
import pygal


grapher = Blueprint(u'grapher', __name__, template_folder='templates')
print(str(grapher.root_path))


@grapher.route('/pygal_test')
def pygal_test():
    try:
        return render_template('pygal_test.html', plot_url=url_for('.test_bar_graph')) 
    except TemplateNotFound:
        return abort(500)

def fibonacci(n=1):
	_val = 0
	_next = 1
	_cnt = 0
	for i in xrange(n):
		yield _val
		temp = _next
		_next += _val
		_val = temp

def padovan(n=1):
	p0,p1,p2 = 1,1,1
	p = 1
	for i in xrange(min(3,n)):
		yield p
	for i in xrange(max(0,n-3)):
		p = p0 + p1
		yield p
		p0 = p1
		p1 = p2
		p2 = p

@grapher.route('/test_bar_graph.svg')
def test_bar_graph(length=10):
    bar_graph = pygal.Bar()
    try:
        bar_graph.add('Fibonacci', [x for x in fibonacci(int(length))])
        bar_graph.add('Padovan', [x for x in padovan(int(length))])
    except:
        return abort(500)
    return bar_graph.render_response()

