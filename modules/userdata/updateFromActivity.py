####################################
#
# 'userdata - updateFromActivity' module for qqBot by Paszq
#
# adds user information to database from 'activity' DB table
#
####################################

#Count execution time
from datetime import datetime, timedelta
startTime = datetime.now()
from datetime import date

#Imports
import os
import sys, getopt
import mysql.connector
from os.path import exists
import json #JSON read/write capability

#Read JSON config
if exists("../../config.json"):
    json_file = open("../../config.json")
elif exists("config.json"):
    json_file = open("config.json")
else:
    print("No config.json found")
    exit(2)
config = json.load(json_file)

#Settings & DB
pathToScript = os.path.dirname(os.path.realpath(__file__))
mydb = mysql.connector.connect(
          host=config["dbhost"],
            user=config["dbuser"],
              password=config["dbpass"],
                database=config["dbname"],
                )
mycursor = mydb.cursor()

#Fetch unique rows from activity
mycursor.execute("SELECT userId, username FROM `activity` GROUP BY `userId`;")
activityData = mycursor.fetchall()
#Iterate over activity results
for row in activityData:
    discord_user_id = str(row[0])
    discord_user_name = str(row[1])
    os.system("python3 addUserData.py -d "+discord_user_id+" -u \""+discord_user_name+"\"")