import unittest

test_config = 'instance/test_config.py'

from slackertracker.tests import main
from slackertracker.tests import model_user
from slackertracker.tests import model_channel
from slackertracker.tests import model_reaction

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(main))
suite.addTests(loader.loadTestsFromModule(model_user))
suite.addTests(loader.loadTestsFromModule(model_channel))
suite.addTests(loader.loadTestsFromModule(model_reaction))