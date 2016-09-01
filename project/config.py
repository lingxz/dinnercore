# project/config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    SECRET_KEY = 'my_precious'
    DEBUG = True
    TESTING = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestConfig(object):
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    BCRYPT_LOG_ROUNDS = 1
