import sqlalchemy as sqla
from flask import render_template, flash, redirect, url_for, request
from app import web_app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post
from app.email import send_password_reset_email
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import timezone, datetime
from typing import cast

@web_app.route('/')
@web_app.route('/home_page', methods=['GET', 'POST'])
def home_page():
    posts = db.session.scalars(sqla.select(Post).order_by(Post.timestamp.desc())).all()
    return render_template('home_page.html', posts=posts)


@web_app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sqla.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page, per_page=web_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None 
    
    return render_template('index.html', title='Explore', posts=posts, next_url=next_url, prev_url=prev_url)


'''
posts by itself is just a object of Pagination class, 
so .items is an attribute which returns rows from database
'''


@web_app.route("/index", methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=str(form.post.data), author=cast(User, current_user))
        db.session.add(post)
        db.session.commit()
        flash('Your post is in public, even tho nobody cares')
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page, per_page=web_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    
    return render_template('index.html', title="Home", 
                           posts=posts.items, form=form, 
                           next_url=next_url, prev_url=prev_url) 


@web_app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen=datetime.now(timezone.utc)
        db.session.commit()


@web_app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        visitor = User(login=str(form.login.data), email=str(form.email.data))
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
        flash(f'Login requested for user {form.login.data}, rememberMe={form.rememberMe.data}')
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

@web_app.route('/user/<login>')
@login_required
def user(login):
    form = EmptyForm()
    visitor = db.first_or_404(sqla.select(User).where(User.login == login))
    posts = db.session.scalars(sqla.select(Post).where(Post.user_id == current_user.id).order_by(Post.timestamp.desc())).all()
    return render_template('user.html', user=visitor, posts=posts, form=form)


@web_app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.login)
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

@web_app.route('/follow/<login>', methods=['POST'])
@login_required
def follow(login):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(sqla.select(User).where(User.login == login))
        if user is None:
            flash(f'User {login} not found')
            return redirect(url_for('index'))
        if current_user.id == user.id: #user and current_user are represented as two different objects in Python,
                                       #meanwhile user.id and current_user.id are specified to point to id of the user
            flash('You can not follow yourself')
            return redirect(url_for('user', login=login))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {login}')
        return redirect(url_for('user', login=login))
    else:
        return redirect(url_for('index')) 

@web_app.route('/unfollow/<login>', methods=['POST'])
@login_required
def unfollow(login):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(sqla.select(User).where(User.login == login))
        if user is None:
            flash (f'User {login} not found')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You can not unfollow yourself')
            return(url_for('user', login=login))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You unfollowed {login}')
        return redirect(url_for('user', login=login))
    else:
        return redirect(url_for('index'))
    
@web_app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sqla.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@web_app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password2.data)
        db.session.commit()
        flash('Your password has been reset')
        return redirect(url_for('home_page'))
    return render_template('reset_password.html', form=form)


