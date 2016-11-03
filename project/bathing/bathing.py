from project.utils import auth
from flask import Blueprint, request, redirect, Response, abort
from project import db, session
from project.models import User, Group
from datetime import datetime, date
import json
import jsonpickle
import project.constants as constants
from werkzeug.exceptions import NotFound

bathing = Blueprint('bathing', __name__)


@bathing.route('/api/start_bathing', methods=['POST'])
def start_bathing():
    user_id = request.json['user_id']
    group_id = request.json['group_id']
    try:
        user = User.query.get_or_404((user_id, group_id))
    except NotFound:
        users = User.query.filter_by(id=user_id).all()
        if len(users) == 0:
            abort(404)
        elif len(users) != 1:
            abort(400)
        else:
            user = users[0]
            group_id = user.groupID

    group = Group.query.get_or_404(group_id)
    if group.currentBathingID == user_id:
        return json.dumps({"other_person": False, "same_person": True})
    elif group.currentBathingID != constants.DEFAULT_BATHING_ID:
        return json.dumps({"other_person": True, "same_person": False})
    else:
        group.currentBathingID = user_id
        group.currentBathingStart = now
        db.session.commit()
        return json.dumps({"other_person": False, "same_person": False})


@bathing.route('/api/stop_bathing', methods=['POST'])
def stop_bathing():
    user_id = request.json['user_id']
    group_id = request.json['group_id']
    try:
        user = User.query.get_or_404((user_id, group_id))
    except NotFound:
        users = User.query.filter_by(id=user_id).all()
        if len(users) == 0:
            abort(404)
        elif len(users) != 1:
            abort(400)
        else:
            user = users[0]
            group_id = user.groupID

    group = Group.query.get_or_404(group_id)
    if group.currentBathingID == constants.DEFAULT_BATHING_ID:
        return json.dumps({'bathing': False})
    elif group.currentBathingID != user_id:
        return json.dumps({'bathing': True, 'correct_person': False})
    else:
        group.currentBathingID = constants.DEFAULT_BATHING_ID
        group.currentBathingStart = None
        db.session.commit()
        return json.dumps({'bathing': True, 'correct_person': True})


@bathing.route('/api/check_bathing', methods=['POST'])
def check_bathing():
    user_id = request.json['user_id']
    group_id = request.json['group_id']
    try:
        user = User.query.get_or_404((user_id, group_id))
    except NotFound:
        users = User.query.filter_by(id=user_id).all()
        # not registered
        if len(users) == 0:
            abort(404)
        # in multiple groups
        elif len(users) != 1:
            abort(400)
        else:
            user = users[0]
            group_id = user.groupID

    group = Group.query.get_or_404(group_id)
    if group.currentBathingID == constants.DEFAULT_BATHING_ID:
        result = {"bathing": False}
    else:
        user = User.query.filter_by(id=group.currentBathingID, groupID=group_id).first()
        result = {"bathing": True,
                  "username": user.username,
                  "start": group.currentBathingStart.strftime('%H:%M')}

    return jsonpickle.encode(result)
