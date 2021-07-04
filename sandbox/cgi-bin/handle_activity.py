#!/usr/bin/env python

import cgi
from backend.activity import activity_tracker
import os

import datetime

if "REMOTE_USER" in os.environ.keys():
    user = os.environ["REMOTE_USER"]
else:
    user = "Anon"

def gen_header():
    print("""<!DOCTYPE html>
    <html>
    <body>

    <title>Activity Helper</title>

    <h2>Good Morning %s !</h2>""" % user)

def gen_form():
    print("<h2> New activity idea ?</h2>")
    print("""<form action="/sandbox/cgi-bin/handle_activity.py" method="post">
    <label for="activity">Activity Name :</label>
    <input type="text" id="activity" name="activity"><br>
    <label for="link"> Link: </label>
    <input type="url" id="link" name="link"><br>

    <label for="desc">Quick Description :</label>
    <input type="text" id="desc" name="desc"<br>
    <input type="submit" value="Submit">""")

def gen_table(dic):
    
    if len(dic['Date']) == 0:
        return
    
    zipped = list(zip(dic['Date'], dic['Activity'], dic['Link'], dic['Description'], dic['Adder']))
    by_date = sorted(zipped, reverse=True)

    print("""<table>
    <tr>
        <th> Activity </th>
        <th> Description </th>
        <th> Date added </th>
        <th> Added by </th>
    </tr>""")

    for i, (date, act, link, desc, adder) in enumerate(by_date):
        print("<tr>")

        if link != None:
            print(f"<td><a href=\"{link}\">{act}</a></td>")
        else:
            print(f"<td>{act}</td>")
        
        print(f"<td>{desc}</td>")
        print(f"<td>{date.strftime('%d-%m-%y')}</td>")
        print(f"<td>{adder}</td>")

        print("</tr>")

    print("</table>")


def gen_tailer():
    print("</body></html>")

def do_GET(hlr):
    gen_header()
    gen_form()
    gen_table(hlr.get_dic())
    gen_tailer()

def do_POST(hlr):
    ## Parsing data from the HTTP server
    form = cgi.FieldStorage()

    act = (form.getfirst('activity', 'None'))
    link = (form.getfirst('link', 'None'))
    desc = (form.getfirst('desc', 'None'))

    def get_str_val(string):
        return string if string != "None" else None

    hlr.add_activity(Activity=act, Link=get_str_val(link), Description=get_str_val(desc))

    gen_header()
    gen_form()
    gen_table(hlr.get_dic())
    gen_tailer()
    
    hlr.save_data()

if not (user in ["shep", "tupai"]):
    print("""<!DOCTYPE html>
    <html>""")
    print(f"""<head>
    </head>
    <body>
    <title>Redirecting...</title>
    <p>User '{user}' nor part of ACL !</p>
    <p>Back to <a href="/sandbox/">sandbox</a>.</p>
    </body>
    </html>""")

    return

hlr = activity_tracker(user)
if os.environ['REQUEST_METHOD'] == "GET":
    do_GET(hlr)
else:
    do_POST(hlr)

