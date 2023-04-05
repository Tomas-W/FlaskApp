import numpy as np

import cairosvg
import io
from PIL import Image

from flasktest.tools.tools_settings import ALLOWED_EXTENSIONS, IMAGE_ADJUST_IMAGE_PATH


# --------------------------------------------------------------------- #
# ------------------------- IMAGE UPLOAD ------------------------------ #
def allowed_extension(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def svg_to_array(filename):
    """Load an SVG file and return image in Numpy array"""
    # Make memory buffer
    mem = io.BytesIO()
    # Convert SVG to PNG in memory
    cairosvg.svg2png(url=filename, write_to=mem)
    # Convert PNG to Numpy array
    return np.array(Image.open(mem))


def convert_img(filetype, filename, lighting, mirror, rotation, rgb):
    """
    Load an SVG or PNG file, adjust with params and return image in Numpy array.
    filetype(str) "svg" or "png"
    filename(str)
    lighting(int) (0.01 - 0.99) or 1 or (2 - 99)
    mirror(int) 0 for horizontal or 1 for vertical
    rotation(int) 1 2 3
    rgb(list; int or None) (0.01 - 0.99) or 1 or (2 - 99) or None
    """
    # TODO: Add 4th array to allow for transparency.
    # TODO: Changes must not apply to transparent or white parts
    filename = f"{IMAGE_ADJUST_IMAGE_PATH}{filename.split('/')[-1]}"
    # Make memory buffer
    mem = io.BytesIO()

    if filetype == "svg":
        # Convert SVG to PNG in memory
        cairosvg.svg2png(url=filename, write_to=mem)
        # Convert PNG to Numpy array
        img_array = np.array(Image.open(mem))

    if filetype == "png":
        img_array = np.asarray(Image.open(filename).convert('RGB'))

    if lighting is not None:
        if lighting < 1:
            # Make darker
            # Do not darken if white (all values under 3)
            img_array = img_array * lighting if 3 < img_array.all() else img_array

        if lighting > 1:
            # Make lighter
            img_array = (((255 - img_array) / 100) * lighting) + img_array

    if mirror is not None:
        if mirror == 0 or 1:
            # mirror over horizontal or vertical
            img_array = np.flip(img_array, axis=mirror)

    # Adjust rotation
    if rotation != 0:
        for i in range(rotation):
            img_array = np.rot90(img_array)

    # Adjust RGB colors individually
    if rgb is not None or 0:
        red_array = img_array[:, :, 0]
        green_array = img_array[:, :, 1]
        blue_array = img_array[:, :, 2]

        # Red
        if rgb[0] < 1:
            # Subtract red
            red_array = red_array * rgb[0]
        if rgb[0] > 1:
            # Add red
            red_array = (((255 - red_array) / 100) * rgb[0]) + red_array

        # Green
        if rgb[1] < 1:
            green_array = green_array * rgb[1]
        if rgb[1] > 1:
            green_array = (((255 - green_array) / 100) * rgb[1]) + green_array

        # Blue
        if rgb[2] < 1:
            blue_array = blue_array * rgb[2]
        if rgb[2] > 1:
            blue_array = (((255 - blue_array) / 100) * rgb[2]) + blue_array

        # Re-stack
        img_array = np.stack([red_array, green_array, blue_array], axis=2)

    return img_array
