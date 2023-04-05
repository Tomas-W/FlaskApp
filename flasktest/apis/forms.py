"""
Controls all FlaskForms related to the API pages
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, widgets, \
    IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.widgets import CheckboxInput

from flasktest.apis.apis_settings import CPI_APPEARANCE, CPI_FOOD, CPI_FIXED, CPI_LUXURY,\
    CPI_SNACKS, CPI_APPLIANCES


# ------------------------------------------------------------- #
# ------------------------- PUBG ------------------------------ #
class SearchPUBGForm(FlaskForm):
    """
    Search form for PUBG page.
    Takes user input and formats it for PUBG API request.

    :param name: StringField; steam name (str).
    :param perspective: SelectField; stats from which game perspective (str).
    :param game_mode: SelectField; stats from which game mode (str).
    :param submit: SubmitField; submit.
    """
    name = StringField(label="Steam name",
                       render_kw={"placeholder": "e.g. hambinooo"},
                       validators=[DataRequired(message="Name is required"),
                                   Length(min=3, max=50,
                                          message="Name must be 3-50 char long")])
    perspective = SelectField(label="Perspective",
                              choices=[("-fpp", "First Person"), ("", "Third person")])
    game_mode = SelectField(label="Game mode",
                            choices=[("solo", "Solo"), ("duo", "Duo"), ("squad", "Squad")])
    submit = SubmitField(label="Search")


# ------------------------------------------------------------ #
# ------------------------- CPI ------------------------------ #
class SearchCPIForm(FlaskForm):
    """
    Search form for CPI page.
    Takes selection(s) from checkboxes per category and
    formats it in the correct format to be used with get_cpi_series().

    Each category contains a SelectMultipleField tuple of form label and category-item name.
    :param: appearance; appliances; fixed; food; luxury; snacks: (SelectBox).
    :param: start_year; stop_year: IntegerField NumberRange (int).
    :param submit: SubmitField; submit.
    """
    appearance = SelectMultipleField(label="Appearance",
                                     widget=widgets.ListWidget(prefix_label=False),
                                     choices=CPI_APPEARANCE,
                                     option_widget=CheckboxInput())
    appliances = SelectMultipleField(label="Appliances",
                                     widget=widgets.ListWidget(prefix_label=False),
                                     choices=CPI_APPLIANCES,
                                     option_widget=CheckboxInput())
    fixed = SelectMultipleField(label="Appearance",
                                widget=widgets.ListWidget(prefix_label=False),
                                choices=CPI_FIXED,
                                option_widget=CheckboxInput())
    food = SelectMultipleField(label="Food",
                               widget=widgets.ListWidget(prefix_label=False),
                               choices=CPI_FOOD,
                               option_widget=CheckboxInput())
    luxury = SelectMultipleField(label="Luxury",
                                 widget=widgets.ListWidget(prefix_label=False),
                                 choices=CPI_LUXURY,
                                 option_widget=CheckboxInput())
    snacks = SelectMultipleField(label="Snacks",
                                 widget=widgets.ListWidget(prefix_label=False),
                                 choices=CPI_SNACKS,
                                 option_widget=CheckboxInput())

    start_year = IntegerField(label="Start date",
                              validators=[(
                                  NumberRange(min=1996,
                                              max=2021,
                                              message="Start year range: 1996 - 2021"))])

    stop_year = IntegerField(label="Start date",
                             validators=[(
                                 NumberRange(min=1997,
                                             max=2022,
                                             message="Stop year range: 1997 - 2022"))])

    submit = SubmitField(label="Search")
