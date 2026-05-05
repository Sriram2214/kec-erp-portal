from flask import jsonify, request
from flask_login import login_required, current_user
from app.models import User
from app import db
from app.api import api

@api.route('/staff', methods=['GET'])
@login_required
def get_staff():
    return jsonify([{
        'id': u.id, 'username': u.username, 'role': u.role
    } for u in User.query.order_by(User.username).all()])

@api.route('/staff', methods=['POST'])
@login_required
def add_staff():
    d = request.get_json()
    if not all([d.get('username'), d.get('password'), d.get('role')]):
        return jsonify({'message': 'All fields required'}), 400
    if User.query.filter_by(username=d['username'].strip()).first():
        return jsonify({'message': 'Username already exists'}), 409
    u = User(username=d['username'].strip(), role=d['role'])
    u.set_password(d['password'])
    db.session.add(u)
    db.session.commit()
    return jsonify({'message': 'User created', 'id': u.id}), 201

@api.route('/staff/<int:uid>', methods=['DELETE'])
@login_required
def delete_staff(uid):
    if uid == current_user.id:
        return jsonify({'message': 'Cannot delete yourself'}), 400
    u = User.query.get_or_404(uid)
    db.session.delete(u)
    db.session.commit()
    return jsonify({'message': 'Deleted'})
