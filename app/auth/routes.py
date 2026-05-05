from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db, limiter
from app.auth import auth_bp
from app.models import User
from app.utils.logger import audit_log
import logging

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            audit_log.log("LOGIN_FAILED", {"username": username, "ip": request.remote_addr})
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
            
        login_user(user)
        audit_log.log("LOGIN_SUCCESS", {"role": user.role})
        return redirect(url_for('core.dashboard'))
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    audit_log.log("LOGOUT")
    logout_user()
    return redirect(url_for('auth.login'))
