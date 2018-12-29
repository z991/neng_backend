# __author__ = itsneo1990
from PIL import Image
from io import BytesIO


def image_resize(data, size):
    i_file = BytesIO(data)
    o_file = BytesIO()

    img = Image.open(i_file)
    img = img.convert("RGB").resize(size, Image.ANTIALIAS)

    img.save(o_file, 'jpeg', quality=100)
    resized_data = o_file.getvalue()

    i_file.close()
    o_file.close()
    return resized_data
