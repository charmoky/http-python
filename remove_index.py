#!/usr/bin/python


import os


for root, dirs, fileslong in os.walk(".", followlinks=True):
    for dir in dirs:
            dir_path = os.path.join(root, dir)

            files = os.listdir(dir_path)

            if "index.html" in files:
                os.remove(dir_path + "/index.html")

