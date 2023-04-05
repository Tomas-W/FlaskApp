import random

from flask_mail import Message

from flasktest import mail, bcrypt, db, GMAIL_EMAIL
from flasktest.models import User, CountriesData


def add_new_user(email, username, hashed_password, reset_key=000000):
    """
    Takes register_form input data and creates a new user with default settings.
    """
    # noinspection PyArgumentList
    new_user = User(
        email=email,
        username=username,
        password=hashed_password,
        reset_key=reset_key,
    )
    db.session.add(new_user)
    db.session.commit()

    countries_data = add_new_countries(user_id=new_user.id)
    db.session.add(countries_data)
    db.session.commit()


def add_new_countries(user_id):
    """
    Takes a user_id(int).
    Returns a new_country(class) for the Countries game.
    """
    new_countries = CountriesData(
        user_id=user_id,
        country_old=random.randint(1, 30),
        country_new=random.randint(1, 30),
        country_streak=0,
        country_record=0,
    )
    return new_countries


def do_passwords_match(user_password, form_password):
    """
    Compares users password (str) with LoginForm password (str).
    Returns True or False.
    """
    if bcrypt.check_password_hash(user_password, form_password):
        return True
    return False


def change_password(user_id, hashed_password):
    """
    Takes a user_id(int) and a hashed_password(str)
    Updates the password in the database.
    """
    user = User.query.get(user_id)
    user.password = hashed_password
    user.reset_key = None
    db.session.commit()


def send_reset_password_mail(user):
    reset_code = str(random.randint(100000, 999999))
    user.reset_key = bcrypt.generate_password_hash(reset_code)
    db.session.commit()
    message = Message(subject="Password reset request",
                      sender=GMAIL_EMAIL,
                      recipients=[user.email])
    message.body = f"""Your reset code: {reset_code}"""
    mail.send(message=message)
