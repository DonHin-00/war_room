from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64),
        Regexp(r'^[a-zA-Z0-9_]+$', message="Username must contain only letters, numbers, and underscores")
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TransferForm(FlaskForm):
    recipient = StringField('Recipient Account Number', validators=[
        DataRequired(),
        Regexp(r'^ACC-\d{4}$', message="Invalid format. Use ACC-XXXX")
    ])
    amount = FloatField('Amount', validators=[
        DataRequired(),
        NumberRange(min=0.01, message="Amount must be positive")
    ])
    submit = SubmitField('Send Funds')
