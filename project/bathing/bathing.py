from project.utils import auth
from flask import Blueprint, request, redirect, Response, abort
from project import db, session
from project.models import User, Group
from datetime import datetime, date
import jsonpickle
import project.constants as constants

bathing = Blueprint('bathing', __name__)


@bathing.route('/api/bathing', methods=['POST'])
def add_bathing():
    user_id = request.json['user_id']
    user = User.query.get_or_404(user_id)
    now = datetime.now()
    group = Group.query.get_or_404(user.groupID)
    group.currentBathingID = user_id
    group.currentBathingStart = now
    db.session.commit()
    return 'OK'


@bathing.route('/api/check_bathing', methods=['POST'])
def check_bathing():
    user_id = request.json['user_id']
    user = User.query.filter_by(id=user_id).first()
    group_id = user.groupID
    group = Group.query.get_or_404(group_id)
    if group.currentBathingID == constants.DEFAULT_BATHING_ID:
        result = {"bathing": False}
    else:
        user = User.query.get_or_404(group.currentBathingID)
        result = {"bathing": True,
                  "username": user.username,
                  "start": group.currentBathingStart.strftime('%H:%M')}

    return jsonpickle.encode(result)
