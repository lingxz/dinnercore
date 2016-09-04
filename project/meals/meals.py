from project.utils import auth
from flask import Blueprint, request, redirect
from project import db, session
from project.models import User, Meal, MealParticipation, Group
from sqlalchemy import text
from datetime import datetime
import json

meals = Blueprint('meals', __name__)


@meals.route('/add_group', methods=['POST'])
@auth.login_required
def add_group():
    name = request.json['name']
    new_group = Group(name)
    db.session.add(new_group)
    db.session.commit()
    return 'OK'


@meals.route('/add_user_to_group', methods=['POST'])
@auth.login_required
def add_user_to_group():
    user_id = request.json['user_id']
    group_id = request.json['group_id']
    current_user = User.query.get(user_id)
    current_user.groupID = group_id
    db.session.commit()
    return 'OK'

