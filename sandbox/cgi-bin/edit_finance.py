#!/usr/bin/env python

import cgi
from backend.compute_expense import exp_handler
import os

import datetime
import numpy as np

if "REMOTE_USER" in os.environ.keys():
    user = os.environ["REMOTE_USER"]
else:
    user = "Anon"

def gen_checkbox(idx, date, amount, benef, exp_type):
    print(f"""<input type="checkbox" id="date_{idx}" name="date_{idx}" value="True">
    <label for="date_{idx}"> {idx}. {str(date)} : {amount} euros for {benef} on {exp_type}</label><br>""")

def do_GET(hlr):
    dic = hlr.get_dic()

    print("""<!DOCTYPE html>
    <html>
    <body>

    <title>Expense Editor</title>

    <h2>Hello %s !</h2>""")
    
    print("<button onclick=\"window.location.href='/sandbox/cgi-bin/handle_finance.py'\">Back to tracker</button>")
    print("""<p> Select the entry(ies) to remove </p>
    <form action="/sandbox/cgi-bin/edit_finance.py" method="post">""" % (user))
    
    oldest_idx = len(dic['Date'])-1
    min_idx = -1
    #if oldest_idx > 10:
    #    min_idx = oldest_idx-10
    for i in range(oldest_idx, min_idx, -1):
        gen_checkbox(i, dic['Date'][i], dic['Amount'][i], dic['Benef'][i], dic['Type'][i])

    print("""<input type="submit" value="Submit">
    </form>""")
    print("<button onclick=\"window.location.href='/sandbox/cgi-bin/handle_finance.py'\">Back to tracker</button>")

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
        print(f"<p>Removing date {dic['Date'][idx_to_remove]} : {dic['Type'][idx_to_remove]} {dic['Amount'][idx_to_remove]} {dic['Method'][idx_to_remove]} for {dic['Benef'][idx_to_remove]}</p>")
        for key in dic.keys():
            if isinstance(dic[key], list):
                dic[key].pop(idx_to_remove)
            elif isinstance(dic[key], np.ndarray):
                dic[key] = np.delete(dic[key], idx_to_remove)
            else:
                raise unexpectedType("Unexpected type !")
        removed += 1

    print("<button onclick=\"window.location.href='/sandbox/cgi-bin/handle_finance.py'\">Back to tracker</button>")
    print("""</body>
    </html>""")

    hlr.save_data(dic=dic)

hlr = exp_handler("all")
if os.environ['REQUEST_METHOD'] == "GET":
    do_GET(hlr)
else:
    do_POST(hlr)

