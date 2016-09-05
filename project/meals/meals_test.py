from project import app, db
from flask_testing import TestCase
from flask import url_for
from project.config import TestConfig
from project.models import User, Group
import json
from datetime import datetime, date
from project.meals import meals


class MealTestSetup(TestCase):
    def create_app(self):
        app.config.from_object(TestConfig)
        return app

    def setUp(self):
        self.test_username1 = 'test1'
        self.test_username2 = 'test2'
        self.test_password1 = 'test1'
        self.test_password2 = 'test2'
        self.test_email1 = 'test1@test.com'
        self.test_email2 = 'test2@test.com'
        self.test_group = 'test_group'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_user(self):
        user1 = User(
            username=self.test_username1,
            password=self.test_password1,
            email=self.test_email1
        )
        user2 = User(
            username=self.test_username2,
            password=self.test_password2,
            email=self.test_email2
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

    def create_group(self):
        group = Group(self.test_group)
        db.session.add(group)
        db.session.commit()

    def add_users_to_group(self):
        users = User.query.all()
        for user in users:
            user.groupID = 1
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
        self.create_group()
        resp = self.client.post(url_for('meals.add_user_to_group'),
                                headers={'Authorization': 'Bearer ' + token},
                                data=json.dumps({
                                    'user_id': 1,
                                    'group_id': 1
                                }),
                                content_type="application/json")
        self.assert200(resp)

    def test_add_user_to_non_existent_group(self):
        token = self.login_user()
        resp = self.client.post(url_for('meals.add_user_to_group'),
                                headers={'Authorization': 'Bearer ' + token},
                                data=json.dumps({
                                    'user_id': 1,
                                    'group_id': 1
                                }),
                                content_type="application/json")
        self.assert404(resp)

    def test_add_meal(self):
        token = self.login_user()
        date = 'Mon Sep 05 2016 00:01:58 GMT+0800 (Malay Peninsula Standard Time)'
        resp = self.client.post(url_for('meals.add_meal'),
                                headers={'Authorization': 'Bearer ' + token},
                                data=json.dumps({
                                    'group_id': 1,
                                    'date': date,
                                    'meal_type': 'lunch',
                                    'ate': {1: 3, 2: 0},
                                    'cooked': 1
                                }),
                                content_type="application/json")
        self.assert200(resp)

    def test_get_meal_count_of_user_by_date(self):
        token = self.login_user()
        self.create_group()
        date = 'Mon Sep 05 2016 00:01:58 GMT+0800 (Malay Peninsula Standard Time)'
        self.client.post(url_for('meals.add_meal'),
                         headers={'Authorization': 'Bearer ' + token},
                         data=json.dumps({
                             'group_id': 1,
                             'date': date,
                             'meal_type': 'lunch',
                             'ate': {1: 3, 2: 0},
                             'cooked': 1
                         }),
                         content_type="application/json")
        resp = self.client.post(url_for('meals.get_meal_count_of_user_by_date'),
                                headers={'Authorization': 'Bearer ' + token},
                                data=json.dumps({
                                    'user_id': 1,
                                    'date': date
                                }),
                                content_type="application/json")
        self.assert200(resp)
        self.assertEqual(resp.json['count'], 3)

        resp2 = self.client.post(url_for('meals.get_meal_count_of_user_by_date'),
                                headers={'Authorization': 'Bearer ' + token},
                                data=json.dumps({
                                    'user_id': 2,
                                    'date': date
                                }),
                                content_type="application/json")

        self.assert200(resp2)
        self.assertEqual(resp2.json['count'], 0)

    def test_tally_meal_count_when_last_tallied_date_is_none(self):
        token = self.login_user()
        self.create_group()
        group = Group.query.get(1)
        self.assertEqual(group.dateLastTallied, None)
        date1 = 'Mon Sep 03 2016 00:01:58 GMT+0800 (Malay Peninsula Standard Time)'
        date2 = 'Mon Sep 04 2016 00:01:58 GMT+0800 (Malay Peninsula Standard Time)'
        self.client.post(url_for('meals.add_meal'),
                         headers={'Authorization': 'Bearer ' + token},
                         data=json.dumps({
                             'group_id': 1,
                             'date': date1,
                             'meal_type': 'lunch',
                             'ate': {1: 3, 2: 0},
                             'cooked': 1
                         }),
                         content_type="application/json")

        self.client.post(url_for('meals.add_meal'),
                         headers={'Authorization': 'Bearer ' + token},
                         data=json.dumps({
                             'group_id': 1,
                             'date': date2,
                             'meal_type': 'lunch',
                             'ate': {1: 2, 2: 1},
                             'cooked': 2
                         }),
                         content_type="application/json")
        resp1 = self.client.post(url_for('meals.tally_meal_count_of_user'),
                                headers={'Authorization': 'Bearer ' + token},
                                data=json.dumps({
                                    'user_id': 1,
                                    'group_id': 1
                                }),
                                content_type="application/json")

        self.assert200(resp1)
        self.assertEqual(resp1.json['count'], 5)

        group = Group.query.get(1)
        today = date.today()
        self.assertEqual(group.dateLastTallied, today)

    def test_tally_meal_when_last_tallied_date_exists(self):
        token = self.login_user()
        self.create_group()
        group = Group.query.get(1)
        group.dateLastTallied = date(2016, 9, 3)
        db.session.commit()
        date1 = 'Mon Sep 03 2016 00:01:58 GMT+0800 (Malay Peninsula Standard Time)'
        date2 = 'Mon Sep 04 2016 00:01:58 GMT+0800 (Malay Peninsula Standard Time)'
        self.client.post(url_for('meals.add_meal'),
                         headers={'Authorization': 'Bearer ' + token},
                         data=json.dumps({
                             'group_id': 1,
                             'date': date1,
                             'meal_type': 'lunch',
                             'ate': {1: 3, 2: 0},
                             'cooked': 1
                         }),
                         content_type="application/json")

        self.client.post(url_for('meals.add_meal'),
                         headers={'Authorization': 'Bearer ' + token},
                         data=json.dumps({
                             'group_id': 1,
                             'date': date2,
                             'meal_type': 'lunch',
                             'ate': {1: 2, 2: 1},
                             'cooked': 2
                         }),
                         content_type="application/json")
        resp1 = self.client.post(url_for('meals.tally_meal_count_of_user'),
                                headers={'Authorization': 'Bearer ' + token},
                                data=json.dumps({
                                    'user_id': 1,
                                    'group_id': 1
                                }),
                                content_type="application/json")

        self.assert200(resp1)
        self.assertEqual(resp1.json['count'], 2)

    def test_tally_meal_count_of_group_when_last_tallied_date_is_none(self):
        token = self.login_user()
        self.create_group()
        self.add_users_to_group()
        group = Group.query.get(1)
        self.assertEqual(group.dateLastTallied, None)
        date1 = 'Mon Sep 03 2016 00:01:58 GMT+0800 (Malay Peninsula Standard Time)'
        date2 = 'Mon Sep 04 2016 00:01:58 GMT+0800 (Malay Peninsula Standard Time)'
        self.client.post(url_for('meals.add_meal'),
                         headers={'Authorization': 'Bearer ' + token},
                         data=json.dumps({
                             'group_id': 1,
                             'date': date1,
                             'meal_type': 'lunch',
                             'ate': {1: 3, 2: 0},
                             'cooked': 1
                         }),
                         content_type="application/json")

        self.client.post(url_for('meals.add_meal'),
                         headers={'Authorization': 'Bearer ' + token},
                         data=json.dumps({
                             'group_id': 1,
                             'date': date2,
                             'meal_type': 'lunch',
                             'ate': {1: 2, 2: 1},
                             'cooked': 2
                         }),
                         content_type="application/json")
        resp1 = self.client.post(url_for('meals.tally_meal_count_of_group'),
                                headers={'Authorization': 'Bearer ' + token},
                                data=json.dumps({
                                    'group_id': 1
                                }),
                                content_type="application/json")

        self.assert200(resp1)
        self.assertEqual(resp1.json['1'], 5)
        self.assertEqual(resp1.json['2'], 1)

        group = Group.query.get(1)
        today = date.today()
        self.assertEqual(group.dateLastTallied, today)

    def test_tally_meal_count_of_group_when_last_tallied_date_exists(self):
        token = self.login_user()
        self.create_group()
        self.add_users_to_group()
        group = Group.query.get(1)
        self.assertEqual(group.dateLastTallied, None)
        date1 = 'Mon Sep 03 2016 00:01:58 GMT+0800 (Malay Peninsula Standard Time)'
        date2 = 'Mon Sep 04 2016 00:01:58 GMT+0800 (Malay Peninsula Standard Time)'
        group.dateLastTallied = date(2016, 9, 3)
        db.session.commit()
        self.client.post(url_for('meals.add_meal'),
                         headers={'Authorization': 'Bearer ' + token},
                         data=json.dumps({
                             'group_id': 1,
                             'date': date1,
                             'meal_type': 'lunch',
                             'ate': {1: 3, 2: 0},
                             'cooked': 1
                         }),
                         content_type="application/json")

        self.client.post(url_for('meals.add_meal'),
                         headers={'Authorization': 'Bearer ' + token},
                         data=json.dumps({
                             'group_id': 1,
                             'date': date2,
                             'meal_type': 'lunch',
                             'ate': {1: 2, 2: 1},
                             'cooked': 2
                         }),
                         content_type="application/json")
        resp1 = self.client.post(url_for('meals.tally_meal_count_of_group'),
                                 headers={'Authorization': 'Bearer ' + token},
                                 data=json.dumps({
                                     'group_id': 1
                                 }),
                                 content_type="application/json")

        self.assert200(resp1)
        self.assertEqual(resp1.json['1'], 2)
        self.assertEqual(resp1.json['2'], 1)

        group = Group.query.get(1)
        today = date.today()
        self.assertEqual(group.dateLastTallied, today)
