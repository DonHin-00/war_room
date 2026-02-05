from flask import Blueprint, render_template, session, redirect, url_for
from ..core.models import Transaction
import logging

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger('admin')

@admin_bp.route('/ledger')
def ledger():
    if 'role' not in session or session['role'] != 'admin':
        return "Access Denied", 403

    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(100).all()
    return render_template('ledger.html', transactions=transactions)
