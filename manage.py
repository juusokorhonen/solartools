# -*- coding: utf-8 -*-
from __future__ import (absolute_import, unicode_literals, print_function, division)

import os
from flask.ext.script import Manager, Server

from backend import create_app
from flask import url_for
from config import Config, DevelopmentConfig, TestingConfig, ProductionConfig

app = create_app(config=DevelopmentConfig)
manager = Manager(app)

manager.add_command("runserver", Server(
    use_debugger = app.config.get('DEBUG', True),
    use_reloader = app.config.get('DEBUG', True),
    host = app.config.get('HOST', '0.0.0.0'))
    )

@manager.command
def runtests():
    print("Testing solarcalculator package.")
    from tests import solarcalculator_test
    solarcalculator_test()
    print("Test finished.")

    print()
    print("Testing solarstats class.")
    from tests import solarstats_test
    solarstats_test()
    print("Test finished.")

    print()
    print("All tests finished.")

if __name__ == '__main__':
    manager.run()
