#!/usr/bin/env python

import cgi
from backend.activity import activity_tracker

import os

import datetime
import numpy as np

if "REMOTE_USER" in os.environ.keys():
    user = os.environ["REMOTE_USER"]
else:
    user = "Anon"

def gen_checkbox(idx, date, act, adder, desciption, link):
    print(f"""<input type="checkbox" id="date_{idx}" name="date_{idx}" value="True">
    <label for="date_{idx}"> {idx}. {str(date)} : <a href="{link}>{act}</a> : {desciption} added by {adder}</label><br>""")

def do_GET(hlr):
    dic = hlr.get_dic()

    print("""<!DOCTYPE html>
    <html>
    <body>

    <title>Activity Editor</title>

    <h2>Hello %s !</h2>
    
    <p> Select the entry(ies) to remove </p>
    <form action="/sandbox/cgi-bin/edit_activity.py" method="post">""" % (user))
    
    oldest_idx = len(dic['Date'])-1
    min_idx = -1
    if oldest_idx > 10:
        min_idx = oldest_idx-10
    for i in range(oldest_idx, min_idx, -1):
        gen_checkbox(i, dic['Date'][i], dic['Activity'][i], dic['Adder'][i], dic['Description'][i], dic['Link'][i])

    print("""<input type="submit" value="Submit">
    </form>""")
    print("<button onclick=\"window.location.href='/sandbox/cgi-bin/handle_activity.py'\">Back to tracker</button>")

    print("""</body>
    </html>""")

def do_POST(hlr):

    print ("Content-Type: text/html")
    print("")
    print ("<html><body>")
    print ("<title>Expense Editor</title>")
    print ("<h2>Hello %s !</h2>" % (user))

    dic = hlr.get_dic()
    ## Parsing data from the HTTP server
    form = cgi.FieldStorage()
    
    idx_to_rm = []
    for i in range(0, len(dic['Date'])):
        to_rm = (form.getfirst(f'date_{i}', 'None'))

        if to_rm == "True":
            idx_to_rm.append(i)

    removed = 0
    for idx in idx_to_rm:
        idx_to_remove = idx-removed
        print(f"<p>Removing date {dic['Date'][idx_to_remove]} : {dic['Activity'][idx_to_remove]} added by {dic['Adder'][idx_to_remove]}</p>")
        for key in dic.keys():
            if isinstance(dic[key], list):
                dic[key].pop(idx_to_remove)
            elif isinstance(dic[key], np.ndarray):
                dic[key] = np.delete(dic[key], idx_to_remove)
            else:
                raise unexpectedType("Unexpected type !")
        removed += 1

    print("<button onclick=\"window.location.href='/sandbox/cgi-bin/handle_activity.py'\">Back to tracker</button>")
    print("""</body>
    </html>""")

    hlr.save_data(dic=dic)

hlr = activity_tracker(user)
if os.environ['REQUEST_METHOD'] == "GET":
    do_GET(hlr)
else:
    do_POST(hlr)

