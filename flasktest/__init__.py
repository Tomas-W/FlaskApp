"""
Initializes the FlaskApp.

Sets general app settings as well as private variables.
"""
import os

from flask import Flask
from flask_mail import Mail
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect

# TODO: Create navbar
# TODO: Clean up Home page - Fix animations with JavaScript
# TODO: Create error pages
# TODO:
# Get base path
BASE_PATH = os.getcwd()
# Flask secret key
FLASK_KEY = os.environ["FLASK_KEY"]
# API keys
PUBG_API_KEY = os.environ["PUBG_API_KEY"]
# FlaskMail keys ( email only used for dummy accounts at @users.route("/fresh") )
GMAIL_EMAIL = os.environ["GMAIL_EMAIL"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
GMAIL_SMTP = os.environ["GMAIL_SMTP"]
# Hotmail email ( email only used for dummy accounts at @users.route("/fresh") )
HOTMAIL_EMAIL = os.environ["HOTMAIL_EMAIL"]

# App settings
app = Flask(__name__)
app.config["SECRET_KEY"] = FLASK_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_PATH}\\flasktest\\databases\\website_database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
# FlaskMail settings
app.config["MAIL_SERVER"] = GMAIL_SMTP
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_'DEBUG'"] = app.debug
app.config["MAIL_USERNAME"] = GMAIL_EMAIL
app.config["MAIL_PASSWORD"] = GMAIL_PASS

# Load helpers
mail = Mail(app)
csrf = CSRFProtect(app)
csrf.init_app(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
Bootstrap(app)

# Set login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"

# Prevent circular import
from flasktest.users.routes import users  # noqa: E402
from flasktest.main.routes import main  # noqa: E402
from flasktest.apis.routes import apis  # noqa: E402
from flasktest.games.routes import games  # noqa: E402
from flasktest.tools.routes import tools  # noqa: E402

# Register Blueprints
app.register_blueprint(users)
app.register_blueprint(main)
app.register_blueprint(apis)
app.register_blueprint(games)
app.register_blueprint(tools)

# If no database exists yet, create it
with app.app_context():
    if not os.path.exists(f"{BASE_PATH}\\flasktest\\databases\\website_database.db"):
        db.create_all()
