import unittest
import slackertracker.tests.tests as main_tests

test_config = 'instance/test_config.py'

suite = unittest.TestLoader().loadTestsFromModule(main_tests)