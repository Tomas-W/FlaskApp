import math
import numpy as np
from PIL import Image

from flask import render_template, request, session, flash, redirect, url_for, Blueprint
from flask_login import login_required

from flasktest import db
from flasktest.models import ImageAdjustData
from flasktest.tools.forms import ImageAdjustForm
from flasktest.tools.utils import convert_img, allowed_extension
from flasktest.tools.tools_settings import IMAGE_ADJUST_IMAGE_PATH, \
    IMAGE_ADJUST_IMAGE_PATH_RELATIVE


tools = Blueprint("tools", __name__)


# --------------------------------------------------------------------- #
# ------------------------- IMAGE UPLOAD ------------------------------ #
@tools.route("/tools/image-adjust", methods=["GET", "POST"])
@login_required
def image_adjust():
    if request.method == "POST":
        # Is a file present
        if "file" not in request.files:
            flash("No file found.")
            return redirect(request.url)
        
        file = request.files["file"]
        # Is a file selected
        if file.filename == "":
            flash("No file selected.")
            return redirect(request.url)
        
        # Is extension allowed
        if not allowed_extension(file.filename):
            flash("Only .png and .svg allowed.")
            return redirect(request.url)
        
        if not file:
            flash("File not accepted.")
            return redirect(request.url)
        
        # File accepted
        file_extension = file.filename.split(".")[1]
        filename = f"{session['id']}-upload"
        file.save(f"{IMAGE_ADJUST_IMAGE_PATH}{filename}.{file_extension}")
        image_path = f"{IMAGE_ADJUST_IMAGE_PATH_RELATIVE}{filename}.{file_extension}"

        image_info = ImageAdjustData.query.filter_by(user_id=session["id"]).first()
        if not image_info:
            new_image_info = ImageAdjustData(user_id=session["id"],
                                             filetype=file_extension,
                                             old_image=image_path)
            db.session.add(new_image_info)
            db.session.commit()
        else:
            image_info.old_image = image_path
            db.session.commit()

        return redirect(url_for("tools.image_adjust_tool"))

    return render_template("tools/image_adjust.html",
                           page="image_adjust")


# --------------------------------------------------------------------- #
# ------------------------- IMAGE ADJUST ------------------------------ #
@tools.route("/tools/image-adjust-tool", methods=["GET", "POST"])
@login_required
def image_adjust_tool():
    # TODO: Add download button for user to download adjusted image
    # TODO: Let user upload new image from adjust page or appy changes to recently adjusted image(s)
    image_adjust_form = ImageAdjustForm()
    lighting = None
    mirror = None
    rotation = 0
    rgb = None

    if image_adjust_form.validate_on_submit():
        if image_adjust_form.lighting.data == "Darker":
            lighting = image_adjust_form.lighting_value.data / 101

        if image_adjust_form.lighting.data == "Lighter":
            lighting = image_adjust_form.lighting_value.data

        if image_adjust_form.mirror.data == "Horizontally":
            mirror = 0
        if image_adjust_form.mirror.data == "Vertically":
            mirror = 1

        rotation = math.floor(int(image_adjust_form.rotate.data))

        rbg_value = image_adjust_form.rgb_value.data
        if image_adjust_form.rgb.data == "Add red":
            rgb = [rbg_value, 1, 1]
        if image_adjust_form.rgb.data == "Remove red":
            rgb = [rbg_value / 100, 1, 1]

        if image_adjust_form.rgb.data == "Add green":
            rgb = [1, rbg_value, 1]
        if image_adjust_form.rgb.data == "Remove green":
            rgb = [1, rbg_value / 100, 1]

        if image_adjust_form.rgb.data == "Add blue":
            rgb = [1, 1, rbg_value]
        if image_adjust_form.rgb.data == "Remove blue":
            rgb = [1, 1, rbg_value / 100]

        image_data = ImageAdjustData.query.filter_by(user_id=session["id"]).first()

        adjusted_image = convert_img(filetype=image_data.filetype,
                                     filename=image_data.old_image,
                                     lighting=lighting,
                                     mirror=mirror,
                                     rotation=rotation,
                                     rgb=rgb)
        adjusted_image = np.array(adjusted_image, "uint8")
        adjusted_filename = f"{session['id']}-new"
        new_file_name = f"{IMAGE_ADJUST_IMAGE_PATH_RELATIVE}{adjusted_filename}.png"
        img = Image.fromarray(adjusted_image, "RGB")
        img.save(f"{IMAGE_ADJUST_IMAGE_PATH}{adjusted_filename}.png")
        image_data.new_image = new_file_name
        db.session.commit()

        return render_template("tools/image_adjust-tool.html",
                               old_image=image_data.old_image,
                               new_image=new_file_name,
                               image_adjust_form=image_adjust_form,
                               page="image_adjust_tool")

    image_data = ImageAdjustData.query.filter_by(user_id=session["id"]).first()

    if not image_data:
        # Tries to access page without uploading an image first
        old_image = f"{IMAGE_ADJUST_IMAGE_PATH_RELATIVE}old_image.png"
    else:
        old_image = image_data.old_image
    return render_template("tools/image_adjust-tool.html",
                           old_image=old_image,
                           image_adjust_form=image_adjust_form,
                           page="image_adjust_tool")
