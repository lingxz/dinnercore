import json
from flask import Flask, request, redirect, jsonify, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from project.config import BaseConfig
from datetime import datetime

# config
app = Flask(__name__)
app.config.from_object(BaseConfig)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# Import after to avoid circular dependency
from project.models import *
from project.utils import auth

# Import routes
from project.users import users
from project.meals import meals
from project.bathing import bathing

# Register the routes, this looks weird but it necessary to register the blueprint object
app.register_blueprint(users.users)
app.register_blueprint(meals.meals)
app.register_blueprint(bathing.bathing)


@app.route('/')
def index():
    return 'hello world'


if __name__ == "__main__":
    app.run(host='0.0.0.0')
