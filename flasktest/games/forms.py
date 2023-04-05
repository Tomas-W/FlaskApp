from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

from flasktest.games.utils import Wordle, WordleWordCheck


# ------------------------------------------------------------------ #
# ------------------------- COUNTRIES ------------------------------ #
class CountryForm(FlaskForm):
    """
    Select form for Countries page.
    Takes input for the Countries game.

    :param select: SelectField; either larger or smaller (str).
    :param submit: SubmitField; submit.
    """
    select = SelectField(label="Larger or Smaller?",
                         choices=[("Larger", "Larger"), ("Smaller", "Smaller")])
    submit = SubmitField(label="Go!")


# --------------------------------------------------------------- #
# ------------------------- WORDLE ------------------------------ #
class WordleForm(FlaskForm):
    """
    Word guess form for Wordle page.
    Takes input for the Countries game.

    :param guess: StringField; 5 letter word (str).
    :param submit: SubmitField; submit.
    """
    guess = StringField(render_kw={"placeholder": "Guess a word..", "autofocus": True},
                        validators=[DataRequired(message="Please make a guess!"),
                                    Length(min=5, max=5,
                                           message="5 letters only!"),
                                    WordleWordCheck(
                                        message=None,  # To be abe to output guessed word in message
                                        allowed_words=Wordle.word_list)])
    submit = SubmitField(label="Guess!")


# ---------------------------------------------------------------- #
# ------------------------- NUMBERS ------------------------------ #
class NumbersForm(FlaskForm):
    """
    Submit form for numbers page.
    Logic is handled by html on page, only submitting is needed.

    :param submit: SubmitField; submit.
    """
    submit = SubmitField(label="Stop")
