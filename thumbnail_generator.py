import os
from PIL import Image


class thumb_gen():
    def __init__(self, path):
        self.path = path

    def make_thumbnail_dir(self):
        try:
            os.mkdir(self.path + ".thumbnails/")
        except FileExistsError:
            pass

    def make_thumbnails(self, size=(256,256)):
        self.make_thumbnail_dir()

        images = [file for file in os.listdir(self.path) if file.lower().endswith((".jpg", ".png"))]

        for image in images:

            # If file already exists, do nothing
            if os.path.exists(self.path + "/.thumbnails/" + image):
                continue

            img = Image.open(self.path + image)
            img.thumbnail(size)
            img.save(self.path + "/.thumbnails/" + image)
