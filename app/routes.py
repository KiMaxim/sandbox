from flask import render_template, flash, redirect, url_for
from app import web_app
from app.forms import LoginForm

@web_app.route("/")
@web_app.route("/index")
def index():
    user = {"login": "maxim"}
    posts = [
        {
            'author': {'login': 'max'},
            'message': 'Overkills is fine'
        },
        {
            'author': {'login': 'kim'},
            'message': 'Stay down till you come up'
        }
    ]
    return render_template("index.html", title="Home", username=user, posts=posts)

@web_app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remmberMe={}'.format(form.login.data, form.rememberMe.data))
        return redirect(url_for('index'))
    return render_template("login.html", title="Login", form=form)