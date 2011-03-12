import unittest2 
from nose.tools import eq_

from astral.conf import settings

import os
os.environ["ASTRAL_SETTINGS_MODULE"] = 'astral.conf.global_settings'

class SettingsTest(unittest2.TestCase):
    def test_global_setting(self):
        eq_(settings.DEBUG, False)
