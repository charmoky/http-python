#!/usr/bin/env python

import cgi
import pickle
import numpy as np
import datetime

data_filename = "/Yep/data/sleep_data.pckl"

## Parsing data from the HTTP server
form = cgi.FieldStorage()

toBed = (form.getfirst('toBed', 'empty'))
upBed = (form.getfirst('upBed', 'empty'))

def get_hour_min(time_str):
    fields = time_str.split(':')
    return [int(fields[0]), int(fields[1])]


# Assume we went to bed the day before
daydiff = datetime.timedelta(days=1)

# Get date
today = datetime.date.today()
yesterday = today - daydiff

toBed_time = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, get_hour_min(toBed)[0], get_hour_min(toBed)[1])
upBed_time = datetime.datetime(today.year, today.month, today.day, get_hour_min(upBed)[0], get_hour_min(upBed)[1])

asleep = upBed_time - toBed_time

asleep_hours, asleep_minutes = divmod(divmod(asleep.seconds, 60)[0], 60)

asleep_stored = asleep_hours * 60 + asleep_minutes
try:
    f = open(data_filename ,'rb')
    dic = pickle.load(f)
    f.close()
except IOError:
    # No data yet, create empty dataframe
    dic = {'Date' : [], 'Asleep' : [], 'Woke' : [], 'Sleep' : []}

def update_dic(colname, data):
    dic[colname].append(data)

update_dic('Date', today)
update_dic('Asleep', toBed_time)
update_dic('Woke', upBed_time)
update_dic('Sleep', asleep_stored)

print ("Content-Type: text/html")
print("")
print ("<html><body>")
print ("<h2>Good morning !</h2>")
print ("<p>")
print ("Today is %s" % str(today))
print ("</p>")
print ("<p>")
print ("Sleep for %sh%s : went to bed at %s, woke up at %s" % (str(asleep_hours), str(asleep_minutes), str(toBed_time), str(upBed_time)))
print("</p>")
print ("<p>")
print(dic)
print("</p>")
print("</body></html>")

f = open(data_filename, 'wb')
pickle.dump(dic, f)
f.close()

