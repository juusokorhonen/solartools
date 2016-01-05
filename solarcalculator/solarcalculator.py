# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import numpy as np
import ephem
import simplejson as json
import pytz
import tzlocal
from tzwhere import tzwhere
from datetime import datetime, timedelta
import dateutil.parser

# Set up a global tz (tzwhere) object
tzw = tzwhere.tzwhere()

class SolarCalculator(object):
  _observer = None
  _sun = None
  __sun_needs_compute = True
  _geocoder = None
  _noon = None
  _solarnoon = None
  _sunset = None
  _sunrise = None

  def __init__(self, coords, elevation=None, date=None):
    """
    Give coords as tuple (lat, lon). If they are floats, radians are expected, and if they are strings then degrees are expected.
    """
    # Set up observer
    self._observer = ephem.Observer()
    self._observer.lat, self._observer.lon = coords

    if (date is None):
      # If no date is given, use now
      self._observer.date = ephem.now()
    else:
      self._observer.date = date

    if (elevation is not None):
      self._obsever.elevation = elevation

    # Set up sun
    self._sun = ephem.Sun()

    # Set a flag to recompute sun
    self.__sun_needs_compute = True

  @property
  def sun(self):
    # Lazy instantiation
    if (self._sun is None):
      self._sun = ephem.Sun()
      self.__sun_needs_compute = True

    if (self.__sun_needs_compute):
      self._sun.compute(self.observer)
      self.__sun_needs_compute = False

    return self._sun

  @sun.setter
  def sun(self, val):
    if (isinstance(val, ephem.Body)):
      self._sun = val
      self.__sun_needs_compute = True
    else:
      raise TypeError("Sun needs to be a ephem.Body instance")

  @property
  def observer(self):
    # Lazy instantiation
    if (self._observer is None):
      self._observer = ephem.Observer()
      self.__sun_needs_compute = True
    return self._observer

  @observer.setter
  def observer(self, val):
    self._observer = val
    self.__sun_needs_compute = True
    self._noon = None
    self._solarnoon = None
    self._sunrise = None
    self._sunset = None

  @property
  def coords(self):
    if (self._observer is None):
      return None
    return (self._observer.lat, self._observer.lon)

  @coords.setter
  def coords(self, coords):
    try:
      self.observer.lat = coords[0]
      self.observer.lon = coords[1]
    except:
      raise TypeError("Coordinates could not be converted to ephem format.")
    else:
      self.__sun_needs_compute = True
      self._noon = None
      self._solarnoon = None
      self._sunrise = None
      self._sunset = None

  @property
  def geocoder(self):
    # Lazy instantiation
    if (self._geocoder is None):
      gc = GeoCoder()
      gc.coords = self.coords
      self._geocoder = gc
    return self._geocoder

  def observer_timezone(self):
    if (self.geocoder.coords != self.coords):
      self.geocoder.coords = self.coords
    return self.geocoder.timezone

  def observer_solartime(self):
    hour_angle = self.observer.sidereal_time() - self.sun.ra
    date_hrs = ephem.hours(hour_angle + ephem.hours(str('12:00'))).norm
    date_triple = self.observer.date.triple()
    date_str = "{}/{}/{} {}".format(date_triple[0], date_triple[1], int(date_triple[2]), str(date_hrs))
    print(date_str)
    date_ephem = ephem.date(str(date_str))
    return date_ephem

  @property
  def sunrise(self):
    if (self._sunrise is not None):
      return self._sunrise

    try:
      self._sunrise = self.observer.previous_rising(self.sun, start=self.noon)
    except Exception as e:
      print(str(e))
      pass

    return self._sunrise

  @property
  def sunset(self):
    if (self._sunset is not None):
      return self._sunset

    try:
      self._sunset = self.observer.next_setting(self.sun, start=self.noon)
    except Exception as e:
      print(str(e))
      pass

    return self._sunset

  @property
  def solarnoon(self):
    if (self._solarnoon is not None):
      return self._solarnoon

    try:
      self._solarnoon = self.observer.next_transit(self.sun, start=self.sunrise)
    except Exception as e:
      print(str(e))
      pass

    return self._solarnoon

  @property
  def noon(self):
    """
    Returns noon on the given date as an ephem date.
    """
    if (self._noon is not None):
      return self._noon

    dt = ephem.localtime(self.observer.date)
    # Get timezone
    tz = self.observer_timezone()
    # Get timedelta from UTC
    td = tz.utcoffset(dt)
    # Set time to noon (local time)
    dt = dt.replace(hour=12, minute=0, second=0, microsecond=0)
    # Convert time to UTC
    dt = dt-td
    # Convert to ephem date
    date = ephem.Date(dt)
    # Save noon
    self._noon = date

    return self._noon

  @property
  def day_length(self):
    """
    Returns the length of the given day.
    """
    return ephem.hours(self.sunset - self.sunrise)

  def dict(self):
    """
    This method returns the current state of the object as dict.
    """
    tz = self.observer_timezone()

    json_obj = {
        'observer': {
          'lat': str(self.observer.lat),
          'lon': str(self.observer.lon),
          'elevation': str(self.observer.elevation),
          'date': str(self.localize_date(self.observer.date, tz)),
          'timezone': str(tz),
          'solartime': str(self.localize_date(self.observer_solartime(), tz)),
          'sunrise': str(self.localize_date(self.sunrise, tz)),
          'sunset': str(self.localize_date(self.sunset, tz)),
          'noon': str(self.localize_date(self.noon, pytz.utc)),
          'solarnoon': str(self.localize_date(self.solarnoon, tz)),
          'daylength': str(self.day_length),
          },
        'sun': {
          'ra': str(self.sun.ra),
          'dec': str(self.sun.dec),
          'az': str(self.sun.az),
          'alt': str(self.sun.alt),
          },
    }
    return json_obj

  @staticmethod
  def localize_date(date_obj, tz):
    """
    This method returns the given date in the timezone of the observer. Ie. not the timezone of the server.
    """
    if (isinstance(date_obj, ephem.Date)):
      # Ephem dates are always in UTC
      date_utc = date_obj.datetime() # in UTC
      # Localized datetime
      date_local = tz.localize(date_utc)
    elif (isinstance(date_obj, datetime)):
      # The given date_obj is already a datetime
      if (date_obj.tzinfo is None):
        # There is no timezone information, so add it
        date_utc = date_obj
        date_local = tz.localize(date_utc)
      else:
        # There is already a timezone information, but it might not be correct
        try:
          date_local = date_obj.astimezone(tz)
        except Excption as e:
          # Could not convert to timezone, so let's just assume it is UTC
          date_naive = date_obj.replace(tzinfo=None)
          date_utc = pytz.utc.localize(date_naive)
          date_local = date_utc.astimezone(tz)
    else:
      # Not ephem.Date or datetime
      raise TypeError("Not an ephem.Date or datetime. Cannot proceed.")

    # Finally we get rid of lonely microseconds
    date_local = SolarCalculator.round_datetime(date_local)

    return date_local

  @staticmethod
  def datetime_to_string(dt):
    """
    Converts a localized datetime object to a string.
    """
    try:
      return dt.isoformat()
    except Exception as e:
      raise TypeError("Provided date is not a datetime object.")

  @staticmethod
  def round_datetime(dt):
    """
    Round the datetime to the nearest second.
    """
    try:
      # First round microseconds
      if (dt.microsecond >= 500000):
        one_second = timedelta(0,1)
        dt = dt.replace(microsecond=0) + one_second
      else:
        dt = dt.replace(microsecond=0)
    except Exception as e:
      raise AttributeError("dt does not appear to be a valid datetime object.")
    return dt

class GeoCoder(object):
  """
  This class abstracts coordinate geocoding and also provides timezone information based on coordinates.
  """
  _geolocator = None
  _coords = None
  _timezone = None

  def __init__(self):
    self._geolocator = tzw

  @property
  def coords(self):
    return self._coords

  @coords.setter
  def coords(self, coords):
    if (len(coords) != 2):
      raise TypeError("Coords needs to be a set of coordinates: (lat, lon) in radians: {}".format(str(coords)))
    try:
      lat = float(coords[0])
      lon = float(coords[1])
    except Exception as e:
      raise TypeError("Coords needs to be given as two floats (in radians): {}".format(str(e)))

    self._coords = (lat, lon)
    self._timezone = None # Reset timezone as we don't know it anymore

  @property
  def timezone(self):
    """
    Returns the tzlocal timezone of the given coordinates.
    """
    # We cache the result to avoid multiple searches
    if (self._timezone is not None):
      return self._timezone

    try:
      timezone = pytz.timezone(self._geolocator.tzNameAt(np.rad2deg(self._coords[0]), np.rad2deg(self._coords[1])))
    except Exception as e:
      # We fall back to using the local timezone of the server
      timezone = tzlocal.get_localzone()
    finally:
      self._timezone = timezone

    return self._timezone





