# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from flask.ext.wtf import Form
from wtforms import StringField, DecimalField
from wtforms.validators import DataRequired, NumberRange


class LocationForm(Form):
    latitude = DecimalField('Latitude', places=6, validators=[DataRequired(), NumberRange(min=-90.0, max=90.0, message="Valid range for latitude: -90.0 (W)...90.0 (E)")])
    longitude = DecimalField('Longitude', places=6, validators=[DataRequired(), NumberRange(min=-180.0, max=180.0, message="Valid range for longitude: -180.0 (S)...180.0 (N)")])

