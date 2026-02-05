from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from ..core.db import db
from ..core.models import User, Transaction
from ..forms import TransferForm
from irondome.analyzer import FraudDetector
from ..core.extensions import limiter
import logging

banking_bp = Blueprint('banking', __name__)
logger = logging.getLogger('banking')
fraud_detector = FraudDetector()

@banking_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    transactions = Transaction.query.filter((Transaction.sender_id == user.id) | (Transaction.receiver_id == user.id)).order_by(Transaction.timestamp.desc()).limit(10).all()

    return render_template('dashboard.html', user=user, transactions=transactions)

@banking_bp.route('/transfer', methods=['GET', 'POST'])
@limiter.limit("60 per minute")
def transfer():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    form = TransferForm()
    if form.validate_on_submit():
        sender = User.query.get(session['user_id'])
        recipient_acc = form.recipient.data
        amount = form.amount.data

        recipient = User.query.filter_by(account_number=recipient_acc).first()

        if not recipient:
            flash('Recipient not found')
        elif amount > sender.balance:
            flash('Insufficient funds')
        else:
            # SOC Check
            if not fraud_detector.check_transaction(sender.id, amount):
                 flash('Transaction flagged for security review.')
                 logger.warning(f"Transaction blocked by IronDome: {sender.username} -> {amount}")
                 return redirect(url_for('banking.dashboard'))

            sender.balance -= amount
            recipient.balance += amount

            tx = Transaction(sender_id=sender.id, receiver_id=recipient.id, amount=amount, description="Online Transfer")
            db.session.add(tx)
            db.session.commit()

            logger.info(f"Transfer successful: {sender.username} sent {amount} to {recipient.username}")
            flash('Transfer successful')
            return redirect(url_for('banking.dashboard'))

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}")

    return render_template('transfer.html', form=form)
