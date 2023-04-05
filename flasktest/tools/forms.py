from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, IntegerField
from wtforms.validators import NumberRange


# --------------------------------------------------------------------- #
# ------------------------- IMAGE ADJUST ------------------------------ #
class ImageAdjustForm(FlaskForm):
    """
    Handles logic for the ImageAdjust tool
    """
    lighting = SelectField(label="Darker or Lighter?",
                           choices=[(None, "No lighting"),
                                    ("Darker", "Darker"),
                                    ("Lighter", "Lighter")])
    lighting_value = IntegerField(label="Value in percentage",
                                  render_kw={"placeholder": "Range: 0-100"},
                                  default=0,
                                  validators=[NumberRange(min=0, max=100,
                                                          message="Min value: 0, max value: 100")])

    mirror = SelectField(label="Mirror along axis",
                         choices=[("None", "No mirroring"),
                                  ("Horizontally", "Horizontally"),
                                  ("Vertically", "Vertically")])

    rotate = SelectField(label="Rotate left",
                         choices=[(0, "None"),
                                  (1, "90 deg"),
                                  (2, "180 deg"),
                                  (3, "270 deg")])

    rgb = SelectField(label="Adjust RGB",
                      choices=[("None", None),
                               ("Add red", "Add red"),
                               ("Remove red", "Remove red"),
                               ("Add green", "Add green"),
                               ("Remove green", "Remove green"),
                               ("Add blue", "Add blue"),
                               ("Remove blue", "Remove blue")])
    rgb_value = IntegerField(label="Value in percentage",
                             default=0,
                             render_kw={"placeholder": "Range: 0 - 100"},
                             validators=[NumberRange(min=0, max=100,
                                                     message="Min value: 0, max value: 100")])

    submit = SubmitField(label="Go!")
