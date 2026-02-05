from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from ..core.db import db
from ..core.models import User
from ..forms import LoginForm
from irondome.analyzer import IdentityDefense
from ..core.extensions import limiter
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger('auth')
identity_defense = IdentityDefense()

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("60 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # SOC Check
        if not identity_defense.check_login(username, request.remote_addr):
            flash('Login blocked by security policy.')
            return render_template('login.html', form=form)

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            logger.info(f"User {username} logged in successfully.")
            return redirect(url_for('banking.dashboard'))
        else:
            logger.warning(f"Failed login attempt for {username} from {request.remote_addr}")
            flash('Invalid credentials')

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}")

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
