import pandas as pd
from random import randint, shuffle, choice

from wtforms import ValidationError

from flasktest import db
from flasktest.models import CountriesData, WordleData
from flasktest.games.games_settings import DF_EUROPE_PATH, DF_WORDLE_WORDS_PATH


# ------------------------------------------------------------------ #
# ------------------------- COUNTRIES ------------------------------ #
def get_country_name(number):
    """
    Gets the name of the country corresponding to the given number.

    :param number: A number ranging from 1 - len(names).

    :return: Country name corresponding with the number (str).
    """
    df_europe = pd.read_csv(DF_EUROPE_PATH)
    countries = df_europe.Name.tolist()
    return countries[number]


def get_country_size(number):
    """
    Gets the name of the country corresponding to the given number.

    :param number: A number ranging from 1 - len(names).

    :return: Country size corresponding with the number (int).
    """
    df_europe = pd.read_csv(DF_EUROPE_PATH)
    sizes = df_europe.Size.tolist()
    return int(sizes[number])


def get_country_path(number):
    """
    Gets the name of the country corresponding to the given number.

    :param number: A number ranging from 1 - len(names).

    :return: Country image path corresponding with the number (str).
    """
    df_europe = pd.read_csv(DF_EUROPE_PATH)
    paths = df_europe.FilePath.tolist()
    return paths[number]


def evaluate_countries_game(guess, user_id):
    """
    Takes a users guess and a user id to compare with the displayed country.

    :param guess: SelectField choice from the CountryForm (str).
    :param user_id: User id from current_user or session["id"] (str or int).

    :returns countries_data: Object with users last game (Obj int).
    """
    countries_data = CountriesData.query.filter_by(user_id=user_id).first()
    size_old = int(get_country_size(countries_data.country_old))
    size_new = int(get_country_size(countries_data.country_new))

    if guess == "Larger" and size_new >= size_old:
        # User guessed correctly
        countries_data.country_streak += 1
        if countries_data.country_streak > countries_data.country_record:
            countries_data.country_record = countries_data.country_streak

    elif guess == "Smaller" and size_new <= size_old:
        # User guessed correctly
        countries_data.country_streak += 1
        if countries_data.country_streak > countries_data.country_record:
            countries_data.country_record = countries_data.country_streak

    else:
        # User guessed incorrectly
        countries_data.country_streak = 0

    countries_data.country_old = countries_data.country_new
    while countries_data.country_new == countries_data.country_old:
        countries_data.country_new = randint(1, 44)

    db.session.commit()

    return countries_data


# --------------------------------------------------------------- #
# ------------------------- WORDLE ------------------------------ #
class Wordle:
    """
    Class containing wordle game info and handles game logic.
    """
    df_words = pd.read_csv(DF_WORDLE_WORDS_PATH)
    word_list = df_words.Word.tolist()

    def __init__(self, answer):
        self.answer = answer.upper()
        self.guess1 = ""
        self.guess2 = ""
        self.guess3 = ""
        self.guess4 = ""
        self.guess5 = ""
        self.round = 0

        # color codes for html
        self.grey = "var(--grey)"
        self.yellow = "var(--yellow)"
        self.green = "var(--green)"

        self.all_info = []
        self.empty = [".", self.grey]

        # Creates a list with all div info for the html
        self.game_start = [self.empty for _ in range(25)]

    def __repr__(self):
        return f"Wordle(" \
               f"round={self.round}, answer={self.answer})"

    def start_wordle(self):
        """
        Returns an empty grid for a new game.
        """
        return self.game_start

    def round1_data(self, guess1, answer):
        """
        Loops over users guess and compares it with the answer.
        Handles color formatting only.

        :param guess1: User guess received from WordleForm (str).
        :param answer: Game answer received from database (str).

        :returns colors: Nested list containing pais of letters and color-codes (list str).
        """
        colors = []
        for index, letter in enumerate(guess1):
            if letter == answer[index]:
                colors.append([letter, self.green])
            elif letter in answer:
                colors.append([letter, self.yellow])
            else:
                colors.append([letter, self.grey])
        self.round += 1
        self.guess1 = guess1
        return colors

    def round2_data(self, guess2, answer):
        """
        Loops over users guess and compares it with the answer.
        Handles color formatting only.

        :param guess2: User guess received from WordleForm (str).
        :param answer: Game answer received from database (str).

        :returns colors: Nested list containing pais of letters and color-codes (list str).
        """
        colors = []
        for index, letter in enumerate(guess2):
            if letter == answer[index]:
                colors.append([letter, self.green])
            elif letter in answer:
                colors.append([letter, self.yellow])
            else:
                colors.append([letter, self.grey])
        self.round += 1
        self.guess2 = guess2
        return colors

    def round3_data(self, guess3, answer):
        """
        Loops over users guess and compares it with the answer.
        Handles color formatting only.

        :param guess3: User guess received from WordleForm (str).
        :param answer: Game answer received from database (str).

        :returns colors: Nested list containing pais of letters and color-codes (list str).
        """
        colors = []
        for index, letter in enumerate(guess3):
            if letter == answer[index]:
                colors.append([letter, self.green])
            elif letter in answer:
                colors.append([letter, self.yellow])
            else:
                colors.append([letter, self.grey])
        self.round += 1
        self.guess3 = guess3
        return colors

    def round4_data(self, guess4, answer):
        """
        Loops over users guess and compares it with the answer.
        Handles color formatting only.

        :param guess4: User guess received from WordleForm (str).
        :param answer: Game answer received from database (str).

        :returns colors: Nested list containing pais of letters and color-codes (list str).
        """
        colors = []
        for index, letter in enumerate(guess4):
            if letter == answer[index]:
                colors.append([letter, self.green])
            elif letter in answer:
                colors.append([letter, self.yellow])
            else:
                colors.append([letter, self.grey])
        self.round += 1
        self.guess4 = guess4
        return colors

    def round5_data(self, guess5, answer):
        """
        Loops over users guess and compares it with the answer.
        Handles color formatting only.

        :param guess5: User guess received from WordleForm (str).
        :param answer: Game answer received from database (str).

        :returns colors: Nested list containing pais of letters and color-codes (list str).
        """
        colors = []
        for index, letter in enumerate(guess5):
            if letter == answer[index]:
                colors.append([letter, self.green])
            elif letter in answer:
                colors.append([letter, self.yellow])
            else:
                colors.append([letter, self.grey])
        self.round += 1
        self.guess5 = guess5
        return colors


class WordleWordCheck:
    """
    Helper class for WordleForm to validate if users Wordle guess is in the allowed list.
    Raises FlaskForm validation error if word is invalid.
    """
    def __init__(self, allowed_words, message=None):
        self.allowed_words = allowed_words
        self.error = None

        if not message:
            message = "Invalid word:"
        self.message = message

    def __call__(self, form, field):
        if not field.data.lower() in self.allowed_words:
            self.error = f"{self.message} '{field.data.lower()}'"
            raise ValidationError(self.error)


def add_new_wordle(user_id, answer):
    """
    Takes a user_id(int) and an answer(str).
    Returns a new_wordle(class) for the Wordle game.
    """
    new_wordle = WordleData(
        user_id=user_id,
        wordle_answer=answer,
        wordle_round=0,
        wordle_game_state="busy",
    )
    return new_wordle


def start_new_wordle(user_id):
    """
    Takes a user_id(int), creates a new Wordle game and saves it in the Users data.
    Returns a new_wordle(class) for the Wordle game.
    """
    wordle_answer = Wordle(choice(Wordle.word_list)).answer
    wordle_divs = Wordle(choice(Wordle.word_list)).game_start
    wordle_data = add_new_wordle(user_id=user_id, answer=wordle_answer)
    db.session.add(wordle_data)
    db.session.commit()
    return wordle_divs


def get_last_wordle_guess(wordle_data):
    """
    Takes a Users wordle_data(class) and returns the Users last made guess.
    """
    if wordle_data.wordle_guess4 is not None:
        return wordle_data.wordle_guess4

    if wordle_data.wordle_guess3 is not None:
        return wordle_data.wordle_guess3

    if wordle_data.wordle_guess2 is not None:
        return wordle_data.wordle_guess2

    if wordle_data.wordle_guess1 is not None:
        return wordle_data.wordle_guess1

    if wordle_data.wordle_guess1 is not None:
        return wordle_data.wordle_guess1


def play_wordle_game(wordle_guess, user_id, req="POST"):
    """
    Handles the logic for playing the Wordle game.
    Takes a Users wordle_guess(str) and user_id(int).
    Returns the game state(str) and the wordle_divs(list) to be rendered.
    """
    descending = WordleData.query.order_by(WordleData.id.desc())
    wordle_data = descending.filter_by(user_id=user_id).first()
    wordle_game = Wordle(wordle_data.wordle_answer)
    wordle_divs = wordle_game.game_start

    # This logic is needed to use this function with both POST and GET requests
    if req == "GET":
        wordle_data.wordle_round -= 1

    # There is an active game
    game_state = "busy"

    # Check for win
    if wordle_data.wordle_answer == wordle_guess.upper():
        wordle_data.wordle_game_state = "win"
        game_state = "win"

    if wordle_data.wordle_round == 4:
        wordle_game = Wordle(wordle_data.wordle_answer)
        wordle_divs[:5] = wordle_game.round1_data(wordle_data.wordle_guess1,
                                                  wordle_data.wordle_answer)
        wordle_divs[5:10] = wordle_game.round2_data(wordle_data.wordle_guess2,
                                                    wordle_data.wordle_answer)
        wordle_divs[10:15] = wordle_game.round3_data(wordle_data.wordle_guess3,
                                                     wordle_data.wordle_answer)
        wordle_divs[15:20] = wordle_game.round4_data(wordle_data.wordle_guess4,
                                                     wordle_data.wordle_answer)
        wordle_divs[20:25] = wordle_game.round5_data(wordle_guess.upper(),
                                                     wordle_data.wordle_answer)
        wordle_data.wordle_round = 5
        wordle_data.wordle_guess5 = wordle_guess.upper()
        if game_state == "win":
            wordle_data.wordle_win_round = 5
        else:
            game_state = "loss"
            wordle_data.wordle_game_state = "loss"
            wordle_data.wordle_win_round = -1

    elif wordle_data.wordle_round == 3:
        wordle_divs[:5] = wordle_game.round1_data(wordle_data.wordle_guess1,
                                                  wordle_data.wordle_answer)
        wordle_divs[5:10] = wordle_game.round2_data(wordle_data.wordle_guess2,
                                                    wordle_data.wordle_answer)
        wordle_divs[10:15] = wordle_game.round3_data(wordle_data.wordle_guess3,
                                                     wordle_data.wordle_answer)
        wordle_divs[15:20] = wordle_game.round4_data(wordle_guess.upper(),
                                                     wordle_data.wordle_answer)
        wordle_data.wordle_round = 4
        wordle_data.wordle_guess4 = wordle_guess.upper()
        if game_state == "win":
            wordle_data.wordle_win_round = 4

    elif wordle_data.wordle_round == 2:
        wordle_divs[:5] = wordle_game.round1_data(wordle_data.wordle_guess1,
                                                  wordle_data.wordle_answer)
        wordle_divs[5:10] = wordle_game.round2_data(wordle_data.wordle_guess2,
                                                    wordle_data.wordle_answer)
        wordle_divs[10:15] = wordle_game.round3_data(wordle_guess.upper(),
                                                     wordle_data.wordle_answer)
        wordle_data.wordle_round = 3
        wordle_data.wordle_guess3 = wordle_guess.upper()
        if game_state == "win":
            wordle_data.wordle_win_round = 3

    elif wordle_data.wordle_round == 1:
        wordle_divs[:5] = wordle_game.round1_data(wordle_data.wordle_guess1,
                                                  wordle_data.wordle_answer)
        wordle_divs[5:10] = wordle_game.round2_data(wordle_guess.upper(),
                                                    wordle_data.wordle_answer)
        wordle_data.wordle_round = 2
        wordle_data.wordle_guess2 = wordle_guess.upper()
        if game_state == "win":
            wordle_data.wordle_win_round = 2

    if wordle_data.wordle_round == 0:
        # Response after 1st guess
        wordle_divs[:5] = wordle_game.round1_data(wordle_guess.upper(),
                                                  wordle_data.wordle_answer)
        wordle_data.wordle_round = 1
        wordle_data.wordle_guess1 = wordle_guess.upper()
        if game_state == "win":
            wordle_data.wordle_win_round = 1

    db.session.commit()
    return game_state, wordle_divs


# ---------------------------------------------------------------- #
# ------------------------- NUMBERS ------------------------------ #
def create_numbers_divs():
    """
    Generates div info for numbers page.
    Returns 25 divs in random order, containing 1-9 once.

    :returns numbers_divs: Nested list containing the content (1-9 or "") and their position
    in the html grid.
    """
    numbers_divs = [["", ""] for _ in range(25)]
    boxes = ["boxB", "boxC", "boxD", "boxE", "boxF", "boxG", "boxH", "boxI"]
    for index, box in enumerate(boxes):
        numbers_divs[index] = [(index + 2), box]
    for div in numbers_divs[8:]:
        div[1] = "boxEmpty"
    shuffle(numbers_divs)
    return numbers_divs
