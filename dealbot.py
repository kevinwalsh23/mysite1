#import cs50
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
import datetime, time
#from helpers import *
from sqlalchemy import DATE, cast
#from flask_jsglue import JSGlue
import os
import re
import json
import random
import sys
import requests
import sqlite3
from keys import *
import tweepy
#from application import db


#db = SQL("sqlite:///newdb.db")
db = SQL("sqlite:///newdb.db")
#db = sqlite3.connect('newdb.db')
#conn = sqlite3.connect('database.db')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def message_gen(deal):
    x = (deal['hood'] + ' Deal Alert: At ' + deal['bar_name'] + ' between ' + deal['time_start'] + ' and ' + deal['time_end'] + ', ''' + deal['deal'] + '. Find more great NYC deals at dealbly.com! #nyc #deals')
    return x
def dealtweet():
    print('hello')

    today = datetime.date.today()
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
            #print(week_day)
        else:
            week_day = 6

    steals = db.execute("SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily JOIN hoods as f on a.zip = f.codezip WHERE :seconds >= minuteman AND :seconds <= mininterval AND daynum = :weekd ORDER BY time_start ASC", weekd = week_day, seconds=seconds)

    #steals = db.execute(SELECT * FROM bars AS a JOIN deals AS b ON a.bar_id = b.id_bar JOIN weekday AS c ON b.day_of_week = c.day_week JOIN dailyhour AS d ON b.time_start = d.timehour JOIN hourdaily as e on b.time_end = e.hdaily WHERE :seconds >= 'minuteman' AND :seconds <= mininterval AND daynum = :weekd ORDER BY time_start ASC, weekd = week_day, seconds=seconds)
    #print(steals)
    num = len(steals)
    print(num)
    randomnum = random.randint(1, num)
    #print(x[randnum])
    if len(steals) != 0:
        x = steals[randomnum]
        print(x)
    else:
        return 0
        #print(x['hood'])

    print(randomnum)




    api.update_status(message_gen(x))
    #return 5



if __name__ == "__main__":

    dealtweet()