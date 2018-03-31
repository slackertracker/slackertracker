import click
from flask import Flask

from slackertracker.app import create_app

app = create_app('instance/config.py')

@app.cli.command()
def test():
    import unittest
    from slackertracker.tests.suite import suite
    unittest.TextTestRunner().run(suite)