from project.utils import auth
from flask import Blueprint, request, abort
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
        id=json_data['id'],
        username=json_data['username'],
        groupID=json_data['groupID']
    )
    try:
        db.session.add(user)
        db.session.commit()
        db.session.close()
        return 'OK'
    except:
        db.session.close()
        abort(400)


@users.route('/api/logout')
@auth.login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return jsonify({'result': 'success'})
