#!/usr/bin/python

import os
import argparse

img_types = [".jpg", ".jpeg", ".png", ".gif"]
vid_types = [".mp4", ".webm"]

def gen_img_dir_list(path):
    img_list = []
    vid_list = []
    file_list = []
    dir_list = []

    for entry in  os.scandir(path):
        if entry.is_file():

            #Ignore "hidden" files
            if entry.name.startswith("."):
                continue

            # is image ?
            if os.path.splitext(entry.name)[1].lower() in img_types:
                img_list.append(entry.name)
                continue
            
            # is vid ?
            if os.path.splitext(entry.name)[1].lower() in vid_types:
                vid_list.append((entry.name, os.path.splitext(entry.name)[1].lower()[1:]))
                continue

            # Skip html files
            if os.path.splitext(entry.name)[1].lower() == ".html":
                continue
            
            file_list.append(entry.name)

        # Else add to dir list
        else:
           dir_list.append(entry.name + "/")

    return img_list, vid_list, file_list, dir_list


class Index_Generator:
    def __init__(self, path):
        self.path = path
        self.img, self.vid, self.file, self.dir = gen_img_dir_list(path)


    def gen_index(self, web_relative):
        f = open(self.path + "/index.html", 'w')

        f.write("""<html>
        <head>
        <title>Index of %s</title>
        """ % (web_relative))
        f.write("""<style>
        div.gallery {
          margin: 5px;
          border: 1px solid #ccc;
          float: left;
          width: 180px;
        }

        div.gallery:hover {
          border: 1px solid #777;
        }

        div.gallery img {
          width: 100%;
          height: auto;
        }
        
        div.gallery video {
          width: 100%;
          height: auto;
        }

        div.desc {
          padding: 15px;
          text-align: center;
        }
        </style>
        </head>""")


        f.write("""<body>
        <h1>Index of %s</h1>
        """ % (web_relative))

        f.write("""<hr>
        <pre>
        """)

        f.write("<h2> Directory List:</h2>\n")
        f.write("<a href=\"../\">../</a>\n")
        if len(self.dir) > 0:
            for dir in self.dir:
                f.write("<a href=\"%s\">%s</a>\n" % (dir, dir))
            
            for file in self.file:
                f.write("<a href=\"%s\" target=\"_blank\" rel=\"noopener noreferrer\">%s</a>\n" % (file, file))
        
        f.write("<br>")

        if len(self.img) > 0:
            f.write("<h2> Image Gallery:</h2>\n")
            for img in self.img:
                f.write("""<div class="gallery">""")
                f.write("<a href=\"{0}\" target=\"_blank\" rel=\"noopener noreferrer\"> <img alt=\"{0}\" src=\"{0}\"></a>".format(img))
                f.write("""</div>""")
                f.write("<br>")

        if len(self.vid) > 0:
            f.write("<h2> Video Gallery:</h2>\n")
            for vid in self.vid:
                f.write("""<div class="gallery">""")
                f.write("<video controls> <source src=\"{0}\" type=\"video/{1}\"> </video>".format(vid[0], vid[1]))
                f.write("<div class=\"desc\">%s</div>" % vid[0])
                f.write("""</div>""")
            f.write("<br>")

        f.write("""</pre>
        </body>
        </html>
        """)

        f.close()
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Path to use", default=".", required=False)
    parser.add_argument("--rel_path", help="Relative path to use", default=None, required=False)
    parser.add_argument("-r", "--recursive", help="Recursive", action="store_true")

    args = parser.parse_args()

    if args.rel_path is None:
        args.rel_path = args.path

    if args.recursive:
        for root, dirs, files in os.walk(args.path, followlinks=True):
            for name in dirs:
                path = os.path.join(root, name)
                print("Generating index for %s" % path) 

                generator = Index_Generator(path)
                if generator.gen_index(name) != 0:
                    exit(0)
    else:
        generator = Index_Generator(args.path)
        generator.gen_index(args.rel_path)

