#!/usr/bin/env python

import cgi
import os

from backend.compute_expense import exp_handler

import datetime

if "REMOTE_USER" in os.environ.keys():
    user = os.environ["REMOTE_USER"]
else:
    user = "Anon"

def get_date_string_plus_0(date):
    if date >= 10:
        return str(date)
    else:
        return "0" + str(date)

def gen_http_select_type(types_list):
    for i in types_list:
        print("<option value=\"%s\"> %s</option>" % (i, i))

def do_GET(types_list, method_list):
    today = datetime.datetime.now()
    print("""<!DOCTYPE html>
    <html>
    <body>

    <title>Expense Tracker</title>

    <h2>Hello %s ! New Expense ?</h2>

    <form action="/sandbox/cgi-bin/handle_finance.py" method="post">

    <label for="amount">Amount :</label>
    <input type="float" id="amount" name="amount" required><br>

    <label for="date">Date :</label>
    <input type="date" id="date" name="date" value="%s-%s-%s" required><br>""" % (user, str(today.year), get_date_string_plus_0(today.month), get_date_string_plus_0(today.day)))

    print("""
    <label for="type">Type :</label>
    <select name="type" id="type" required>""")

    gen_http_select_type(types_list)
    print("</select><br>")

    print("""
    <label for="method">Pay Method :</label>
    <select name="method" id="method" required>""")
    gen_http_select_type(method_list)
    print("</select><br>")

    print("""<br>
    <input type="submit" value="Submit">
    </form>

    </body>
    </html>""")

def do_POST(hlr):
    ## Parsing data from the HTTP server
    form = cgi.FieldStorage()

    date = (form.getfirst('date', 'empty'))
    exp_type = (form.getfirst('type', 'empty'))
    exp_method = (form.getfirst('method', 'empty'))
    amount = (form.getfirst('amount', 'empty')).replace(",",".")

    hlr.add_new_exp(date_str=date, amount_float=float(amount), exp_type=exp_type, pay_method=exp_method)

    print ("Content-Type: text/html")
    print("")
    print ("<html><body>")
    print ("<title>Expense Tracker</title>")
    print ("<h2>New Expense taken into account !</h2>")
    print ("<p>")
    print ("Spent %.1f euros on %s" % (float(amount), exp_type))
    print("</p>")
    print("<button onclick=\"window.location.href='/sandbox/cgi-bin/handle_finance.py'\">New Expense ?</button>")
    print("</body></html>")

    hlr.save_data()

hlr = exp_handler(all)

if os.environ['REQUEST_METHOD'] == "GET":
    do_GET(hlr.get_types(), hlr.get_pay_methods())
else:
    do_POST(hlr)

