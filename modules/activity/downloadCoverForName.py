####################################
#
# 'userdata - calc total activity' module for qqBot by Paszq
#
#  download cover script
#
####################################

#Count execution time
from datetime import datetime, timedelta
startTime = datetime.now()
from datetime import date 
import time

#Imports
import os
import sys, getopt
import re
import requests#For getting covers from IGDB
import mysql.connector
from os.path import exists
import json #JSON read/write capability

#Read JSON config
if exists("../../config.json"):
    json_file = open("../../config.json")
elif exists("config.json"):
    json_file = open("config.json")
elif exists("/home/pi/qbot2/config.json"):#Custom path, ex. for crontab purposes
    json_file = open("/home/pi/qbot2/config.json")
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

##Functions

def downloadCoverFromUrl(name, coverUrl):
    #print("Trying to download Cover IMAGE from Cover URL for game name: "+name+" ....using URL: "+coverUrl)
    if "https:" in coverUrl:
        #print("Correct URL was FOUND for game name: "+name)
        r = requests.get(coverUrl)  #Download cover from coverurl
        name = re.sub('[^A-Za-z0-9\-]+', '', name)
        with open(config["script_path"]+config["activity_path"]+"temp/"+name.replace(" ","")+".jpg", 'wb') as f:
            f.write(r.content)
        f.close()
        #print(coverUrl.replace("\n",""))
        return coverUrl
    else:
        #print("Correct URL was NOT FOUND for game name: "+name)
        return ""

#Get cover - function

def getCoverFromName(name):
    #get url from db
    #print("Retrieving Cover URL for Game Name: "+name+" from DATABASE")
    mycursor.execute("SELECT coverurl FROM `steamgames` WHERE `name`='"+name+"' AND `coverurl` IS NOT NULL AND `coverurl` != '' LIMIT 1;")
    coverresult = mycursor.fetchall()
    if len(coverresult) > 50:#If cover was found in DB
        #print("Cover URL for Game Name: "+name+" was FOUND in the DATABASE")
        coverUrl = str(coverresult[0][0])
        downloadCoverFromUrl(name, coverUrl)
        return coverUrl
    else:#If cover was not found in DB
        #print("Cover URL for Game Name: "+name+" was NOT FOUND in the DATABASE. Trying to add cover URL to DB using command below:")
        command = "python3 "+config["script_path"]+config["activity_path"]+"addCoverUrlToDB.py nameyear \""+name+"\""
        #print("[downloadCoverForName.py] [INFO] Add cover CMD: "+command+"         ")
        os.system(command)
        mydb.reconnect(attempts=1, delay=1)
        mycursor.execute("SELECT coverurl FROM `steamgames` WHERE `name`='"+name+"' LIMIT 1;")
        coverresult = mycursor.fetchall()
        if len(coverresult) > 0:
            coverUrl = str(coverresult[0][0]).replace("'b","").replace("\n'","").replace("\n","")
            #print("[downloadCoverForName.py] [INFO] Cover URL: "+coverUrl)
            downloadCoverFromUrl(name, coverUrl)
            return coverUrl
        return ""
       

##Script magic itself       

if len(sys.argv) > 0:
    #print("1")
    #print(" SYSARGV1: "+sys.argv[1])
    gameName = re.sub('[^A-Za-z0-9\.\-\(\) ]+', ' ', sys.argv[1])
    #print(" gameName1: "+gameName)
    gameName = re.sub('[^A-Za-z0-9\.\-\(\) ]+', ' ', gameName)
    #print(" gameName2: "+gameName+"     \n")
    
    getCoverFromName(gameName)
else:
    print("Missing arguments")
    exit
    