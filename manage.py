import sys
import click
from flask import Flask

from slackertracker.app import create_app

app = create_app('instance/config.py')

@app.cli.command()
def test():
    import unittest
    from slackertracker.tests.suite import suite
    runner = unittest.TextTestRunner()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)