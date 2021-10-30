#!/usr/bin/env python

import cgi
import os

from backend.compute_expense import exp_handler
from backend.show_expense import exp_shower

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


def gen_http_form(types_list, method_list, benef_list):
    today = datetime.datetime.now()
    print("""<form action="/sandbox/cgi-bin/handle_finance.py" method="post">

    <label for="amount">Amount :</label>
    <input type="float" id="amount" name="amount" required><br>

    <label for="date">Date :</label>
    <input type="date" id="date" name="date" value="%s-%s-%s" required><br>""" % (str(today.year), get_date_string_plus_0(today.month), get_date_string_plus_0(today.day)))

    print("""
    <label for="type">Type :</label>
    <select name="type" id="type" required>""")

    gen_http_select_type(types_list)
    print("<option value=\"reboursement\"> remboursement</option>")
    print("</select><br>")

    print("""
    <label for="method">Pay Method :</label>
    <select name="method" id="method" required>""")
    gen_http_select_type(method_list)
    print("</select><br>")

    print("""
    <label for="benef">Beneficiary :</label>
    <select name="benef" id="benef" required>""")
    gen_http_select_type(benef_list)
    print("</select><br>")

    print("""<br>
    <input type="submit" value="Submit">
    </form>""")

def show_graphs(shw):
    print("<h3> Small recap on last 7 days expenses :</h3>")
    print("<img src=\"%s\" alt=\"Last 7 days\" width=\"800\" height=\"600\">" % shw.get_fig_name()[0])
    print("<h3> The bigger picture :</h3>")
    ac_owes = round(shw.get_owns_what_month("AC", "Tony", 0),2)
    if ac_owes > 0:
        print(f"<p> AC owes Tony {ac_owes}e this month </p>")
    else:
        print(f"<p> Tony owes AC {-ac_owes}e this month </p>")
    ac_owes = round(shw.get_owns_what_month("AC", "Tony", 1),2)
    if ac_owes > 0:
        print(f"<p> AC owes Tony {ac_owes}e from last month </p>")
    else:
        print(f"<p> Tony owes AC {-ac_owes}e from last month </p>")
    print("<img src=\"%s\" alt=\"This month\" width=\"50%%\">" % shw.get_fig_name()[1])
    print("<img src=\"%s\" alt=\"Last year\" width=\"50%%\">" % shw.get_fig_name()[3])
    print("<img src=\"%s\" alt=\"Past 12 months\" width=\"50%%\">" % shw.get_fig_name()[2])

def gen_edit_button(dic):
    print("<h3> Couple of the last entries: </h3>")
    oldest_idx = len(dic['Date'])-1
    min_idx = oldest_idx - 20
    for i in range(oldest_idx, min_idx, -1):
        print(f"{i} : " + dic['Date'][i].strftime("%d %b %y") + f" : {dic['Amount'][i]}e for {dic['Benef'][i]} on {dic['Type'][i]} with {dic['Method'][i]} <br>")
    print("<br><button onclick=\"window.location.href='/sandbox/cgi-bin/edit_finance.py'\">Edit expenses data</button>")
    print("""<form action="/sandbox/cgi-bin/rm_colors.py" method="post"><input type="submit" value="Change Colors"></form>""")

def do_GET(hlr):
    shw = exp_shower(user, hlr.get_dic(), hlr.get_types(), hlr.get_pay_methods(), hlr.get_benefs())
    shw.gen_charts()

    types_list = hlr.get_types()
    method_list = hlr.get_pay_methods()
    benef_list = hlr.get_benefs()
    print("""<!DOCTYPE html>
    <html>
    <body>

    <title>Expense Tracker</title>

    <h2>Hello %s ! New Expense ?</h2>""" % user)

    gen_http_form(types_list, method_list, benef_list)
    show_graphs(shw)
    gen_edit_button(hlr.get_dic())
    
    print("""</body>
    </html>""")

def do_POST(hlr):
    ## Parsing data from the HTTP server
    form = cgi.FieldStorage()

    date = (form.getfirst('date', 'empty'))
    exp_type = (form.getfirst('type', 'empty'))
    exp_method = (form.getfirst('method', 'empty'))
    benef = (form.getfirst('benef', 'empty'))
    amount = (form.getfirst('amount', 'empty')).replace(",",".")
    
    hlr.add_new_exp(date_str=date, amount_float=float(amount), exp_type=exp_type, pay_method=exp_method, benef=benef)
    
    shw = exp_shower(user, hlr.get_dic(), hlr.get_types(), hlr.get_pay_methods(), hlr.get_benefs())
    shw.gen_charts()

    print ("Content-Type: text/html")
    print("")
    print ("<html><body>")
    print ("<title>Expense Tracker</title>")
    print ("<h2>New Expense taken into account !</h2>")
    print ("<p>")
    print ("Spent %.1f euros with %s on %s for %s" % (float(amount), exp_method, exp_type, benef))
    print("</p>")
    print("<h3> Another Expense ?</h3>")
    
    gen_http_form(hlr.get_types(), hlr.get_pay_methods(), hlr.get_benefs())
    show_graphs(shw)
    gen_edit_button()
    
    hlr.save_data()

hlr = exp_handler("all")

if os.environ['REQUEST_METHOD'] == "GET":
    do_GET(hlr)
else:
    do_POST(hlr)

