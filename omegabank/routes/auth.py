from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from ..core.db import db
from ..core.models import User
from irondome.analyzer import IdentityDefense
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger('auth')
identity_defense = IdentityDefense()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')

        # SOC Check
        if not identity_defense.check_login(username, request.remote_addr):
            flash('Login blocked by security policy.')
            return render_template('login.html')

        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            logger.info(f"User {username} logged in successfully.")
            return redirect(url_for('banking.dashboard'))
        else:
            logger.warning(f"Failed login attempt for {username} from {request.remote_addr}")
            flash('Invalid credentials')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
