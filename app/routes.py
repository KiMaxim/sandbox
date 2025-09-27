from flask import render_template, flash, redirect, url_for, request
from app import web_app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User, Post
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sqla
from urllib.parse import urlsplit
from datetime import timezone, datetime


@web_app.route("/")
@web_app.route("/index")
@login_required
def index():
    posts = db.session.scalars(sqla.select(Post)).all()
    return render_template("index.html", title="Home", posts=posts)

@web_app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen=datetime.now(timezone.utc)
        db.session.commit()


@web_app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm(current_user.login)
    if form.validate_on_submit():
        visitor = User(login=form.login.data, email=form.email.data) #type: ignore
        visitor.set_password(form.password.data)
        db.session.add(visitor)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@web_app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        visitor = db.session.scalar(sqla.select(User).where(User.login == form.login.data))
        if visitor is None or not visitor.check_password(form.password.data):
            flash('Invalid login or password')
            return redirect(url_for('login'))
        flash('Login requested for user {}, remmberMe={}'.format(form.login.data, form.rememberMe.data))
        login_user(visitor, remember=form.rememberMe.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template("login.html", title="Login", form=form)

@web_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@web_app.route('/user/<username>')
@login_required
def user(username):
    visitor = db.first_or_404(sqla.select(User).where(User.login == username))
    posts = [
        {"author": user, "body": "Test post 1"},
        {"author": user, "body": "Test post 2"}
    ]
    return render_template('user.html', user=visitor, posts=posts)


@web_app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.login = form.login.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.login.data = current_user.login
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)
