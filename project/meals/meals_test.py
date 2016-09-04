from project import app, db
from flask_testing import TestCase
from flask import url_for
from project.config import TestConfig
from project.models import User, Group
import json


class MealTestSetup(TestCase):
    def create_app(self):
        app.config.from_object(TestConfig)
        return app

    def setUp(self):
        self.test_username1 = 'test1'
        self.test_password1 = 'test1'
        self.test_email1 = 'test1@test.com'
        self.test_group = 'test_group'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_user(self):
        user = User(
            username=self.test_username1,
            password=self.test_password1,
            email=self.test_email1
        )

        db.session.add(user)
        db.session.commit()

    def create_group(self):
        group = Group(self.test_group)
        db.session.add(group)
        db.session.commit()

    def login_user(self):
        self.create_user()
        resp = self.client.post(url_for('users.login'),
                                data=json.dumps({'email': self.test_email1, 'password': self.test_password1}),
                                content_type='application/json')
        return resp.json['token']


class TestMealRoutes(MealTestSetup):
    """Functions to check user routes"""

    def test_create_group(self):
        token = self.login_user()
        resp = self.client.post(url_for('meals.add_group'),
                                headers={'Authorization': 'Bearer ' + token},
                                data=json.dumps({
                                    'name': self.test_group
                                }),
                                content_type="application/json")
        self.assert200(resp)

    def test_add_user_to_group(self):
        token = self.login_user()
        resp = self.client.post(url_for('meals.add_user_to_group'),
                                headers={'Authorization': 'Bearer ' + token},
                                data=json.dumps({
                                    'user_id': 1,
                                    'group_id': 1
                                }),
                                content_type="application/json")
        self.assert200(resp)
