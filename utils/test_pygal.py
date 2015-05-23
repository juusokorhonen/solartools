# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, unicode_literals, print_function)

import pygal

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

bar_chart = pygal.Bar()
bar_chart.add('Fibonacci', [x for x in fibonacci(10)])
bar_chart.add('Padovan', [x for x in padovan(10)])
bar_chart.render_to_file('bar_chart.svg')
