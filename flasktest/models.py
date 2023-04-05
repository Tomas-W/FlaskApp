from flask_login import UserMixin

from flasktest import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))


# ------------------------------------------------------------- #
# ------------------------- USER ------------------------------ #
# TODO: Generate fake users data
class User(db.Model, UserMixin):
    """
    Stores the User login data and their relationships.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(75), unique=True, nullable=False)
    username = db.Column(db.String(75), unique=False, nullable=False)
    password = db.Column(db.String(75), unique=False, nullable=False)
    reset_key = db.Column(db.String(75), unique=False, nullable=True)
    # relationships
    countries_games = db.relationship("CountriesData", backref="countries_user")
    wordle_games = db.relationship("WordleData", backref="wordle_user")
    numbers_games = db.relationship("NumbersData", backref="numbers_user")
    image_adjust_data = db.relationship("ImageAdjustData", backref="image_adjust_user")

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"


# ------------------------------------------------------------------ #
# ------------------------- COUNTRIES ------------------------------ #
class CountriesData(db.Model):
    """
    Stores Users info on Countries game.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # relationship
    country_old = db.Column(db.Integer, unique=False, nullable=True)
    country_new = db.Column(db.Integer, unique=False, nullable=True)
    country_streak = db.Column(db.Integer, unique=False, nullable=True)
    country_record = db.Column(db.Integer, unique=False, nullable=True)

    def __repr__(self):
        return f"CountriesData(id={self.id}, user_id={self.user_id}," \
               f" country_old={self.country_old}, country_new={self.country_new}," \
               f" country_streak={self.country_streak}, country_record={self.country_record})"


# --------------------------------------------------------------- #
# ------------------------- WORDLE ------------------------------ #
class WordleData(db.Model):
    """
    Stores Users info on Wordle game.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # relationship
    wordle_answer = db.Column(db.String(100), unique=False, nullable=True)
    wordle_round = db.Column(db.Integer, unique=False, nullable=True)
    wordle_guess1 = db.Column(db.String(100), unique=False, nullable=True)
    wordle_guess2 = db.Column(db.String(100), unique=False, nullable=True)
    wordle_guess3 = db.Column(db.String(100), unique=False, nullable=True)
    wordle_guess4 = db.Column(db.String(100), unique=False, nullable=True)
    wordle_guess5 = db.Column(db.String(100), unique=False, nullable=True)
    wordle_win_round = db.Column(db.Integer, unique=False, nullable=True)
    wordle_game_state = db.Column(db.String(10), unique=False, nullable=True)

    def __repr__(self):
        return f"WordleData(id={self.id}, user_id={self.user_id}," \
               f"game_state={self.wordle_game_state}, answer={self.wordle_answer})"


# ---------------------------------------------------------------- #
# ------------------------- NUMBERS ------------------------------ #
class NumbersData(db.Model):
    """
    Stores Users info on Numbers game.
    """
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # relationship
    numbers_start = db.Column(db.Float(), nullable=False)
    numbers_stop = db.Column(db.Float(), nullable=True, default=-1)
    numbers_time = db.Column(db.Float(), nullable=True, default=-1)

    def __repr__(self):
        return f"NumbersData(id={self.id}, user_id={self.user_id}," \
               f" numbers_time={self.numbers_time})"


# ------------------------------------------------------------ #
# ------------------------- API ------------------------------ #
class APIData(db.Model):
    """
    Stores pubg api availability.
    """
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(30), unique=True, nullable=False)
    last_used = db.Column(db.Integer, unique=False, nullable=True)
    timer = db.Column(db.Integer, unique=False, nullable=True)

    def __repr__(self):
        return f"APIData(id={self.id}, api_name={self.api_name}," \
               f" last_used={self.last_used}, timer={self.timer})"


# --------------------------------------------------------------------- #
# ------------------------- IMAGE ADJUST ------------------------------ #
class ImageAdjustData(db.Model):
    """
    Stores Users info on image adjust.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # relationship
    filetype = db.Column(db.String, unique=False, nullable=True)
    old_image = db.Column(db.String, unique=False, nullable=True)
    new_image = db.Column(db.String, unique=False, nullable=True)

    def __repr__(self):
        return f"ImageAdjustData(id={self.id}, user_id={self.user_id}," \
               f" filetype={self.filetype}, old_image={self.old_image}," \
               f"new_image={self.new_image})"
