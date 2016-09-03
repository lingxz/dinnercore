# project / models.py

import datetime
from project import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    groupID = db.Column(db.Integer, default=None)

    def __init__(self, email, password, username, admin=False, groupID=None):
        self.email = email
        self.password = bcrypt.generate_password_hash(str(password))
        self.registered_on = datetime.datetime.now()
        self.username = username
        self.admin = admin
        self.groupID = groupID

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """True, as anonymous users are supported."""
        return True


class Meal(db.Model):
    __tablename__ = "meals"

    id = db.Column(db.Integer, primary_key=True)
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

    id = db.Column(db.Integer, primary_key=True)
    mealID = db.Column(db.Integer)
    userID = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    cooked = db.Column(db.Boolean, default=False)

    def __init__(self, mealID, userID, date, cooked=False):
        self.mealID = mealID
        self.userID = userID
        self.date = date
        self.cooked = cooked


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    dateLastTallied = db.Column(db.DateTime, default=None)

    def __init__(self, dateLastTallied=None):
        self.dateLastTallied = dateLastTallied