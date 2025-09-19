from flask import render_template
from app import web_app, db

@web_app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@web_app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

