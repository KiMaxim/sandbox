from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length
from app import db
import sqlalchemy as sqla
from app.models import User

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    rememberMe = BooleanField('Remember Me')
    submit = SubmitField('Sign in')

class RegistrationForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_login(self, login):
        if login.data != self.original_username:
            visitor = db.session.scalar(sqla.select(User).where(User.login == login.data))
            if visitor is not None:
                raise ValidationError('Use a different a login, this on is taken')

    def validate_email(self, email):
        visitor = db.session.scalar(sqla.select(User).where(User.email == email.data))
        if visitor is not None:
            raise ValidationError('Use a different a email, this on is taken')
     
class EditProfileForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
        