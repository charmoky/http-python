import os
from PIL import Image, ExifTags


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

        images = [file for file in os.listdir(self.path) if file.lower().endswith((".jpg", ".jpeg", ".png"))]

        for image in images:

            # If file already exists, do nothing
            if os.path.exists(self.path + "/.thumbnails/" + image):
                print("{} exists, skipping".format(image))
                continue
            
            print("Making thumbnail for {}".format(image))
            try:
                img = Image.open(self.path + image)
            except:
                return

            try:
                for orientation in ExifTags.TAGS.keys() : 
                    if ExifTags.TAGS[orientation]=='Orientation' : break 
                exif=dict(img._getexif().items())
            
                if   exif[orientation] == 3 : 
                    img=img.rotate(180, expand=True)
                elif exif[orientation] == 6 : 
                    img=img.rotate(270, expand=True)
                elif exif[orientation] == 8 : 
                    img=img.rotate(90, expand=True)
            except:
                pass

            img.thumbnail(size)
            img.save(self.path + "/.thumbnails/" + image)
