from project.utils import auth
from flask import Blueprint, request, redirect, Response, abort
from project import db, session
from project.models import User, Meal, MealParticipation, Group
from sqlalchemy import text
from datetime import datetime, date
import json
import jsonpickle
import project.constants as constants

meals = Blueprint('meals', __name__)


@meals.route('/api/eating', methods=['POST'])
def update_meal_participation():
    user_id = request.json['user_id']
    group_id = request.json['group']
    portions = request.json['portions']
    cooked = request.json['cooked']

    group = Group.query.get_or_404(group_id)

    # Check if there is no meal
    if not has_active_meal(group):
        abort(400)

    add_user_to_meal(
        user_id=user_id,
        meal_id=group.currentMealID,
        portions=portions,
        cooked=cooked
    )

    return 'OK'


# for adding chef after meal has ended
@meals.route('/api/add_chef', methods=['POST'])
def add_chef():
    meal_id = request.json['meal_id']
    user_id = request.json['user_id']
    mp = MealParticipation.query.filter(MealParticipation.mealID == meal_id,
                                        MealParticipation.userID == user_id).first()
    if mp:
        mp.cooked = True
        db.session.commit()
    else:
        add_user_to_meal(user_id=user_id,
                         meal_id=meal_id,
                         portions=0,
                         cooked=True)
    return 'OK'


@meals.route('/api/remove_chef', methods=['POST'])
def remove_chef():
    meal_id = request.json['meal_id']
    user_id = request.json['user_id']
    mp = MealParticipation.query.filter(MealParticipation.mealID == meal_id,
                                        MealParticipation.userID == user_id).first()
    if not mp:
        abort(404)

    mp.cooked = False
    db.session.commit()
    return 'OK'


# for adding / changing after a meal has ended
@meals.route('/api/change_portions')
def add_eater():
    meal_id = request.json['meal_id']
    user_id = request.json['user_id']
    portions = request.json['portions']
    mp = MealParticipation.query.filter(MealParticipation.mealID == meal_id,
                                        MealParticipation.userID == user_id).first()
    if mp:
        mp.portions = portions
        db.session.commit()
    else:
        add_user_to_meal(user_id=user_id,
                         meal_id=meal_id,
                         portions=portions,
                         cooked=False)
    return 'OK'


@meals.route('/api/add_meal', methods=['POST'])
def add_meal():
    group_id = request.json['group']
    meal_type = request.json['meal_type']
    date = datetime.now()

    group = Group.query.get_or_404(group_id)

    # Check if a meal is running
    if has_active_meal(group):
        abort(400)

    # Create meal and update the group
    meal_id = create_meal(date, group_id, meal_type)
    group.currentMealID = meal_id
    db.session.commit()
    return 'OK'


@meals.route('/api/end_meal', methods=['POST'])
def end_meal():
    group_id = request.json['group']
    group = Group.query.get_or_404(group_id)
    group.currentMealID = constants.DEFAULT_MEAL_ID
    db.session.commit()
    return 'OK'


@meals.route('/api/register_group', methods=['POST'])
def add_group():
    group_id = request.json['group']
    new_group = Group(group_id)
    try:
        db.session.add(new_group)
        db.session.commit()
        db.session.close()
        return 'OK'
    except:
        db.session.close()
        abort(400)


@meals.route('/api/meal_info', methods=['POST'])
def meal_info():
    group_id = request.json['group']
    group = Group.query.get_or_404(group_id)

    meal_id = request.json['meal_id']
    if meal_id == constants.DEFAULT_MEAL_ID:
        meal_id = group.currentMealID

    meal_participations = MealParticipation.query.filter_by(
        mealID=meal_id
    ).all()

    ret = []
    for mp in meal_participations:
        user = User.query.filter_by(
            id=mp.userID,
            groupID=group_id
        ).first()
        ret.append({
            'user_name': user.username,
            'portions': mp.portions,
            'cooked': mp.cooked
        })

    return jsonpickle.encode(ret)


@meals.route('/api/meals', methods=['POST'])
def get_meals():
    group_id = request.json['group']
    n = request.json['number']
    last_n_meals = Meal.query.filter(Meal.groupID == group_id).order_by(Meal.date.desc()).limit(n).all()
    result = []
    for meal in last_n_meals:
        mps = MealParticipation.query.filter(MealParticipation.mealID == meal.id).all()
        count = sum(mp.portions for mp in mps)
        result.append([meal.id, count])
    return jsonpickle.encode(result)


# @meals.route('/add_user_to_group', methods=['POST'])
# def add_user_to_group():
#     user_id = request.json['user_id']
#     group_id = request.json['group_id']
#     # to check whether the group exists
#     group = Group.query.get_or_404(group_id)
#     current_user = User.query.get(user_id)
#     current_user.groupID = group_id
#     db.session.commit()
#     return 'OK'


@meals.route('/get_meal_count_of_user_by_date', methods=['POST'])
def get_meal_count_of_user_by_date():
    user_id = request.json['user_id']
    date_string = request.json['date']
    date = datetime.strptime(date_string, '%a %b %d %Y %H:%M:%S GMT%z (%Z)').date()
    mps = MealParticipation.query.filter(MealParticipation.date == date,
                                         MealParticipation.userID == user_id).all()
    count = sum(mp.portions for mp in mps)
    return json.dumps({'count': count})


@meals.route('/tally_meal_count_of_user', methods=['POST'])
def tally_meal_count_of_user():
    # get meal count of user in the group from last tallied date till now
    user_id = request.json['user_id']
    group_id = request.json['group_id']
    count = get_meal_count_for_user(user_id, group_id)
    return json.dumps({'count': count})


@meals.route('/api/tally_group', methods=['POST'])
def tally_meal_count_of_group():
    group_id = request.json['group']
    set_date = request.json['set_date']

    # check whether group exists
    group = Group.query.get_or_404(group_id)

    users = User.query.filter(User.groupID == group_id).all()
    if not users:
        users = []

    user_to_counts = {}
    for user in users:
        count = get_meal_count_for_user(user.id, group_id)
        user_to_counts[user.username] = count

    if set_date:
        now = datetime.now()
        set_last_tallied_date(group_id, now)

    return json.dumps(user_to_counts)


@meals.route('/api/tally_user', methods=['POST'])
def tally_user():
    user_id = request.json['user_id']
    group_id = request.json['group']
    group = Group.query.get_or_404(group_id)
    last_tallied = group.dateLastTallied
    if last_tallied:
        meals = Meal.query.filter(Meal.groupID == group_id, Meal.date > last_tallied).all()
    else:
        meals = Meal.query.filter(Meal.groupID == group_id).all()
    meal_ids = [meal.id for meal in meals]
    mps = MealParticipation.query.filter(MealParticipation.mealID.in_(meal_ids),
                                         MealParticipation.userID == user_id).all()
    result = []

    for mp in mps:
        meal = Meal.query.get(mp.mealID)
        result.append({'mealID': mp.mealID, 'date': mp.date.strftime('%d %b'), 'type': meal.mealType})
    return jsonpickle.encode(result)


def get_meal_count_for_user(user_id, group_id):
    # TODO: get only the meals in the group
    group = Group.query.get(group_id)
    last_tallied = group.dateLastTallied
    if last_tallied:
        meals = Meal.query.filter(Meal.groupID == group_id, Meal.date > last_tallied).all()
        meal_ids = [meal.id for meal in meals]
        mps = MealParticipation.query.filter(MealParticipation.mealID.in_(meal_ids),
                                             MealParticipation.userID == user_id)
    else:
        meals = Meal.query.filter(Meal.groupID == group_id).all()
        meal_ids = [meal.id for meal in meals]
        mps = MealParticipation.query.filter(MealParticipation.mealID.in_(meal_ids),
                                             MealParticipation.userID == user_id)

    count = sum(mp.portions for mp in mps)
    return count


def create_meal(date, group_id, meal_type):
    meal = Meal(date, group_id, meal_type)
    db.session.add(meal)
    db.session.commit()
    return meal.id


def add_user_to_meal(user_id, meal_id, portions, cooked=False):
    meal = Meal.query.get(meal_id)
    meal_date = meal.date

    # Search for existing meal participation
    meal_participation = MealParticipation.query.filter_by(
        mealID=meal_id,
        userID=user_id
    ).first()

    if meal_participation:
        if portions == 0:
            db.session.delete(meal_participation)
        else:
            meal_participation.portions = portions
            meal_participation.cooked = cooked
        db.session.commit()
        return

    if portions > 0:
        mp = MealParticipation(meal_id, user_id, meal_date, portions, cooked)
        db.session.add(mp)

    db.session.commit()


def set_last_tallied_date(group_id, date):
    group = Group.query.get(group_id)
    group.dateLastTallied = date
    db.session.commit()


def has_active_meal(group):
    return group.currentMealID != constants.DEFAULT_MEAL_ID
