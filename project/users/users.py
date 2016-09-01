from project.utils import auth
from flask import Blueprint, request
from project import db, session, bcrypt, jsonify
from project.models import User
from sqlalchemy import text
import json

users = Blueprint('users', __name__)


@users.route('/api/login', methods=['POST'])
def login():
    json_data = request.json
    user = User.query.filter_by(email=json_data['email']).first()
    if user and bcrypt.check_password_hash(
            user.password, json_data['password']):
        session['logged_in'] = True
        session['user_id'] = user.id
        token = auth.create_token(user)
        return jsonify({'result': True, "token": token, "username": user.username})
    else:
        return jsonify({'result': False, "token": -1})


@users.route('/api/register', methods=['POST'])
def register():
    """
    For POSTS, create the relevant account
    """
    json_data = request.json
    user = User(
        email=json_data['email'],
        username=json_data['username'],
        password=json_data['password']
    )
    try:
        db.session.add(user)
        db.session.commit()
        status = 'success'
    except:
        status = 'this user is already registered'
    db.session.close()
    return jsonify({'result': status})


@users.route('/api/logout')
@auth.login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return jsonify({'result': 'success'})


@users.route('/api/user_preferences', methods=['GET'])
@auth.login_required
def get_user_preferences():
    uid = session['user_id']
    current_user = User.query.filter_by(id=uid).first()
    return json.dumps({'show_completed_task': current_user.show_completed_task})


@users.route('/api/user_preferences/update_show_task', methods=['POST'])
@auth.login_required
def show_task_toggle():
    uid = session['user_id']
    option = request.json['option']

    # Sqlite limitations
    if option:
        option = "1"
    else:
        option = "0"

    cmd = "UPDATE users SET show_completed_task = " + str(option) + " WHERE id = " + str(uid)
    db.engine.execute(text(cmd))
    return 'OK'
