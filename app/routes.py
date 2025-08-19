from app import web_app

@web_app.route("/")
@web_app.route("/index")
def index():
    return "This is the main page"