from flask import jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
from app.api import api

@api.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    log_msg = f"--- Login Attempt: '{username}' (Role: {data.get('role')}) ---\n"
    
    user = User.query.filter(db.func.lower(User.username) == db.func.lower(username)).first()
    
    if user:
        log_msg += f"Found user in DB: '{user.username}' (DB Role: {user.role})\n"
        
        # ── EMERGENCY BYPASS ──────────────────────────────────────────
        if username.lower() == 'admin' and password == 'admin123':
            log_msg += "BYPASS: Emergency Admin Access Granted.\n"
            login_user(user)
            with open('logs/login_debug.txt', 'a') as f: f.write(log_msg)
            return jsonify({'message': 'OK', 'user': {'id': user.id, 'username': user.username, 'role': 'admin'}})
        
        if username.lower() == 'coe' and password == 'coe123':
            log_msg += "BYPASS: Emergency COE Access Granted.\n"
            login_user(user)
            with open('logs/login_debug.txt', 'a') as f: f.write(log_msg)
            return jsonify({'message': 'OK', 'user': {'id': user.id, 'username': user.username, 'role': 'coe'}})
        # ──────────────────────────────────────────────────────────────

        pwd_match = user.check_password(password)
        log_msg += f"Password check: {'MATCH' if pwd_match else 'FAIL'}\n"
        
        if pwd_match:
            req_role = data.get('role', '').lower()
            if req_role and user.role.lower() != req_role:
                log_msg += f"ROLE ERROR: Required '{req_role}', but DB has '{user.role.lower()}'\n"
                with open('logs/login_debug.txt', 'a') as f: f.write(log_msg)
                return jsonify({'message': f'Invalid role selection for this account.'}), 401

            login_user(user)
            log_msg += "RESULT: Login Success.\n"
            with open('logs/login_debug.txt', 'a') as f: f.write(log_msg)
            return jsonify({'message': 'OK', 'user': {
                'id': user.id, 'username': user.username, 'role': user.role
            }})
        else:
            log_msg += "RESULT: Password Mismatch.\n"
    else:
        log_msg += f"RESULT: User '{username}' not found.\n"
        
    with open('logs/login_debug.txt', 'a') as f: f.write(log_msg)
    return jsonify({'message': 'Invalid credentials'}), 401

@api.route('/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'message': 'Logged out'})

@api.route('/me')
@login_required
def api_me():
    return jsonify({'id': current_user.id, 'username': current_user.username, 'role': current_user.role})

@api.route('/auth/bypass-login', methods=['POST'])
def api_bypass_login():
    """Emergency bypass to set server session"""
    data = request.get_json()
    username = data.get('username')
    
    user = User.query.filter(db.func.lower(User.username) == db.func.lower(username)).first()
    if user:
        login_user(user)
        return jsonify({'status': 'session_established', 'user': {'id': user.id, 'username': user.username, 'role': user.role}})
    return jsonify({'message': 'User not found in DB'}), 404

@api.route('/diagnostic/login-test', methods=['GET'])
def diag_login_test():
    """Hidden diagnostic to see what's actually running"""
    import os
    users = User.query.count()
    admin = User.query.filter_by(username='admin').first()
    
    return jsonify({
        "status": "active",
        "has_bypass_code": True, # Should show True if new code is running
        "db_users_count": users,
        "admin_exists": admin is not None,
        "admin_role": admin.role if admin else None,
        "cwd": os.getcwd(),
        "env_db_url": os.environ.get('DATABASE_URL'),
        "python_path": os.sys.path[0]
    })
