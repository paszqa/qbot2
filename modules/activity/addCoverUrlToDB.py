####################################
#
# 'userdata - calc total activity' module for qqBot by Paszq
#
#  add cover URL to database - script
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
import subprocess
import requests#For getting covers from IGDB
import mysql.connector
from os.path import exists
import json #JSON read/write capability
from difflib import SequenceMatcher

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

#####################################
# Functions
#####################################

#Return coverurl
def getCoverUrl(name, year=0):
    #print("Trying to ADD cover URL to DB for game name: "+name+" from year: "+str(year))
    #Check for game's cover from IGDB
    if year != 0:
        yearFilter = " & release_dates.y = '"+year+"'"
    else:
        yearFilter = ""
    # OLD COMMAND, USING SEARCH
    #command = "curl -s 'https://api.igdb.com/v4/games/' -d 'search \""+name.replace("\"","").replace(";","").replace("'","")+"\"; fields id; where category='0'"+yearFilter+"; limit 1;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][]"
    # NEW COMMAND, USING FILTER / WHERE
    #Try to find Game ID using full game name:
    command = "curl -s 'https://api.igdb.com/v4/games/' -d 'fields id; where name ~ \""+name.replace("\"","").replace(";","").replace("'","")+"\" | alternative_names.name ~ \""+name.replace("\"","").replace(";","").replace("'","")+"\""+yearFilter+"; limit 1;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][]"
    #print("\tFirst command of getCoverUrl:")
    #print("\t"+command)
    gameid=subprocess.check_output(command, shell=True).decode( "utf-8" ).strip()
    #If first method failed - try to get best name from IGDB and compare to the target
    if gameid == "" or gameid == " " or gameid == "NULL" or gameid == "null":
        #print("\t[addCoverUrlToDB.py] [INFO] Compare game name to IGDB: "+str(name))
        bestName = getIgdbName(str(name))
        if bestName != "":
            command = "curl -s 'https://api.igdb.com/v4/games/' -d 'fields id; where name ~ \""+bestName.replace("\"","").replace(";","").replace("'","")+"\" | alternative_names.name ~ \""+bestName.replace("\"","").replace(";","").replace("'","")+"\""+yearFilter+"; limit 1;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][]"
            #print("\tSecond command of getCoverUrl:")
            #print("\t"+command)
            gameid=subprocess.check_output(command, shell=True).decode( "utf-8" ).strip()
    #If second method failed - try to find Game ID using first word in the name and then grepping the rest:
    if gameid == "" or gameid == " " or gameid == "NULL" or gameid == "null":
        firstWordInName = name.split(" ")[0].split(":")[0]
        preparedGrepName = name.replace("\"","").replace(";","").replace("'","").replace(" ",".*")
        command = "curl -s 'https://api.igdb.com/v4/games/' -d 'fields name; where name ~ \""+firstWordInName+"\"*; limit 50;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][] |grep -B1 -Ei '"+preparedGrepName+"'|head -1"
        #print("\tThird command of getCoverUrl:")
        #print("\t"+command)
        gameid=subprocess.check_output(command, shell=True).decode( "utf-8" ).strip()
    #Another method to get gameid, if the last one failed
    if gameid=="" or gameid == " " or gameid == "NULL" or gameid == "null":#If not found game id, search without where-category filter
        command = "curl -s 'https://api.igdb.com/v4/games/' -d 'search \""+name.replace("\"","").replace(";","").replace("'","")+"\"; fields id; limit 1;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][]"
        #print("\tFourth command of getCoverUrl:")
        #print("\t"+command)
        gameid=subprocess.check_output(command, shell=True).decode( "utf-8" ).strip()
    command = "curl -s 'https://api.igdb.com/v4/covers/' -d 'fields url; where game = "+str(gameid)+"; limit 1;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][] "    
    #print("---")
    #print("Second command of getCoverUrl:")
    #print(command)
    coverurl=str(subprocess.check_output(command, shell=True).decode( "utf-8" ).strip())
    if len(coverurl) > 3:
        coverurl = coverurl.split("\n")[1].replace("t_thumb","t_cover_small").replace("//","https://").replace("\"","")
    if "https" not in coverurl:
        coverurl = ""
    #print("Result of getCoverUrl 1 -> "+coverurl)
    #Now add this result to DATABASE
    numberOfResults = 0
    #Check if there is a DB entry with already existing coverurl
    mycursor.execute("SELECT `name` FROM `steamgames` WHERE `name` = '"+name+"' AND `coverurl` IS NOT NULL AND `coverurl` != ''")
    for row in mycursor.fetchall():
        numberOfResults += 1
    if numberOfResults > 0:#There is a result for already existing coverurl for this game name
        #print("Found a result for already existing coverurl in DATABASE for this game name: "+name)
        command = "UPDATE `steamgames` SET `coverurl` = '"+str(coverurl)+"' WHERE `name` = '"+str(name)+"';"
        #print("Running this command below to ADD or UPDATE coverurl for this game:")
        #print(command)
        mycursor.execute(command)
        mycursor.execute("COMMIT;")
    else:    #There are ZERO RESULTS for already existing coverurl for this game name
        #print("Results for coverurl for this game name NOT FOUND")
        #Check if there is a DB entry with EMPTY coverurl
        mycursor.execute("SELECT `name` FROM `steamgames` WHERE `name` = '"+name+"'")        
        for row in mycursor.fetchall():
            numberOfResults += 1
        if numberOfResults > 0:
            #print("there is already a DB entry with empty coverurl for "+name+" - UPDATING DATABASE entry")
            command = "UPDATE `steamgames` SET `coverurl` = '"+str(coverurl)+"' WHERE `name` = '"+str(name)+"';"
            mycursor.execute(command)
            mycursor.execute("COMMIT;")
        else:
            if coverurl != "" and coverurl != " " and coverurl != "NULL" and coverurl != "null":
                #print("Adding cover entry for "+name+" CoverURL: "+coverurl)
                mycursor.execute("INSERT INTO `steamgames` VALUES (NULL, NULL, '"+name+"', '"+str(coverurl)+"')")
            else:
                #print("Can't add cover entry for "+name+" CoverURL: "+coverurl+" - adding null")
                mycursor.execute("INSERT INTO `steamgames` VALUES (NULL, NULL, '"+name+"', NULL)")
        mycursor.execute("COMMIT;")
        #print("[addCoverUrlToDB] [INFO] Cover URL retrieved: "+coverurl)
    return coverurl

#Get best match for game's name
def getIgdbName(nameToCheck):
    firstWordInName = nameToCheck.split(" ")[0].split(":")[0]
    preparedGrepName = nameToCheck.replace("\"","").replace(";","").replace("'","").replace(" ",".*")
    command = "curl -s 'https://api.igdb.com/v4/games/' -d 'fields name; where name ~ \""+firstWordInName+"\"*; limit 150;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[].name | xargs -L 1 > "+pathToScript+"/temp/bestname"
    #print("\t[addCoverUrlToDB.py] [INFO] IGDB Name command:")
    #print("\t"+command)
    runIt = subprocess.check_output(command, shell=True).decode( "utf-8" ).strip()
    list = open(pathToScript+"/temp/bestname")
    currentBestScore = 0
    currentBestName = ""
    for row in list:
        row = str(row)
        s1 = SequenceMatcher(None, row, nameToCheck)
        if s1.ratio() > currentBestScore:
            currentBestScore = s1.ratio()
            currentBestName = row
        #Debug:
        #print (">>>>>>>>>>>>>>>>>>>>>"+nameToCheck+"<<<<<<<<<<<<<<<<<<<<<")
        #print(row.replace("\n","")+" === "+str(s1.ratio())+" ---> BEST IS "+str(currentBestName).replace("\n","")+" = "+str(currentBestScore), end='\n')
    #print("\t[addCoverUrlToDB.py] [INFO] Chosen best name: "+str(currentBestName)+" RATIO:"+str(currentBestScore)[:4])
    if currentBestScore > 0.7:
        return str(currentBestName.replace("\n",""))
    else:
        return ""

##Script magic itself       

if len(sys.argv) > 1:
    
    scriptMode = sys.argv[1]
    #print("1"+scriptMode)
    if scriptMode == "name":
        #print("2")
        gameName = re.sub('[^A-Za-z0-9\.\- ]+', '', sys.argv[2])
        print(getCoverUrl(gameName))
    if scriptMode == "nameyear":
        gameName = re.sub('[^A-Za-z0-9\.\-\( ]+', '', sys.argv[2])
        gameNameSplit = gameName.split(" (")
        if len(gameNameSplit) > 1:
            gameYear = gameName.split(" (")[1]
            gameName = gameName.split(" (")[0]
            getCoverUrl(gameName,gameYear)
        else:
            gameName = re.sub('[^A-Za-z0-9\.\- ]+', '', sys.argv[2])
            getCoverUrl(gameName)
else:
    print("\t[addCoverUrlToDB.py] [ERROR] Missing arguments")
    exit
    