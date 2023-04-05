from flask import Blueprint

import math
import time

from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user

from flasktest import db, bcrypt, GMAIL_EMAIL, HOTMAIL_EMAIL
from flasktest.models import User, APIData
from flasktest.users.forms import RegisterForm, LoginForm, EmailForm, ResetForm
from flasktest.users.utils import send_reset_password_mail, add_new_user, do_passwords_match, \
    change_password
from flasktest.apis.utils import remove_pubg_images


users = Blueprint("users", __name__)


@users.route("/")
def index():
    return redirect("login")


@users.route("/fresh")
def base():
    """Create two dummy accounts and API defaults after db reset"""
    hashed_password = bcrypt.generate_password_hash("test1234")
    add_new_user(email=HOTMAIL_EMAIL, username="test1", hashed_password=hashed_password)
    add_new_user(email=GMAIL_EMAIL, username="test2", hashed_password=hashed_password)
    pubg_api = APIData(api_name="pubg", last_used=math.floor(time.time()), timer=60)
    db.session.add(pubg_api)
    db.session.commit()
    return redirect(url_for("users.login"))


@users.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    register_form = RegisterForm()

    if request.method == "GET":
        return render_template("/landing/login.html",
                               login_form=login_form,
                               register_form=register_form)

    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()

        if not do_passwords_match(user.password, login_form.password.data):
            flash("Password incorrect.")

        else:
            # Login successful
            login_user(user, remember=True)
            session["id"] = user.id
            return redirect(url_for("main.home"))

    # Unsuccessful attempts
    return render_template("/landing/login.html",
                           login_form=login_form,
                           register_form=register_form)


@users.route("/logout")
@login_required
def logout():
    remove_pubg_images(session["id"])
    logout_user()
    return redirect(url_for("users.login"))


@users.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm()

    if request.method == "GET":
        return render_template("/landing/register.html",
                               register_form=register_form)

    if register_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(register_form.password.data)
        add_new_user(
            email=register_form.email.data,
            username=register_form.username.data,
            hashed_password=hashed_password,
            )
        return redirect(url_for("users.login"))

    # Form not validated
    return render_template("/landing/register.html",
                           register_form=register_form)


@users.route("/request-reset", methods=["GET", "POST"])
def request_reset():
    email_form = EmailForm()

    if request.method == "GET":
        return render_template("/landing/request_reset.html",
                               email_form=email_form)

    # Request reset attempt
    if email_form.validate_on_submit():
        user = User.query.filter_by(email=email_form.email.data).first()

        send_reset_password_mail(user)
        flash("Code hes been send!")
        return redirect(url_for("users.enter_reset"))

    # Request reset form not validated
    return render_template("/landing/request_reset.html",
                           email_form=email_form)


@users.route("/enter-reset", methods=["GET", "POST"])
def enter_reset():
    reset_form = ResetForm()

    if request.method == "GET":
        return render_template("/landing/enter_reset.html",
                               reset_form=reset_form)

    # Reset attempt
    if reset_form.validate_on_submit():
        user = User.query.filter_by(email=reset_form.email.data).first()

        if bcrypt.check_password_hash(user.reset_key, str(reset_form.reset_code.data)):
            # Correct code
            hashed_password = bcrypt.generate_password_hash(str(reset_form.password.data))
            change_password(user.id, hashed_password)
            return redirect("login")

        else:
            # Incorrect code
            flash("Incorrect email or code!")
            return render_template("/landing/enter_reset.html",
                                   reset_form=reset_form)

    # Enter reset form not validated
    return render_template("/landing/enter_reset.html",
                           reset_form=reset_form)
