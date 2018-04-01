import unittest

test_config = 'instance/test_config.py'

from slackertracker.tests import main
from slackertracker.tests import model_user
from slackertracker.tests import model_channel

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(main))
suite.addTests(loader.loadTestsFromModule(model_user))
suite.addTests(loader.loadTestsFromModule(model_channel))