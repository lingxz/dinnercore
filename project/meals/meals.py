from project.utils import auth
from flask import Blueprint, request, redirect
from project import db, session
from project.models import User, Meal, MealParticipation, Group
from sqlalchemy import text, func
from datetime import datetime, date
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


@meals.route('/add_meal', methods=['POST'])
@auth.login_required
def add_meal():
    group_id = request.json['group_id']
    date_string = request.json['date']
    date = datetime.strptime(date_string, '%a %b %d %Y %H:%M:%S GMT%z (%Z)')
    meal_type = request.json['meal_type']

    meal_id = create_meal(date, group_id, meal_type)

    mps = request.json['ate']
    cooked = request.json['cooked']
    for user_id in mps:
        portions = mps[user_id]
        if user_id == cooked:
            add_user_to_meal(user_id, meal_id, portions, True)
        else:
            add_user_to_meal(user_id, meal_id, portions, False)
    return 'OK'


@meals.route('/get_meal_count_of_user_by_date', methods=['POST'])
@auth.login_required
def get_meal_count_of_user_by_date():
    user_id = request.json['user_id']
    date_string = request.json['date']
    date = func.date(datetime.strptime(date_string, '%a %b %d %Y %H:%M:%S GMT%z (%Z)'))
    mps = MealParticipation.query.filter(func.date(MealParticipation.date) == date,
                                         MealParticipation.userID == user_id).all()
    count = sum(mp.portions for mp in mps)
    return json.dumps({'count': count})


# @meals.route('/get_meal_count', methods=['POST'])
# def get_meal_count():
#     # get meal count of user in the group from last tallied date till now
#     user_id = request.json['user_id']
#     group_id = request.json['group_id']
#     group = Group.query.get(group_id)
#     last_talied = group.dateLastTallied
#     today = date.today()



def create_meal(date, group_id, meal_type):
    meal = Meal(date, group_id, meal_type)
    db.session.add(meal)
    db.session.commit()
    return meal.id


def add_user_to_meal(user_id, meal_id, portions, cooked=False):
    meal = Meal.query.get(meal_id)
    date = meal.date
    mp = MealParticipation(meal_id, user_id, date, portions, cooked)
    db.session.add(mp)
    db.session.commit()
