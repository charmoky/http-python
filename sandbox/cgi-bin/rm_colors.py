#!/usr/bin/env python

import cgi
import os

from backend.show_expense import get_colors_filename

def gen_header():
    print("""<!DOCTYPE html>
    <html>""")

def do_GET():
    gen_header()
    print("""<body>
    <title>Remove colors ?</title>
    <h2>Change expenses current colors ?</h2>
    <br><form action>"/sandbox/cgi-bin/rm_colors.py" method="post"><input type="submit" value="Change Expenses Colors"></form>
    </body>
    </html>""")

def do_POST():

    #os.remove(get_colors_filename())
    #os.sync()

    gen_header()
    print("""<head>
    <meta http-equiv="refresh" content="7; url='/sandbox/cgi-bin/handle_finance.py'" />
    </head>
    <body>
    <title>Redirecting...</title>
    <p>Please follow <a href="/sandbox/cgi-bin/handle_finance.py">this link</a>.</p>
    </body>
    </html>""")

if os.environ['REQUEST_METHOD'] == "GET":
    do_GET()
else:
    do_POST()
