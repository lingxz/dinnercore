from project import app, db
from flask_testing import TestCase
from flask import url_for
from project.config import TestConfig


class BasicTestSetup(TestCase):
    def create_app(self):
        app.config.from_object(TestConfig)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class ServerRunning(BasicTestSetup):
    def test_server_running(self):
        """Check if server is up"""
        resp = self.client.get(url_for('index'))
        self.assert200(resp)
