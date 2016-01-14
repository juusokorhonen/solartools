# -*- coding: utf-8 -*-
from __future__ import (absolute_import, print_function, unicode_literals, division)

def solarcalculator_test():
    import ephem
    import pytz
    from datetime import datetime, timedelta
    import numpy as np
    from solarcalculator import SolarCalculator

    print("Testing SolarCalculator interface.")

    sc = SolarCalculator(("65:01", "25:28")) # Passing coordinates of Oulu to constructor
    assert sc is not None, 'SolarCalculator initialization returned None'
    print("  Initialization ok.")

    hel = ephem.city('Helsinki')
    sc.observer = hel
    assert (int(sc.observer.lat/3.14159*180*1e5)/1e5) == 60.16986, 'Observer coordinates (lat) incorrect: {}'.format(sc.observer.lat/3.14159*180)
    assert (int(sc.observer.long/3.14159*180*1e5)/1e5) == 24.93826, 'Observer coordinates (long) incorrect: {}'.format(sc.observer.long/3.14159*180)
    print("  Observer setting ok.")

    sc.coords = ('37.8044', '-122.2697', 3.0)
    assert np.round(np.rad2deg(sc.observer.lat),4) == 37.8044, 'Changing observer (lat) coordinates failed: {}'.format(np.rad2deg(sc.observer.lat))
    assert np.round(np.rad2deg(sc.observer.long),4) == -122.2697, 'Changing observer (long) coordinates failed: {}'.format(np.rad2deg(sc.observer.long))
    print("  Coordinate setting ok.")

    time_str = '2012/11/16 20:34:56'
    time_fmt = '%Y/%m/%d %H:%M:%S'
    dt = datetime.strptime(time_str, time_fmt).replace(tzinfo=pytz.utc)
    assert dt.strftime(time_fmt) == time_str, 'Initializing a datetime object failed: {}'.format(dt.strftime(time_fmt))
    print("  Initialized datetime object ok.")
    sc.date = dt
    assert sc.localized_date(tz=pytz.utc).strftime(time_fmt) == time_str, 'Initializing date to solarcalculator failed: {}'.format(sc.localized_date(tz=pytz.utc).strftime(time_fmt))
    print("  Changed observer date ok.")
    tz = sc.timezone
    assert str(tz) == 'America/Los_Angeles', 'Timezone is incorrect: {}'.format(tz)
    print("  Timezone found ok.")

    assert sc.date.strftime(time_fmt) == '2012/11/16 12:34:56', 'Observer date did not return a proper result: {}'.format(sc.date.strftime(time_fmt))
    print("  Conversion to local timezone ok.")

    sdt = sc.solartime
    assert sdt.strftime(time_fmt) == '2012/11/16 12:40:55', 'Solartime did not return proper result: {}'.format(sdt.strftime(time_fmt))
    assert sdt.strftime("%z") == '-0754', 'Timezone offset incorrect: {}'.format(sdt.strftime("%z"))

    obs = ephem.city('Helsinki')
    sc.observer = obs
    assert sc.coords == (1.0501613384326405, 0.43525439939787997), 'Coordinates were not set properly: {}'.format(sc.coords)

    sc.coords = ('60:10:11.3', '24.9')

    dt = pytz.timezone('Europe/Stockholm').localize(datetime(2016, 1, 6, 20, 41, 31, 0))
    sc.date = dt
    assert sc.date.strftime(time_fmt) == '2016/01/06 21:41:31', 'Setting time from wrong local timezone failed: {}'.format(sc.date.strftime(time_fmt))
    print("  Date and time changed from wrongly localized time ok.")

    assert sc.solartime.strftime(time_fmt) == '2016/01/06 21:15:22', 'Calculating solar time in east failed: {}'.format(sc.solartime.strftime(time_fmt))
    print("  Solar time calculated ok.")

    tz = sc.timezone
    assert str(tz) == 'Europe/Helsinki', 'Timezone location failed: {}'.format(tz)
    print("  Timezone located ok.")
