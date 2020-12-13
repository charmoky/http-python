#!/usr/bin/env python

import cgi
from backend.compute_sleep import sleep_handler
import os

import datetime

def do_GET():
    today = datetime.datetime.now()
    daydiff = datetime.timedelta(days=1)
    yesterday = today - daydiff
    print("""<!DOCTYPE html>
    <html>
    <body>

    <title>Sleep Tracker</title>

    <h2>Good Morning !</h2>

    <form action="/sandbox/cgi-bin/handle_sleep.py" method="post">
    <label for="toBed_time">Asleep  at:</label><br>
    <input type="time" id="toBed_time" name="toBed_time" value="22:30" required>
    <label for="toBed_date"></label>
    <input type="date" id="toBed_date" name="toBed_date" value="%s-%s-%s" required><br>

    <label for="upBed_time">Woken at:</label><br>
    <input type="time" id="upBed_time" name="upBed_time" value="%s:%s" required>
    <label for="upBed_date"></label>
    <input type="date" id="upBed_date" name="upBed_date" value="%s-%s-%s" required><br><br>

    <input type="submit" value="Submit">
    </form>

    </body>
    </html>""" % (str(today.year), str(today.month), str(yesterday.day), str(today.hour), str(today.minute), str(today.year), str(today.month), str(today.day)))

def do_POST():
    ## Parsing data from the HTTP server
    form = cgi.FieldStorage()

    toBed_time = (form.getfirst('toBed_time', 'empty'))
    upBed_time = (form.getfirst('upBed_time', 'empty'))
    toBed_date = (form.getfirst('toBed_date', 'empty'))
    upBed_date = (form.getfirst('upBed_date', 'empty'))

    hlr = sleep_handler()

    hlr.add_new_time(time_bed_str=toBed_time, date_bed_str=toBed_date, time_up_str=upBed_time, date_up_str=upBed_date)
    hlr.gen_graph_last_7days()

    print ("Content-Type: text/html")
    print("")
    print ("<html><body>")
    print ("<h2>Good morning !</h2>")
    print ("<p>")
    print ("Slept for %sh%s : went to bed at %s, woke up at %s" % (str(hlr.get_time_slept()[0]), str(hlr.get_time_slept()[1]), str(toBed_time), str(upBed_time)))
    print("</p>")
    print ("<p>")
    print("Last week average is %sh%s" % (str(hlr.get_average()[0]), str(hlr.get_average()[1])))
    print("</p>")
    print("<img src=\"%s\" alt=\"Last 7 days average\" width=\"800\" height=\"600\">" % hlr.get_fig_name())
    print("</body></html>")

    hlr.save_data()

if os.environ['REQUEST_METHOD'] == "GET":
    do_GET()
else:
    do_POST()

