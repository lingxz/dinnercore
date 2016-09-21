# project / models.py

import datetime
from project import db, bcrypt
import project.constants as constants


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, default=None)
    admin = db.Column(db.Boolean, default=False)
    groupID = db.Column(db.Integer, default=None, primary_key=True)

    def __init__(self, id, username, groupID=None, admin=False):
        self.id = id
        self.username = username
        self.admin = admin
        self.groupID = groupID

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        return self.id

    def is_anonymous(self):
        """True, as anonymous users are supported."""
        return True


class Meal(db.Model):
    __tablename__ = "meals"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mealType = db.Column(db.String, default=None)
    date = db.Column(db.DateTime)
    groupID = db.Column(db.Integer)
    cost = db.Column(db.Float, default=None)

    def __init__(self, date, groupID, mealType):
        self.date = date
        self.groupID = groupID
        self.mealType = mealType


class MealParticipation(db.Model):
    __tablename__ = "meal_participations"

    mealID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    portions = db.Column(db.Integer)
    cooked = db.Column(db.Boolean, default=False)

    def __init__(self, mealID, userID, date, portions, cooked=False):
        self.mealID = mealID
        self.userID = userID
        self.date = date
        self.portions = portions
        self.cooked = cooked


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    dateLastTallied = db.Column(db.DateTime, default=None)
    currentMealID = db.Column(db.Integer, default=constants.DEFAULT_MEAL_ID)

    def __init__(self, id):
        self.id = id
