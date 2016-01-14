# -*- coding: utf-8 -*-
from __future__ import (absolute_import, print_function, unicode_literals, division)

def solarstats_test():
  import ephem
  import pytz
  from datetime import datetime, timedelta
  import numpy as np
  from solarcalculator import SolarCalculator, SolarStats

  print("Testing SolarStats interface.")

  hel = ephem.city('Helsinki')
  sc = SolarCalculator(hel)
  tz = pytz.timezone('Europe/Helsinki')
  dt = tz.localize(datetime(2016, 1, 6, 21, 41, 31, 0))
  sc.date = dt

  time_fmt = '%Y/%m/%d %H:%M:%S'

  assert sc.date.strftime(time_fmt) == '2016/01/06 21:41:31', 'Setting SolarCalculator date failed: {}'.format(sc.date.strftime(time_fmt))
  assert sc.coords == (1.0501613384326405, 0.43525439939787997), 'Setting SolarCalculator observer failed: {}'.format(sc.coords)
  print("  Setting up the preliminary SolarCalculator object ok.")

  st = SolarStats(sc)
  assert st.solarcalculator.coords == (1.0501613384326405, 0.43525439939787997), 'Setting up SolarStats failed: {}'.format(st.solarcalculator.coords)
  print("  Set up SolarStats ok.")

  days_in_year_arr = [x for x in st.days_in_year()]
  assert len(days_in_year_arr) == 366, 'Wrong number of days_in_year: {}'.format(len(days_in_year_arr))
  print("  Correct number of days in year 2016")

  assert tz.localize(datetime(2016, 2, 29, 12, 0, 0)) in days_in_year_arr, 'Leap day 2016/02/29 not in day array. Check failed.'
  print("  Leap day 2016/02/29 found in 2016 ok.")

  daily_stats = st.daily_stats()
  obs_assert = {u'elevation': '7.153307', u'lon': '24:56:17.7', u'date': '2016-01-01 12:00:00+02:00', u'solartime': '2016-01-01 12:00:29+02:00', u'lat': '60:10:11.3', u'timezone': 'Europe/Helsinki'}
  assert daily_stats.get('observer') == obs_assert, 'Observer info failed: {}'.format(daily_stats.get('observer'))
  print("  SolarStats observer field ok.")

  assert len(daily_stats.get('days')) == 366, 'Wrong number of days in SolarStats days: {}'.format(len(daily_stats.get('days')))
  print("  SolarStats number of days ok.")


