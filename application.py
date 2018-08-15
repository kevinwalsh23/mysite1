
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
import datetime, time
from helpers import *
from sqlalchemy import DATE, cast
from flask_jsglue import JSGlue
from cs50 import SQL
import os
import re
import json
#import MySQLdb
from flask_sslify import SSLify
#from flask.ext.sqlalchemy import SQLAlchemy

# configure application
app = Flask(__name__)

JSGlue(app)
sslify = SSLify(app)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response
#SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{kevinwalsh23}:{May221993$}@{kevinwalsh23.mysql.pythonanywhere-services.com}/{kevinwalsh23$finale}".format
#SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
#    username="kevinwalsh23",
##    password="May221993$",
 #   hostname="kevinwalsh23.mysql.pythonanywhere-services.com",
#    databasename="kevinwalsh23$finale",
#)
#app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
#app.config["SQLALCHEMY_POOL_RECYCLE"] = 299

#db = SQLAlchemy(app)

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
#db = SQL("sqlite:///kevinwalsh23.mysql.pythonanywhere-services.com")
#db = SQL("kevinwalsh23.mysql.pythonanywhere-services.com")
#db = DAL('mysql://<kevinwalsh23>:<May221993$>@<kevinwalsh23.mysql.pythonanywhere-services.com>/<finale>')
db = SQL("sqlite:///newdb.db")


@app.route("/")
#@login_required
def index():


    today = datetime.date.today()
    #print(today)
    week_day = datetime.datetime.today().weekday()


    now = datetime.datetime.utcnow()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

    secondundo = int(((now - midnight).seconds) / 60)

    #Time is based off UTC Time, which is 5 hours ahead (CHECK DAYLIGHT SAVINGS TIME, COULD CHANGE TO 4 Hours)
    #1440 minutes in day, this is saying if time between 1159pm and 5am, subtract the 5 hours
    #else need to add 19 hours forwards to account that it is between 7PM and Midnight (19HR to 24HR)
    #TO DO: When adding these forward, we are pulling deals from the following day, and we need to account for this by subtracting 1 from the given day

    if (secondundo < 1439 and secondundo > 240):
        seconds = int((((now - midnight).seconds) / 60) - 240)
    else:
        seconds = int((((now - midnight).seconds) / 60) + 1200)

        #Still dealing with UTC Time, so the day of week will always be one ahead during 7pm to midnight EST (midnight to 5 UTC)
        #Subtracting one if time is in this interval to account for that so correct deals appear from correct day

        if week_day != 0:
            week_day -= 1
            #print(week_day)
        else:
            week_day = 6


    steals = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as f on f.id = a.bar_id WHERE :seconds >= minuteman AND :seconds <= mininterval AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, seconds=seconds)

    upcomingdeals = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as f on f.id = a.bar_id WHERE :seconds <= minuteman AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, seconds=seconds)

    barjson = json.dumps(steals)
    day_hour = datetime.datetime.today().time()

    if len(steals) == 0 and len(upcomingdeals) != 0:
        return render_template("index.html", upcomingdeals=upcomingdeals, seconds=seconds,  key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))
    elif len(steals) != 0 and len(upcomingdeals) == 0:
        return render_template("index.html", steals=steals, seconds=seconds,  key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))

    elif len(steals) == 0 and len(upcomingdeals) == 0:
        return render_template("index.html", seconds=seconds,  key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))

    else:
        return render_template("index.html", steals=steals, upcomingdeals=upcomingdeals, seconds=seconds, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))


@app.route("/indexsearch")
def indexsearch():



    now = datetime.datetime.utcnow()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    secondundo = int(((now - midnight).seconds) / 60)
    week_day = datetime.datetime.today().weekday()

    #Time is based off UTC Time, which is 5 hours ahead (CHECK DAYLIGHT SAVINGS TIME, COULD CHANGE TO 4 Hours)
    #1440 minutes in day, this is saying if time between 1159pm and 5am, subtract the 5 hours
    #else need to add 19 hours forwards to account that it is between 7PM and Midnight (19HR to 24HR)
    #TO DO: When adding these forward, we are pulling deals from the following day, and we need to account for this by subtracting 1 from the given day

    if (secondundo < 1439 and secondundo > 240):
        seconds = int((((now - midnight).seconds) / 60) - 240)
    else:
        seconds = int((((now - midnight).seconds) / 60) + 1200)

        #Still dealing with UTC Time, so the day of week will always be one ahead during 7pm to midnight EST (midnight to 5 UTC)
        #Subtracting one if time is in this interval to account for that so correct deals appear from correct day
        if week_day != 0:
            week_day -= 1
        else:
            week_day = 6

    start = db.execute("SELECT timehour from dailyhour WHERE :start = hournumb", start=request.args.get("start_time") )
    end = db.execute("SELECT timehour from dailyhour WHERE :start = hournumb", start=request.args.get("end_time") )
    query = [ request.args.get("zipnasty"), request.args.get("keyword"), start, end ]

    if len(start) != 0:
        starts = start[0]['timehour']
    if len(end) != 0:
        ends = end[0]['timehour']

    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    day = request.args.get("day")

    if day == 'today':

        if start_time == "live_start" and end_time == "live_end":

            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                zipresults = db.execute("SELECT DISTINCT deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, rating, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = week_day, keyword = y, search = x)
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")
                response = "Showing today's deals for " + b  + " in " + a +  "."

            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                y = request.args.get("zipnasty")
                zipresults = db.execute("SELECT DISTINCT bar_id, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, rating, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = week_day, search = x)
                response = "Showing today's deals in " + y +  "."

            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT bar_id, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, rating, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = week_day, search = y)
                response = "Showing today's deals for " + z + "."

            else:
                zipresults = db.execute("SELECT DISTINCT bar_id, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, rating, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd ORDER BY time_start ASC", weekd = week_day)
                response = "Showing today's live deals."

        elif start_time != "live_start" and end_time == "live_end":
            #if start time exists, but end time does not
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = week_day, keyword = y, search = x, start_time=start_time, end_time=start_time)
                response = "Showing today's deals, live at " + starts + ", for " + b  + " in " + a +  "."

            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                y = request.args.get("zipnasty")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = week_day, search = x, start_time=start_time, end_time=start_time)
                response = "Showing today's deals, live at " + starts + ", in " + y +  "."

            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = week_day, search = y, start_time=start_time, end_time=start_time)
                response = "Showing today's deals, live at " + starts + ", for " + z + "."


            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, start_time=start_time, end_time=start_time)
                response = "Showing today's deals, live at " + starts + "."

        elif start_time == "live_start" and end_time != "live_end":
            #if end time, but no start time, show all deals live at the end time submitted
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time > hournumb AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = week_day, keyword = y, search = x, start_time=start_time)
                response = "Showing today's deals, live before " + ends + ", for " + b  + " in " + a +  "."

            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time > hournumb AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = week_day, search = x, start_time=start_time)
                y = request.args.get("zipnasty")
                response = "Showing today's deals, live before " + ends + ", in " + y +  "."
            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as f on f.id = a.bar_id WHERE :start_time > hournumb AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = week_day, search = y, start_time=start_time)
                response = "Showing today's deals, live before " + ends + ", for " + z + "."

            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time > hournumb AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, start_time=end_time)
                response = "Showing today's deals, live before " + ends + "."

        elif start_time >= end_time:
            response = "Error in your search: The deal's starting time cannot be after its ending time."
            zipresults = []
            #return render_template("indexsearch.html", query=query, seconds=seconds, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))

        else:
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT bar_id, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, rating, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = week_day, keyword = y, search = x, start_time=start_time, end_time=end_time)
                response = "Showing today's deals, live between " + starts + " and " + ends + ", for " + b  + " in " + a +  "."


            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                y = request.args.get("zipnasty")
                zipresults = db.execute("SELECT DISTINCT bar_id, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, rating, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = week_day, search = x, start_time=start_time, end_time=end_time)
                response = "Showing today's deals, live between " + starts + " and " + ends + ", in " + y +  "."

            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT bar_id, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, rating, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = week_day, search = y, start_time=start_time, end_time=end_time)
                response = "Showing today's deals, live between " + starts + " and " + ends + ", for " + z + "."

            else:
                zipresults = db.execute("SELECT DISTINCT bar_id, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, rating, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, start_time=start_time, end_time=end_time)
                response = "Showing today's deals, live between " + starts + " and " + ends + "."

        if len(zipresults) == 0:
            return render_template("indexsearch.html", query=query, seconds=seconds, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"), response=response)
        else:
            return render_template("indexsearch.html", zipresults=zipresults, seconds=seconds, query=query, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"), response=response)

    else:
        day_filter = db.execute("SELECT day_week FROM weekday WHERE daynum = :weekd", weekd=day)
        theday = day_filter[0]['day_week']
        if start_time == "live_start" and end_time == "live_end":

            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = day, keyword = y, search = x)
                response = "Showing " + theday + "'s deals for " + b  + " in " + a +  "."

            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                y = request.args.get("zipnasty")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = day, search = x)
                response = "Showing " + theday + "'s deals in " + y +  "."

            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = day, search = y)

                response = "Showing " + theday + "'s deals for " + z + "."
                print(zipresults)
            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd ORDER BY time_start ASC", weekd = day)

                response = "Showing " + theday + "'s live deals."


        elif start_time != "live_start" and end_time == "live_end":
            #if start time exists, but end time does not
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id JOIN hoods AS f ON a.zip = f.codezip WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = day, keyword = y, search = x, start_time=start_time, end_time=start_time)
                response = "Showing  " + theday + "'s deals, live at " + starts + ", for " + b  + " in " + a +  "."


            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                y = request.args.get("zipnasty")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily  JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = day, search = x, start_time=start_time, end_time=start_time)
                response = "Showing  " + theday + "'s deals, live at " + starts + ", in " + y +  "."


            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = day, search = y, start_time=start_time, end_time=start_time)
                response = "Showing  " + theday + "'s deals, live at " + starts + ", for " + z + "."

            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd ORDER BY time_start ASC", weekd = day, start_time=start_time, end_time=start_time)

                response = "Showing  " + theday + "'s deals, live at " + starts + "."

        elif start_time == "live_start" and end_time != "live_end":
            #if start time exists, but end time does not
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = day, keyword = y, search = x, start_time=start_time, end_time=start_time)
                response = "Showing  " + theday + "'s deals, live before " + ends + ", for " + b  + " in " + a +  "."

            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                y = request.args.get("zipnasty")

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = day, search = x, start_time=start_time, end_time=start_time)
                response = "Showing  " + theday + "'s deals, live before " + ends + ", in " + y +  "."
            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = day, search = y, start_time=start_time, end_time=start_time)
                response = "Showing  " + theday + "'s deals, live before " + ends + ", for " + z + "."
                print(zipresults)
            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd ORDER BY time_start ASC", weekd = day, start_time=start_time, end_time=start_time)
                response = "Showing  " + theday + "'s deals, live before " + ends + "."
            #return render_template("indexsearch.3.html")

        elif start_time >= end_time:
            #if start greater than end, return message, start cannot be after end
            #create javascript logic that does not allow you to search with these params
            #return render_template("indexsearch.3.html")
            response = "Error in your search: The deal's starting time cannot be after its ending time."
            zipresults = []

        else:
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = day, keyword = y, search = x, start_time=start_time, end_time=end_time)
                response = "Showing  " + theday + "'s deals, live between " + starts + " and " + ends + ", for " + b  + " in " + a +  "."

            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = day, search = x, start_time=start_time, end_time=end_time)
                y = request.args.get("zipnasty")
                response = "Showing  " + theday + "'s deals, live between " + starts + " and " + ends + ", in " + y +  "."
            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = day, search = y, start_time=start_time, end_time=end_time)
                response = "Showing  " + theday + "'s deals, live between " + starts + " and " + ends + ", for " + z + "."
                print(zipresults)
            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd ORDER BY time_start ASC", weekd = day, start_time=start_time, end_time=end_time)
                response = "Showing  " + theday + "'s deals, live between " + starts + " and " + ends + "."

        if len(zipresults) == 0:
            return render_template("indexsearch.html", query=query, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"), response=response)
        else:
            return render_template("indexsearch.html", seconds=seconds, zipresults=zipresults, query=query, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"), response=response)

@app.route("/login", methods=["POST", "GET"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"))

        # ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"))

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return render_template("login.html", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"))

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"), canon="/mobilelogin")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("index"))

@app.route("/mapadd", methods=["POST", "GET"])
def mapadd():
    """Log user out."""

    print("dickhead")
    today = datetime.date.today()
    print(today)
    week_day = datetime.datetime.today().weekday()
    print(request.args.get("keyword"))

    now = datetime.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

    secondundo = int(((now - midnight).seconds) / 60)
    y = request.form.get("keyword")
    #if y:
    #print(y)
    x = request.args.get("zipnasty")
    #if x:
    #print(x)

    #Time is based off UTC Time, which is 5 hours ahead (CHECK DAYLIGHT SAVINGS TIME, COULD CHANGE TO 4 Hours)
    #1440 minutes in day, this is saying if time between 1159pm and 5am, subtract the 5 hours
    #else need to add 19 hours forwards to account that it is between 7PM and Midnight (19HR to 24HR)
    #TO DO: When adding these forward, we are pulling deals from the following day, and we need to account for this by subtracting 1 from the given day

    if (secondundo < 1439 and secondundo > 240):
        seconds = int((((now - midnight).seconds) / 60) - 240)
    else:
        seconds = int((((now - midnight).seconds) / 60) + 1200)

        #Still dealing with UTC Time, so the day of week will always be one ahead during 7pm to midnight EST (midnight to 5 UTC)
        #Subtracting one if time is in this interval to account for that so correct deals appear from correct day
        if week_day != 0:
            week_day -= 1
            #print(week_day)
        else:
            week_day = 6
    # forget any user_id
    #if request.args.get("zipnasty") != None:
    if x:
        x = request.args.get("zipnasty")  + "%"
        print(x + "asdffdsa")
        zipresults = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN hoods AS d ON a.zip = d.codezip WHERE daynum = :weekd AND a.zip LIKE :search OR d.hood LIKE :search", weekd = week_day, search = x)
        print(zipresults)
        return json.dumps(zipresults)

    elif request.args.get("keyword") != None:
        y = "%" + request.args.get("keyword")  + "%"
        zipresults = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week WHERE daynum = :weekd AND b.deal LIKE :search", weekd = week_day, search = y)
        return json.dumps(zipresults)
    else:
        zipresults = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily WHERE :seconds >= minuteman AND :seconds <= mininterval AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, seconds=seconds)
        return json.dumps(zipresults)




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        #ensure password confirmation submitted
        elif not request.form.get("confirm password"):
            return apology("must confirm password")

        # query db for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        #ensure username is available
        if len(rows) != 0:
            return apology("username not available, please try again")

        #ensure passwords match
        if request.form.get("password") != request.form.get("confirm password"):
            return render_template("register.html")

        #hash passwrod
        hash = pwd_context.encrypt(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash, email, zipcode) VALUES(:username, :hash, :email, :zipcode)", username=request.form.get('username'), hash=hash, email=request.form.get('email'), zipcode=request.form.get('zipcode'))

        #print(zipcode)
        #log user in automatically and remember who user is
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        return redirect(url_for("index"))


    else:
        return render_template("register.html", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"), canon="/mobileregister")

#@app.route("/mapsearch")
#def mapsearch():
#    """Log user out."""
#
#    today = datetime.date.today()
#    #print(today)
#    week_day = datetime.datetime.today().weekday()


#    now = datetime.datetime.now()
#    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

#    secondundo = int(((now - midnight).seconds) / 60)
#    y = request.args.get("keyword")
    #if y:
    #    print(y)
#    x = request.args.get("zipnasty")
    #print(cheese)
    #if x:
        #print(x)

#    if (secondundo < 1439 and secondundo > 240):
##        seconds = int((((now - midnight).seconds) / 60) - 240)
#    else:
#        seconds = int((((now - midnight).seconds) / 60) + 1200)
    # forget any user_id
    #if request.args.get("zipnasty") != None:
#    if x:
#        x = request.args.get("zipnasty")  + "%"
        #print(x + "!")
#        zipresults = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN hoods AS d ON a.zip = d.codezip WHERE daynum = :weekd AND a.zip LIKE :search OR d.hood LIKE :search", weekd = week_day, search = x)
        #if zipresults == None:
#        return json.dumps(zipresults)
         #   zipresults = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN hoods AS d ON a.zip = d.codezip WHERE daynum = :weekd AND d.hood LIKE :search", weekd = week_day, search = x)
        #zipresults = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily WHERE :seconds >= minuteman AND :seconds <= mininterval AND daynum = :weekd AND a.zip LIKE :search ORDER BY time_start ASC", weekd = week_day, seconds=seconds, search = x)
#    elif request.args.get("keyword") != "":
#        y = "%" + request.args.get("keyword")  + "%"
#        print(y)
#        zipresults = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week WHERE daynum = :weekd AND b.deal LIKE :search", weekd = week_day, search = y)
#        return json.dumps(zipresults)


@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"), canon="/mobileabout")

@app.route("/bar/<string:thisbar>", methods=["GET", "POST"])
def bar(thisbar):

    today = datetime.date.today()
    #print(today)
    week_day = datetime.datetime.today().weekday()

    now = datetime.datetime.utcnow()
    print('NOW' + str(now))
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    #secondundo is the amount of seconds away from midnight in UTC Time
    secondundo = int(((now - midnight).seconds) / 60)
    #print(str(secondundo)+'PIGS')

    #Time is based off UTC Time, which is 5 hours ahead (CHECK DAYLIGHT SAVINGS TIME, COULD CHANGE TO 4 Hours)
    #1440 minutes in day, this is saying if time between 1159pm and 5am, subtract the 5 hours
    #else need to add 19 hours forwards to account that it is between 7PM and Midnight (19HR to 24HR)
    #TO DO: When adding these forward, we are pulling deals from the following day, and we need to account for this by subtracting 1 from the given day

    if (secondundo < 1439 and secondundo > 240):
        seconds = int((((now - midnight).seconds) / 60) - 240)
    else:
        seconds = int((((now - midnight).seconds) / 60) + 1200)

        #Still dealing with UTC Time, so the day of week will always be one ahead during 7pm to midnight EST (midnight to 5 UTC)
        #Subtracting one if time is in this interval to account for that so correct deals appear from correct day
        if week_day != 0:
            week_day -= 1
            #print(week_day)
        else:
            week_day = 6

    todaydeal = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily WHERE :seconds >= minuteman AND :seconds <= mininterval AND daynum = :weekd AND bar_name = :thisbar ORDER BY time_start ASC", weekd = week_day, seconds=seconds, thisbar=thisbar)


    barry = db.execute("SELECT * FROM bars as a JOIN ratings as b ON a.bar_id = b.id WHERE bar_name = :thisbar", thisbar=thisbar)

    sunday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Sunday' ORDER by time_start", thisbar=thisbar)
    monday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Monday' ORDER by time_start", thisbar=thisbar)
    tuesday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Tuesday' ORDER by daynum", thisbar=thisbar)
    wednesday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Wednesday' ORDER by daynum", thisbar=thisbar)
    thursday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Thursday' ORDER by daynum", thisbar=thisbar)
    friday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Friday' ORDER by daynum", thisbar=thisbar)
    saturday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Saturday' ORDER by daynum", thisbar=thisbar)

    zipresults = db.execute("SELECT * FROM bars ORDER by bar_name")#daynum = #:weekd ORDER BY time_start ASC", weekd = week_day, seconds=seconds


    return render_template("bar.html", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"), canon="/mobilebar", todaydeal=todaydeal, bars=zipresults, barry=barry, sunday=sunday, monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday, friday=friday, saturday=saturday)

@app.route("/rests", methods=["GET", "POST"])
def rests():

    zipresults = db.execute("SELECT * FROM bars as a JOIN hoods as b on a.zip = b.codezip JOIN ratings as c on c.id = a.bar_id ORDER by hood")


    return render_template("rests.html", bars=zipresults,key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"), canon="/mobilerestaurants")

#MOBILE FUNCTION AD/DED
@app.route("/mobile", methods=["GET", "POST"])
#@login_required
def mobile():


    today = datetime.date.today()
    week_day = datetime.datetime.today().weekday()

    now = datetime.datetime.utcnow()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)


    #secondundo is the amount of seconds away from midnight in UTC Time
    secondundo = int(((now - midnight).seconds) / 60)


    #Time is based off UTC Time, which is 5 hours ahead (CHECK DAYLIGHT SAVINGS TIME, COULD CHANGE TO 4 Hours)
    #1440 minutes in day, this is saying if time between 1159pm and 5am, subtract the 5 hours
    #else need to add 19 hours forwards to account that it is between 7PM and Midnight (19HR to 24HR)
    #TO DO: When adding these forward, we are pulling deals from the following day, and we need to account for this by subtracting 1 from the given day

    if (secondundo < 1439 and secondundo > 240):
        seconds = int((((now - midnight).seconds) / 60) - 240)
    else:
        seconds = int((((now - midnight).seconds) / 60) + 1200)

        #Still dealing with UTC Time, so the day of week will always be one ahead during 7pm to midnight EST (midnight to 5 UTC)
        #Subtracting one if time is in this interval to account for that so correct deals appear from correct day
        if week_day != 0:
            week_day -= 1

        else:
            week_day = 6

    steals = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as f on f.id = a.bar_id WHERE :seconds >= minuteman AND :seconds <= mininterval AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, seconds=seconds)

    upcomingdeals = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as f on f.id = a.bar_id WHERE :seconds <= minuteman AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, seconds=seconds)

    barjson = json.dumps(steals)

    day_hour = datetime.datetime.today().time()

    now = datetime.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    #seconds = int((((now - midnight).seconds) / 60) - 240)

    if len(steals) == 0 and len(upcomingdeals) != 0:
        return render_template("/mobile/mobile9.html", seconds=seconds, upcomingdeals=upcomingdeals, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))

    elif len(steals) != 0 and len(upcomingdeals) == 0:
        return render_template("/mobile/mobile9.html", seconds=seconds, steals=steals, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))

    elif len(steals) == 0 and len(upcomingdeals) == 0:
        return render_template("/mobile/mobile9.html", seconds=seconds, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))

    else:
        return render_template("/mobile/mobile9.html", seconds=seconds, steals=steals, upcomingdeals=upcomingdeals, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))



@app.route("/mobilesearch")
def mobilesearch():


    week_day = datetime.datetime.today().weekday()
    now = datetime.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    secondundo = int(((now - midnight).seconds) / 60)

    if (secondundo < 1439 and secondundo > 240):
        seconds = int((((now - midnight).seconds) / 60) - 240)
    else:
        seconds = int((((now - midnight).seconds) / 60) + 1200)

        #Still dealing with UTC Time, so the day of week will always be one ahead during 7pm to midnight EST (midnight to 5 UTC)
        #Subtracting one if time is in this interval to account for that so correct deals appear from correct day
        if week_day != 0:
            week_day -= 1
        else:
            week_day = 6


    start = db.execute("SELECT timehour from dailyhour WHERE :start = hournumb", start=request.args.get("start_time") )
    end = db.execute("SELECT timehour from dailyhour WHERE :start = hournumb", start=request.args.get("end_time") )
    query = [ request.args.get("zipnasty"), request.args.get("keyword"), start, end ]
    day = request.args.get("day")

    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    if day == 'today':
        if start_time == "live_start" and end_time == "live_end":

            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"

                zipresults = db.execute("SELECT DISTINCT rating, bar_id, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = week_day, keyword = y, search = x)

            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                zipresults = db.execute("SELECT DISTINCT rating, bar_id, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = week_day, search = x)

            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"

                zipresults = db.execute("SELECT DISTINCT bar_id, rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = week_day, search = y)

            else:
                zipresults = db.execute("SELECT DISTINCT bar_id, rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd ORDER BY time_start ASC", weekd = week_day)


        elif start_time != "live_start" and end_time == "live_end":
            #if start time exists, but end time does not
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = week_day, keyword = y, search = x, start_time=start_time, end_time=start_time)

            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = week_day, search = x, start_time=start_time, end_time=start_time)

            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = week_day, search = y, start_time=start_time, end_time=start_time)

                print(zipresults)
            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, start_time=start_time, end_time=start_time)

        elif start_time == "live_start" and end_time != "live_end":
            #if end time, but no start time, show all deals live at the end time submitted
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time > hournumb AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = week_day, keyword = y, search = x, start_time=start_time)

            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time > hournumb AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = week_day, search = x, start_time=start_time)

            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as f on f.id = a.bar_id WHERE :start_time > hournumb AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = week_day, search = y, start_time=start_time)

                print(zipresults)
            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time > hournumb AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, start_time=end_time)

        elif start_time >= end_time:
            zipresults = []
            response = "Error in Search: Start time cannot be after End Time!"
        else:
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"

                zipresults = db.execute("SELECT DISTINCT bar_id, rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = week_day, keyword = y, search = x, start_time=start_time, end_time=end_time)

            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                zipresults = db.execute("SELECT DISTINCT bar_id, rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = week_day, search = x, start_time=start_time, end_time=end_time)

            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"

                zipresults = db.execute("SELECT DISTINCT bar_id, rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = week_day, search = y, start_time=start_time, end_time=end_time)

                print(zipresults)
            else:
                zipresults = db.execute("SELECT DISTINCT bar_id, rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, start_time=start_time, end_time=end_time)

        #return render_template("/mobile/mobilesearch.html", zipresults=zipresults, query=query, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))
        if len(zipresults) == 0:
            return render_template("/mobile/mobilesearch.html", seconds=seconds, query=query, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))
        else:
            return render_template("/mobile/mobilesearch.html", seconds=seconds, zipresults=zipresults, query=query, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))
    else:
        day_filter = db.execute("SELECT day_week FROM weekday WHERE daynum = :weekd", weekd=day)
        theday = day_filter[0]['day_week']
        if start_time == "live_start" and end_time == "live_end":

            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = day, keyword = y, search = x)

            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                y = request.args.get("zipnasty")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = day, search = x)


            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = day, search = y)

            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE daynum = :weekd ORDER BY time_start ASC", weekd = day)



        elif start_time != "live_start" and end_time == "live_end":
            #if start time exists, but end time does not
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = day, keyword = y, search = x, start_time=start_time, end_time=start_time)


            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                y = request.args.get("zipnasty")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = day, search = x, start_time=start_time, end_time=start_time)



            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = day, search = y, start_time=start_time, end_time=start_time)


            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd ORDER BY time_start ASC", weekd = day, start_time=start_time, end_time=start_time)


        elif start_time == "live_start" and end_time != "live_end":
            #if start time exists, but end time does not
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = day, keyword = y, search = x, start_time=start_time, end_time=start_time)


            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                y = request.args.get("zipnasty")

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = day, search = x, start_time=start_time, end_time=start_time)

            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")

                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = day, search = y, start_time=start_time, end_time=start_time)
            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time < numbhour AND daynum = :weekd ORDER BY time_start ASC", weekd = day, start_time=start_time, end_time=start_time)


        elif start_time >= end_time:
            #if start greater than end, return message, start cannot be after end
            #create javascript logic that does not allow you to search with these params
            #return render_template("indexsearch.3.html")
            response = "Error in your search: The deal's starting time cannot be after its ending time."
            zipresults = []

        else:
            if request.args.get("zipnasty") != "" and request.args.get("keyword") != "":
                x = request.args.get("zipnasty")  + "%"
                y = "%" + request.args.get("keyword")  + "%"
                a = request.args.get("zipnasty")
                b = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND b.deal LIKE :keyword AND (a.zip LIKE :search OR f.hood LIKE :search)", weekd = day, keyword = y, search = x, start_time=start_time, end_time=end_time)


            elif request.args.get("zipnasty") != "" and request.args.get("keyword") == "":
                x = request.args.get("zipnasty")  + "%"
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods AS f ON a.zip = f.codezip JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND (a.zip LIKE :search OR f.hood LIKE :search) ORDER BY time_start ASC", weekd = day, search = x, start_time=start_time, end_time=end_time)
                y = request.args.get("zipnasty")

            elif request.args.get("keyword") != "" and request.args.get("zipnasty") == "":
                y = "%" + request.args.get("keyword")  + "%"
                z = request.args.get("keyword")
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd AND b.deal LIKE :search ORDER BY time_start ASC", weekd = day, search = y, start_time=start_time, end_time=end_time)


            else:
                zipresults = db.execute("SELECT DISTINCT rating, deal, address, phone, bar_name, city, state, zip, time_start, time_end, latitude, longitude, mininterval FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN ratings as g on g.id = a.bar_id WHERE :start_time >= hournumb AND :end_time <= numbhour AND daynum = :weekd ORDER BY time_start ASC", weekd = day, start_time=start_time, end_time=end_time)


        if len(zipresults) == 0:
            return render_template("/mobile/mobilesearch.html", seconds=seconds, query=query, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))
        else:
            return render_template("/mobile/mobilesearch.html", seconds=seconds, zipresults=zipresults, query=query, key=("AIzaSyA7ZZ0E2oWiQRLYUgZ7Hn_-i87XV6mmbNM"))

@app.route("/mobilelogin", methods=["GET","POST"])
def mobilelogin():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        #print(rows)
        #print("HELLLOOOOOO")

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return render_template("/mobile/mobilelogin.html", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"))

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for('mobile'))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        #print('TESSSSSS')
        return render_template("/mobile/mobilelogin.html", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"), canon="/login")

@app.route("/mobilelogout")
def mobilelogout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("mobile"))

@app.route("/mobileregister", methods=["GET", "POST"])
def mobileregister():
    """Register user."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return mobileregistererror("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return mobileregistererror("must provide password")

        #ensure password confirmation submitted
        elif not request.form.get("confirm password"):
            return mobileregistererror("must confirm password")

        # query db for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        #ensure username is available
        if len(rows) != 0:
            return mobileregistererror("username not available, please try again")

        #ensure passwords match
        if request.form.get("password") != request.form.get("confirm password"):
            return render_template("/mobile/mobileregister.html")

        #hash passwrod
        #CryptContext.hash(request.form.get("password"))
        hash = pwd_context.encrypt(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash, email, zipcode) VALUES(:username, :hash, :email, :zipcode)", username=request.form.get('username'), hash=hash, email=request.form.get('email'), zipcode=request.form.get('zipcode'))

        #print(zipcode)
        #log user in automatically and remember who user is
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        return redirect(url_for("mobile"))


    else:
        return render_template("/mobile/mobileregister.html", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"), canon="/register")

@app.route("/mobileabout", methods=["GET", "POST"])
def mobileabout():
    return render_template("/mobile/mobileabout.html", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"), canon="/about")

@app.route("/mobilerestaurants", methods=["GET", "POST"])
def mobilerestaurants():


    zipresults = db.execute("SELECT * FROM bars as a JOIN hoods as b on a.zip = b.codezip JOIN ratings as c on c.id = a.bar_id ORDER by hood")


    return render_template("/mobile/mobilerestaurants.html", bars=zipresults, key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"), canon="/rests")

@app.route("/mobilebar/<string:thisbar>", methods=["GET", "POST"])
def mobilebar(thisbar):


    today = datetime.date.today()
    #print(today)
    week_day = datetime.datetime.today().weekday()

    now = datetime.datetime.utcnow()
    print('NOW' + str(now))
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    #secondundo is the amount of seconds away from midnight in UTC Time
    secondundo = int(((now - midnight).seconds) / 60)
    #print(str(secondundo)+'PIGS')

    #Time is based off UTC Time, which is 5 hours ahead (CHECK DAYLIGHT SAVINGS TIME, COULD CHANGE TO 4 Hours)
    #1440 minutes in day, this is saying if time between 1159pm and 5am, subtract the 5 hours
    #else need to add 19 hours forwards to account that it is between 7PM and Midnight (19HR to 24HR)
    #TO DO: When adding these forward, we are pulling deals from the following day, and we need to account for this by subtracting 1 from the given day

    if (secondundo < 1439 and secondundo > 240):
        seconds = int((((now - midnight).seconds) / 60) - 240)
    else:
        seconds = int((((now - midnight).seconds) / 60) + 1200)

        #Still dealing with UTC Time, so the day of week will always be one ahead during 7pm to midnight EST (midnight to 5 UTC)
        #Subtracting one if time is in this interval to account for that so correct deals appear from correct day
        if week_day != 0:
            week_day -= 1
            #print(week_day)
        else:
            week_day = 6

    todaydeal = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily WHERE :seconds >= minuteman AND :seconds <= mininterval AND daynum = :weekd AND bar_name = :thisbar ORDER BY time_start ASC", weekd = week_day, seconds=seconds, thisbar=thisbar)

    todaysdeal = db.execute("SELECT * FROM deals as a JOIN bars as b on b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week JOIN dailyhour as d ON a.time_start = d.timehour JOIN hourdaily as e ON a.time_end = e.hdaily WHERE daynum = :weekd AND bar_name = :thisbar", weekd = week_day, thisbar=thisbar)

    barry = db.execute("SELECT * FROM bars as a JOIN ratings as b on b.id = a.bar_id WHERE bar_name = :thisbar", thisbar=thisbar)

    sunday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Sunday' ORDER by time_start", thisbar=thisbar)
    monday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Monday' ORDER by time_start", thisbar=thisbar)
    tuesday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Tuesday' ORDER by daynum", thisbar=thisbar)
    wednesday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Wednesday' ORDER by daynum", thisbar=thisbar)
    thursday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Thursday' ORDER by daynum", thisbar=thisbar)
    friday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Friday' ORDER by daynum", thisbar=thisbar)
    saturday = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Saturday' ORDER by daynum", thisbar=thisbar)

    today = db.execute("SELECT * FROM deals as a JOIN bars as b ON b.bar_id = a.id_bar JOIN weekday as c ON c.day_week = a.day_of_week WHERE bar_name = :thisbar AND day_of_week = 'Saturday' ORDER by daynum", thisbar=thisbar)


    zipresults = db.execute("SELECT * FROM bars ORDER by bar_name")#daynum = #:weekd ORDER BY time_start ASC", weekd = week_day, seconds=seconds


    return render_template("/mobile/mobilebar.html", canon="/bar", key=("AIzaSyDsQzORg1Gz0RMNTK_jnJLhwulK7zL2LKA"), todaydeal=todaydeal, bars=zipresults, barry=barry, sunday=sunday, monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday, friday=friday, saturday=saturday)

@app.errorhandler(500)
def internal_error(error):

    return "500 error"