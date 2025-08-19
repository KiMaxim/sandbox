from flask import render_template
from app import web_app

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