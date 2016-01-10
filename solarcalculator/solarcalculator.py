# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import numpy as np
import ephem
import ephem.cities
import simplejson as json
import pytz
import tzlocal
from tzwhere import tzwhere
from datetime import datetime, timedelta
import dateutil.parser
import dateutil.tz

# Set up a global tz (tzwhere) object
#tzw = tzwhere.tzwhere()

class SolarCalculator(object):
  _observer = None
  __sun = None
  __sun_needs_compute = True
  _geocoder = None
  _noon = None
  _solarnoon = None
  _sunset = None
  _sunrise = None

  def __init__(self, obs, elevation=None, date=None):
    """
    Give coords as tuple (lat, lon). If they are floats, radians are expected, and if they are strings then degrees are expected.
    Observer can also be an ephem.Observer instance.
    """
    # Set up observer
    if (isinstance(obs, ephem.Observer)):
      self._observer = obs
    else:
      self._observer = ephem.Observer()
      try:
        self._observer.lat, self._observer.lon = obs
      except Exception as e:
        raise AttributeError("Coord needs to be a ephem.Observer instance or a tuple of two floats")

    if (date is None):
      # If no date is given, use now
      self._observer.date = ephem.now()
    else:
      self._observer.date = date

    if (elevation is not None):
      self._obsever.elevation = elevation

    # Set up sun
    #self.__sun = ephem.Sun()

    # Set a flag to recompute sun
    self.__sun_needs_compute = True

  @property
  def sun(self):
    # Lazy instantiation
    if (self.__sun is None):
      self.__sun = ephem.Sun()
      self.__sun_needs_compute = True
      #print("[DEBUG] sun lazy instantiation")

    if (self.__sun_needs_compute):
      self.__sun.compute(self.observer)
      self.__sun_needs_compute = False
      #print("[DEBUG] sun compute")

    #print("[DEBUG] #### sun = {} ####".format(self.__sun))
    #print("[DEBUG] sun.ra={}".format(self.__sun.ra))
    #print("[DEBUG] sun.dec={}".format(self.__sun.dec))
    #print("[DEBUG] sun.alt={}".format(self.__sun.alt))
    #print("[DEBUG] sun.az={}".format(self.__sun.az))

    return self.__sun

  @sun.setter
  def sun(self, val):
    #print("[DEBUG] Setting sun")
    if (isinstance(val, ephem.Body)):
      self.__sun = val
      self.__sun_needs_compute = True
    else:
      raise TypeError("Sun needs to be a ephem.Body instance")

  @property
  def observer(self):
    # Lazy instantiation
    if (self._observer is None):
      self._observer = ephem.Observer()
      self.__sun_needs_compute = True
    #print("[DEBUG] self.observer='{}'".format(self._observer))
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
    self.__sun_needs_compute = True
    self._noon = None
    self._solarnoon = None
    self._sunrise = None
    self._sunset = None

  @property
  def date(self):
    """
    Returns the observer date in standard format.
    """
    return self.localized_date()

  @date.setter
  def date(self, val):
    """
    Sets the observer date.
    """
    self.observer.date = self.datetime_to_ephem(val)

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
    """
    Returns the observer timezone as a datetime object.
    """

    #print("[DEBUG] self.observer.date='{}'".format(self.observer.date))
    #print("[DEBUG] running observer_solartime, self.sun.az={}".format(self.sun.az))
    hour_angle = self.observer.sidereal_time() - self.sun.ra
    #print("[DEBUG] self.sun.az={}".format(self.sun.az))
    date_hrs = ephem.hours(hour_angle + ephem.pi).norm
    #print("[DEBUG] date_hrs='{}'".format(date_hrs))
    date = self.date
    date_str = "{}/{}/{} {}0000".format(date.year, date.month, date.day, str(date_hrs))
    #print("[DEBUG] date_str='{}'".format(date_str))
    date_fmt = "%Y/%m/%d %H:%M:%S.%f"

    # Create a naive datetime and a timezone offset
    solardate_naive = datetime.strptime(date_str, date_fmt)
    #print("[DEBUG] solardate_naive='{}'".format(solardate_naive))
    solar_tz = self.local_timezone(solardate_naive, self.localized_date(tz=pytz.utc))
    #print("[DEBUG] solar_tz='{}'".format(solar_tz))

    # Attach timezone to the datetime object
    solardate = solardate_naive.replace(tzinfo=solar_tz)
    #print("[DEBUG] solardate='{}'".format(solardate))


    """
    date_utc = self.localized_date(tz=pytz.utc)
    longitude = self.observer.lon
    date_naive = date_utc.replace(tzinfo=None)
    solardate_naive = date_naive + timedelta(hours=longitude/np.pi*12)
    td = solardate_naive - date_naive
    tz = dateutil.tz.tzoffset(None, 60*np.round(td.seconds/60.0))
    solardate = solardate_naive.replace(tzinfo=tz)
    """

    return self.round_datetime(solardate)

  @staticmethod
  def local_timezone(solartime, utc_time):
    """
    Returns the true timezone of the observer.
    utc_time has to be in utc timezone (no conversion is made here!)
    solartime does not need a timezone
    """
    #print("[DEBUG] local_timezone()")
    # Strip dates to naive datetime objects, to rid of time zone conversion (which we obviously do not want)
    utc_naive = utc_time.replace(tzinfo=None)
    #print("[DEBUG] utc_naive='{}'".format(utc_naive))
    solar_naive = solartime.replace(tzinfo=None)
    #print("[DEBUG] solar_naive='{}'".format(solar_naive))

    td = solar_naive - utc_naive

    #print("[DEBUG] td='{}'".format(td))
    seconds = td.total_seconds()
    # Make sure that -24 < td < 24 hrs
    while (seconds > 24*60*60):
      seconds -= 24*60*60
    while (seconds < -24*60*60):
      seconds += 24*60*60

    minutes = np.round(seconds/60.0)
    #print("[DEBUG] minutes='{}'".format(minutes))




    tz = dateutil.tz.tzoffset(None, 60*minutes)

    return tz

  @property
  def sunrise(self):
    #print("[DEBUG] sunrise()")
    if (self._sunrise is not None):
      return self._sunrise

    try:
      # Look out! Dirty fix ahead!
      sun = ephem.Sun()
      sun.compute(self.observer)
      self._sunrise = self.observer.previous_rising(sun, start=self.noon)
    except ephem.NeverUpError as e:
      self._sunrise = self.date.replace(hours=24, minutes=00, seconds=00, microseconds=00)
    except ephem.AlwaysUpError as e:
      self._sunrise = self.date.replace(hours=00, minutes=00, seconds=00, microseconds=00)

    return self._sunrise

  @property
  def sunset(self):
    #print("[DEBUG] sunset()")
    if (self._sunset is not None):
      return self._sunset

    try:
      # Dirty fix for an essentially a pyephem API problem (do not modify passed values in function!)
      sun = ephem.Sun()
      sun.compute(self.observer)
      self._sunset = self.observer.next_setting(sun, start=self.noon)
    except ephem.AlwaysUpError as e:
      self._sunset = self.date.replace(hours=24, minutes=00, seconds=00, microseconds=00)

    return self._sunset

  @property
  def solarnoon(self):
    #print("[DEBUG] solarnoon")
    if (self._solarnoon is not None):
      return self._solarnoon

    # Whoa, whoa, whoa! next_transit(sun) modifies sun!! WTF!?!
    # FIX: copy the sun and pass it to the next_transit method
    sun = ephem.Sun()
    sun.compute(self.observer)
    self._solarnoon = self.observer.next_transit(sun, start=self.sunrise)
    return self._solarnoon

  @property
  def solartime(self):
    """
    Returns the current solar time of the observer.
    """
    return self.observer_solartime()

  @property
  def timezone(self):
    """
    Returns the observer timezone.
    """
    return self.observer_timezone()

  @property
  def noon(self):
    """
    Returns noon on the given date as an ephem date.
    """
    #print("[DEBUG] noon()")
    #print("sun.az={}".format(self.sun.az))
    if (self._noon is not None):
      return self._noon

    # Get localized date (as local timezone)
    dt_local = self.date
    # Set time to noon (local time)
    dt_local_noon = dt_local.replace(hour=12, minute=0, second=0, microsecond=0)
    # Convert time to UTC
    dt_utc = dt_local_noon.astimezone(pytz.utc)
    dt_naive = dt_utc.replace(tzinfo=None)
    # Convert to ephem date
    self._noon = ephem.Date(dt_naive)

    #print("sun.az={}".format(self.sun.az))

    return self._noon

  @property
  def day_length(self):
    """
    Returns the length of the given day as a timedelta object.
    """
    #print("[DEBUG] day_length()")
    return self.localized_date(date=self.sunset) - self.localized_date(date=self.sunrise)

  def force_compute(self):
    """
    Forces sun to compute against the observer. Should be called if observer was changed manually.
    """
    self.sun.compute(self.observer)
    self.__sun_needs_compute = False

  def dict(self):
    """
    This method returns the current state of the object as dict.
    """
    self.force_compute()
    tz = self.observer_timezone()

    json_obj = {
        'observer': {
          'lat': str(self.observer.lat),
          'lon': str(self.observer.lon),
          'elevation': str(self.observer.elevation),
          'date': self.stringify(self.date),
          'timezone': str(tz),
          'solartime': self.stringify(self.solartime),
          },
        'stats': {
          'sunrise': self.stringify(self.localized_date(date=self.sunrise)),
          'sunset': self.stringify(self.localized_date(date=self.sunset)),
          'noon': self.stringify(self.localized_date(date=self.noon, tz=pytz.utc)),
          'solarnoon': self.stringify(self.localized_date(date=self.solarnoon)),
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

  def localized_date(self, tz=None, date=None):
    """
    This method returns the given date in the timezone of the observer. Ie. not the timezone of the server.
    """
    if date is None:
      date = self.observer.date
    if tz is None:
      tz = self.timezone

    if (isinstance(date, ephem.Date)):
      # Ephem dates are always in UTC
      date_naive = date.datetime() # in UTC
      date_utc = pytz.utc.localize(date_naive)
      # Localized datetime
      date_local = date_utc.astimezone(tz)
    elif (isinstance(date, datetime)):
      # The given date is already a datetime
      if (date.tzinfo is None):
        # There is no timezone information, so add it
        date_utc = pytz.utc.localize(date)
        date_local = date_utc.astimezone(tz)
      else:
        # There is already a timezone information, but it might not be correct
        try:
          date_local = date.astimezone(tz)
        except Exception as e:
          # Could not convert to timezone, so let's just assume it is UTC
          date_naive = date.replace(tzinfo=None)
          date_utc = pytz.utc.localize(date_naive)
          date_local = date_utc.astimezone(tz)
    else:
      # Not ephem.Date or datetime
      raise TypeError("Not an ephem.Date or datetime. Cannot proceed.")

    # Finally we get rid of lonely microseconds
    date_local = SolarCalculator.round_datetime(date_local)

    return date_local

  @staticmethod
  def stringify(dt):
    """
    Converts a localized datetime object to a string.
    """
    try:
      return str(dt.isoformat())
    except Exception as e:
      raise TypeError("Provided date is not a datetime object ({}): {}".format(type(dt), e))

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

  @staticmethod
  def datetime_to_ephem(dt):
    """
    Returns a non-localized version of a datetime object as an ephem date.
    Initializing an ephem.Date directly from a localized datetime results in an error, because the timezone does not get converted properly.
    """
    if (isinstance(dt, ephem.Date)):
      return dt
    if (not isinstance(dt, datetime)):
      raise TypeError("Not a datetime (or ephem.Date) object")

    if (dt.tzinfo is None):
      # This is a naive datetime, so we assume its already in UTC
      return ephem.Date(dt)
    else:
      # We have timezone information
      dt_utc = dt.astimezone(pytz.utc)
      return ephem.Date(dt_utc)

  @staticmethod
  def cities():
    """
    Returns a list of cities (with lat, lon, and elev), that the parser is able to understand.
    """
    city_data = ephem.cities._city_data
    city_arr = [{'name': city, 'lat': str(city_data[city][0]), 'lon': str(city_data[city][1]), 'elev': str(city_data[city][2])} for city in city_data]
    return city_arr

  @staticmethod
  def get_observer_from_city(city):
    """
    Returns an ephem.Observer that corresponds to the given city name.
    """
    try:
      obs = ephem.city(city)
    except Exception as e:
      raise AttributeError('City, {}, could not be found in database.'.format(city))
    return obs

class SolarStats(object):
  """
  A class that creates solar stats.
  """
  _solarcalculator = None

  def __init__(self, solarcalculator):
    self.solarcalculator = solarcalculator

  @property
  def solarcalculator(self):
    return self._solarcalculator

  @solarcalculator.setter
  def solarcalculator(self, solarcalculator):
    if (not isinstance(solarcalculator, SolarCalculator)):
      raise TypeError("Not a SolarCalculator instance.")
    self._solarcalculator = solarcalculator

  def days_in_year(self):
    """
    Iterates over all the days in the given year, starting from 1.1. and ending in 31.12.
    """
    tz = self.solarcalculator.timezone
    orig_date = self.solarcalculator.date
    one_day = timedelta(1,0)
    dt = tz.localize(datetime(orig_date.year, 1, 1, 12, 0, 0, 0))
    while (dt.year == orig_date.year):
      yield dt
      # Increase by one day
      dt = dt + one_day

  def daily_stats(self):
    """
    Iterates over all days in the given year and returns stats as a dict.
    """
    sc = self.solarcalculator
    tz = sc.timezone
    obs = sc.observer

    stats = {
        'days': [],
        }

    day_number = 0
    for day in self.days_in_year():
      sc.date = sc.datetime_to_ephem(day)
      day_stats = sc.dict()
      # Append day number to stats
      day_stats.update({'daynumber': str(day_number)})
      # Observer information is not needed for every day
      observer_info = day_stats.pop('observer')
      observer_info.pop('date')
      observer_info.pop('solartime')
      observer_info.update({'year': day.year})
      sun_info = day_stats.pop('sun')
      if (day_number == 0):
        # Add observer info to parent level
        stats['observer'] = observer_info
      stats['days'].append(day_stats)
      day_number += 1

    return stats

class GeoCoder(object):
  """
  This class abstracts coordinate geocoding and also provides timezone information based on coordinates.
  """
  _geolocator = tzwhere.tzwhere()
  _coords = None
  _timezone = None

  def __init__(self):
    # self._geolocator = tzw
    pass

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





