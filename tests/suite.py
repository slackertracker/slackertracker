import unittest

test_config = 'instance/test_config.py'

import slackertracker.tests.tests as main_tests

suite = unittest.TestLoader().loadTestsFromModule(main_tests)