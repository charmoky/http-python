#!/usr/bin/env python

import cgi
from backend.activity import activity_tracker
import os

import datetime

if "REMOTE_USER" in os.environ.keys():
    user = os.environ["REMOTE_USER"]
else:
    user = "Anon"

vac_date = datetime.datetime(year=2021, month=5, day=12, hour=17, minute=30)

def gen_header():
    print("<!DOCTYPE html>")
    print("\n<html>\n<body>\n<title>Vacation is coming :D</title>")

def gen_tailer():
    print("</body></html>")

def do_GET():
    gen_header()

    now = datetime.datetime.now()

    delta = vac_date - now

    days = delta.days
    (hours, secs) = divmod(delta.seconds, 3600)
    mins = divmod(secs, 60)[0]

    picture=None
    vid=None

    if days > 10:
        print("<h2> Hang in there ! Vacations are coming I promise</h2>")
        picture = "https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fgiphygifs.s3.amazonaws.com%2Fmedia%2FmP94uHyKvY1nq%2Fgiphy.gif"
        vid="""<p> Pour garder courage en musique:</p><iframe width="560" height="315" src="https://www.youtube.com/embed/uMQp0lnRZ94" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>"""
    elif days > 7:
        print("<h2> Less than a week to go, you got this !</h2>")
        vid = """<p></p><iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/AIpv3Shdzf4\" title=\"YouTube video player\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>"""
        picture = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.reactiongifs.com%2Fr%2F2012%2F12%2Fyou-got-it-dude.gif"
    elif days > 3:
        print("<h2> Last sprint before a piña colada</h2>")
        vid = """<p></p><iframe width="560" height="315" src="https://www.youtube.com/embed/TazHNpt6OTo" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>"""
    elif days >= 1 or hours > 10:
        print("<h2> Better start packing !</h2>")
        vid = """<p>Whoop Whoop</p> <iframe width="560" height="315" src="https://www.youtube.com/embed/vWaRiD5ym74?start=38" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>"""
    else:
        print("<h2> Less than 10h, get in there Gandalf")
        vid = """<p>Theses are good 10h videos to wait</p><iframe width="560" height="315" src="https://www.youtube.com/embed/G1IbRujko-A" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
<p></p><iframe width="560" height="315" src="https://www.youtube.com/embed/0ZZTP_hoMPw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
<p></p><iframe width="560" height="315" src="https://www.youtube.com/embed/AgpWX18dby4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
<p></p><iframe width="560" height="315" src="https://www.youtube.com/embed/wSYoT_ptT00" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>"""

    print(f"<p style=\"font-size:70px;\"><b> You need to hold for </b></p>")
    
    print("<b><p id=\"timeout\" style=\"font-size:70px;\"></p></b>")

    if picture is not None:
        print(f"<img src={picture} alt=\"picture\" style=\"width:auto;\">")
    if vid is not None:
        print(f"{vid}")

    print("""
<script>
// Set the date we're counting down to
var countDownDate = new Date("May 12, 2021 17:30:00").getTime();

// Update the count down every 1 second
var x = setInterval(function() {

  // Get today's date and time
  var now = new Date().getTime();

  // Find the distance between now and the count down date
  var distance = countDownDate - now;

  // Time calculations for days, hours, minutes and seconds
  var days = Math.floor(distance / (1000 * 60 * 60 * 24));
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  // Display the result in the element with id="demo"
  document.getElementById("timeout").innerHTML = days + "d " + hours + "h "
  + minutes + "m " + seconds + "s ";

  // If the count down is finished, write some text
  if (distance < 0) {
    clearInterval(x);
    document.getElementById("demo").innerHTML = "EXPIRED";
  }
}, 1000);
</script>""")

    gen_tailer()

if os.environ['REQUEST_METHOD'] == "GET":
    do_GET()

