from flask import render_template, Blueprint
from flask_login import login_required


main = Blueprint("main", __name__)


@main.route("/home")
@login_required
def home():
    return render_template("home.html",
                           page="home")
