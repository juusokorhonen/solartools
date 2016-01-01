# -*- coding: utf-8 -*-
from __future__ import (absolute_import, unicode_literals, print_function, division)

from flask import current_app

def solarcalculator_test():
    from app.grapher import SolarCalculator
    import ephem
    from datetime import datetime, timedelta
    import pytz
    import numpy as np

    print("Testing SolarCalculator interface.")

    sc = SolarCalculator()
    assert sc is not None, 'SolarCalculator initialization returned None'
    print("  Initialization ok.")

    hel = ephem.city('Helsinki')
    sc.observer = hel
    assert (int(sc.observer.lat/3.14159*180*1e5)/1e5) == 60.16986, 'Observer coordinates (lat) incorrect: {}'.format(sc.observer.lat/3.14159*180)
    assert (int(sc.observer.long/3.14159*180*1e5)/1e5) == 24.93826, 'Observer coordinates (long) incorrect: {}'.format(sc.observer.long/3.14159*180)
    print("  Observer setting ok.")

    sc.coordinates = ('37.8044', '-122.2697', 3.0)
    assert np.round(np.rad2deg(sc.observer.lat),4) == 37.8044, 'Changing observer (lat) coordinates failed: {}'.format(np.rad2deg(sc.observer.lat))
    assert np.round(np.rad2deg(sc.observer.long),4) == -122.2697, 'Changing observer (long) coordinates failed: {}'.format(np.rad2deg(sc.observer.long))
    print("  Coordinate setting ok.")

    time_str = '2012/11/16 20:34:56'
    time_fmt = '%Y/%m/%d %H:%M:%S'
    dt = datetime.strptime(time_str, time_fmt).replace(tzinfo=pytz.utc)
    assert dt.strftime(time_fmt) == time_str, 'Initializing a date failed: {}'.format(dt.strftime(time_fmt))
    print("  Initialized datetime ok.")
    ldt = dt.astimezone(pytz.timezone('Europe/Helsinki'))
    assert ldt.strftime(time_fmt) == '2012/11/16 22:34:56', 'Changing to local timezone failed: {}'.format(ldt.strftime(time_fmt))
    print("  Conversion to local timezone ok.")

    sdt = sc.solartime(dt=dt)
    assert sdt.strftime(time_fmt) == '2012/11/16 12:40:55', 'Solartime did not return proper result: {}'.format(sdt.strftime(time_fmt))
    assert sdt.strftime("%z") == '-0754', 'Timezone offset incorrect: {}'.format(sdt.strftime("%z"))

    sdt_approx = sc.solartime_approximation(dt=dt)
    td = sdt_approx - sdt
    assert np.abs(td.total_seconds()) < 60.0, 'Solar time approximation differs from accurate calculation too much: {}'.format(td.total_seconds())



