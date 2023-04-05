import time

from flask import render_template, request, session, Blueprint
from flask_login import login_required

from flasktest import db
from flasktest.models import CountriesData, WordleData, NumbersData
from flasktest.games.forms import CountryForm, WordleForm, NumbersForm
from flasktest.games.utils import get_country_name, get_country_size, get_country_path, \
    evaluate_countries_game, create_numbers_divs, start_new_wordle, get_last_wordle_guess, \
    play_wordle_game

games = Blueprint("games", __name__)


# ------------------------------------------------------------------ #
# ------------------------- COUNTRIES ------------------------------ #
@games.route("/games/countries", methods=["GET", "POST"])
@login_required
def countries():
    # TODO: Connect database and add highscores countries
    country_form = CountryForm()
    # Get users last game positions from the database
    countries_data = CountriesData.query.filter_by(user_id=session["id"]).first()

    if request.method == "GET":
        return render_template("/games/countries.html",
                               country_form=country_form,
                               name1=get_country_name(countries_data.country_old),
                               size1=get_country_size(countries_data.country_old),
                               path1=get_country_path(countries_data.country_old),
                               name2=get_country_name(countries_data.country_new),
                               size2=get_country_size(countries_data.country_new),
                               path2=get_country_path(countries_data.country_new),
                               country_streak=countries_data.country_streak,
                               page="countries",
                               country_record=countries_data.country_record)

    if country_form.validate_on_submit():
        # Take user guess and apply game logic
        guess = country_form.select.data
        countries_data = evaluate_countries_game(guess=guess, user_id=session["id"])

        return render_template("/games/countries.html",
                               country_form=country_form,
                               name1=get_country_name(countries_data.country_old),
                               size1=get_country_size(countries_data.country_old),
                               path1=get_country_path(countries_data.country_old),
                               name2=get_country_name(countries_data.country_new),
                               size2=get_country_size(countries_data.country_new),
                               path2=get_country_path(countries_data.country_new),
                               country_streak=countries_data.country_streak,
                               country_record=countries_data.country_record,
                               page="countries",
                               scrollToAnchor="game-section")


# --------------------------------------------------------------- #
# ------------------------- WORDLE ------------------------------ #
@games.route("/games/wordle", methods=["POST", "GET"])
@login_required
def wordle():
    return render_template("games/wordle.html", page="wordle")


# -------------------------------------------------------------------- #
# ------------------------- PLAY WORDLE ------------------------------ #
@games.route("/games/play-wordle", methods=["POST", "GET"])
@login_required
def play_wordle():
    # TODO: After game finish "Guess" button must disappear and "Reset" must appear
    # TODO: Style html page
    # TODO: Connect database and add highscores wordle
    # TODO: Show the answer after a lost game
    wordle_form = WordleForm()

    # Get the users last played game
    descending = WordleData.query.order_by(WordleData.id.desc())
    wordle_data = descending.filter_by(user_id=session["id"]).first()

    game_win = False
    game_loss = False
    # Print answer to console
    if wordle_data:
        print(wordle_data.wordle_answer)

    if request.method == "GET":

        # Set initial state
        game_state = "busy"
        if not wordle_data:
            # No games played yet, start new game
            wordle_divs = start_new_wordle(session["id"])

        elif not wordle_data.wordle_guess1:
            # New game started but didn't guess yet, start new game
            wordle_divs = start_new_wordle(session["id"])

        elif wordle_data.wordle_game_state in ("win", "loss"):
            # Last game finished, start new game
            wordle_divs = start_new_wordle(session["id"])

        else:
            # User is in the middle of a game
            last_wordle_guess = get_last_wordle_guess(wordle_data=wordle_data)
            game_state, wordle_divs = play_wordle_game(wordle_guess=last_wordle_guess,
                                                       user_id=session["id"],
                                                       req="GET")

        return render_template("games/play_wordle.html",
                               wordle_form=wordle_form,
                               wordle_divs=wordle_divs,
                               game_state=game_state,
                               page="play_wordle")

    # There is an active game
    if wordle_form.validate_on_submit():

        # Check if user makes invalid refresh after game end so new game can still start
        if wordle_data.wordle_game_state in ("win", "loss"):
            wordle_divs = start_new_wordle(session["id"])
            game_state = "busy"

            return render_template("games/play_wordle.html",
                                   wordle_form=wordle_form,
                                   wordle_divs=wordle_divs,
                                   game_state=game_state,
                                   page="play_wordle")

        if wordle_form.guess.data.lower() == wordle_data.wordle_answer.lower():
            # User guessed correctly
            game_win = True

        # Call play game function
        game_state, wordle_divs = play_wordle_game(wordle_guess=wordle_form.guess.data,
                                                   user_id=session["id"])
        if game_state == "loss":
            # User lost the game
            game_loss = True

        # Reset form to clear FormField
        wordle_form.guess.data = None

        return render_template("games/play_wordle.html",
                               wordle_form=wordle_form,
                               wordle_divs=wordle_divs,
                               game_state=game_state,
                               game_win=game_win,
                               game_loss=game_loss,
                               page="play_wordle")

    last_wordle_guess = get_last_wordle_guess(wordle_data=wordle_data)
    game_state, wordle_divs = play_wordle_game(wordle_guess=last_wordle_guess,
                                               user_id=session["id"],
                                               req="GET")

    # Reset form to clear FormField
    wordle_form.guess.data = None

    return render_template("games/play_wordle.html",
                           wordle_form=wordle_form,
                           wordle_divs=wordle_divs,
                           game_state=game_state,
                           page="play_wordle")


# ---------------------------------------------------------------- #
# ------------------------- NUMBERS ------------------------------ #
@games.route("/games/numbers", methods=["POST", "GET"])
@login_required
def numbers():

    return render_template("/games/numbers.html",
                           page="numbers")


# --------------------------------------------------------------------- #
# ------------------------- PLAY NUMBERS ------------------------------ #
@games.route("/games/play-numbers", methods=["POST", "GET"])
@login_required
def play_numbers():
    # TODO: Update html and css for highscores
    numbers_form = NumbersForm()
    numbers_divs = create_numbers_divs()

    # Get users last unfinished game
    numbers_data = db.session.query(NumbersData) \
        .order_by(NumbersData.id.desc()) \
        .filter(NumbersData.user_id == session["id"]) \
        .first()

    # Get best times global
    numbers_highscores_all = db.session.query(NumbersData) \
        .order_by(NumbersData.numbers_time) \
        .filter(NumbersData.numbers_time > 0).limit(8) \
        .all()

    # Get best times personal
    numbers_highscores_self = db.session.query(NumbersData) \
        .order_by(NumbersData.numbers_time) \
        .filter(NumbersData.numbers_time > 0, NumbersData.user_id == session["id"]).limit(8) \
        .all()

    if numbers_data is None:
        # Never played before
        new_numbers = NumbersData(
            user_id=session["id"],
            numbers_start=time.time(),
        )
        db.session.add(new_numbers)
        db.session.commit()

    elif numbers_data.numbers_time != -1:
        # Played before and last game is over
        new_numbers = NumbersData(
            user_id=session["id"],
            numbers_start=time.time(),
        )
        db.session.add(new_numbers)
        db.session.commit()

    elif numbers_form.validate_on_submit():
        # Game is going on pressed stop
        numbers_data.numbers_stop = time.time()
        numbers_data.numbers_time = round((numbers_data.numbers_stop - numbers_data.numbers_start),
                                          4)
        db.session.commit()

    elif numbers_data.numbers_stop == -1:
        # Game is going on and restarted
        db.session.delete(numbers_data)
        db.session.commit()
        new_numbers = NumbersData(
            user_id=session["id"],
            numbers_start=time.time(),
        )
        db.session.add(new_numbers)
        db.session.commit()

    return render_template("/games/play-numbers.html",
                           numbers_form=numbers_form,
                           numbers_divs=numbers_divs,
                           numbers_highscores_self=numbers_highscores_self,
                           numbers_highscores_all=numbers_highscores_all,
                           page="play-numbers")
