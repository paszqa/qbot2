############################################
#
# gamename - qqbot module by Paszq
#
# Outputs game name after being supplied game's Steam ID
#
############################################
############################################
# 1. check if ID is supplied
# 2. check if it exists in the database already
# 3. query Steam for the name
#    if it fails, query SteamCharts
# 4. update db
############################################

import mysql.connector
import subprocess
import sys
import re
import os
from os.path import exists
from datetime import datetime
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

#Settings
pathToScript = os.path.dirname(os.path.realpath(__file__))
mydb = mysql.connector.connect(
          host=config["dbhost"],
            user=config["dbuser"],
              password=config["dbpass"],
                database=config["dbname"],
                )

mycursor = mydb.cursor()

#Setup logfile
f = open(pathToScript+'/outputNameFromId.log','a+')

#Get arguments 
if len(sys.argv) > 1:
    id = sys.argv[1]
else:
    print("[OutputNameFromId] [ERROR] No argument supplied.")
    exit(1)

#####################################
# Functions
#####################################
def checkDatabase(id):
    numberOfResults = 0
    sqlQuery = "SELECT `name` FROM `steamgames` WHERE `appId` = '"+id+"'"
    mycursor.execute(sqlQuery)
    for row in mycursor.fetchall():
        if str(row[0]) != "" and str(row[0]) != "NULL" and str(row[0]) != None: #Check if NAME for the id is not empty, and count it only if it's not empty
            numberOfResults += 1
    if numberOfResults == 0: #If fails, then return false and proceed
        return False
    else:                   #If found, then get the name, print it and exit
        gameName = str(row[0])
        print(gameName)
        log(str(datetime.now())+" [INFO] Database - for id:"+str(id)+" found name: "+gameName+". Exiting...\n")
        exit(0)

def checkSteam(id, attempts=10):    #Try Steam Store
    for x in range(1,attempts):
        #print("Steam Attempts:"+str(x)+"/"+str(attempts)+" for id:"+str(id))
        log(str(datetime.now())+" [INFO] Steam - Attempts:"+str(x)+"/"+str(attempts)+" for id:"+str(id)+"\n")
        gameName=subprocess.check_output('curl -s https://store.steampowered.com/api/appdetails/?appids='+str(id)+' | jq \'.[] | .data | .name\'', shell=True)
        gameName = str(gameName.decode()).replace("\"","")
        gameName = gameName.replace("\n","")
        if gameName != "":
            log(str(datetime.now())+" [INFO] Steam - result for id:"+str(id)+" found name: "+gameName+"\n")
            return gameName
        time.sleep(4 * x)
        x=x+1
    log(str(datetime.now())+" [INFO] Steam - result for id:"+str(id)+" found name: "+gameName+"\n")
    return ""

def checkSteamCharts(id, attempts=10):  #Try Steam Charts
    for x in range(1,attempts):
        #print("SteamCharts Attempts:"+str(x)+"/"+str(attempts)+" for id:"+str(id))
        log(str(datetime.now())+" [INFO] SteamCharts - Attempts:"+str(x)+"/"+str(attempts)+" for id:"+str(id)+"\n")
        url = "'https://steamcharts.com/app/"+str(id)+"'"
        gameName=subprocess.check_output('curl -s '+url+' | grep -i "<title>"', shell=True)
        gameName = str(gameName.decode()).replace("\"","")
        gameName = gameName.replace("\n","")
        if gameName != "null":
            log(str(datetime.now())+" [INFO] SteamCharts - result for id:"+str(id)+" found name: "+gameName+"\n")
            return gameName
        time.sleep(4 * x)
        x=x+1
    log(str(datetime.now())+" [INFO] SteamCharts - result for id:"+str(id)+" found name: "+gameName+"\n")
    return ""

def cleanUpName(gameName):        #Clean up the name
    originalGameName = str(gameName).replace("\n","")
    gameName=str(gameName).replace(" - Steam Charts","")
    gameName=gameName.replace("Steam Charts - ","")
    gameName=gameName.replace("\\n","")
    gameName=gameName.replace("<title>","")
    gameName=gameName.replace("</title>","")
    gameName=gameName.replace("\t","")
    gameName = gameName.replace("\"","")
    gameName = gameName.replace("\\'","'") #fix apostrophe
    gameName = gameName.replace("\\xe2\\x84\\xa2","®")
    gameName = gameName.replace("\\xe2\\x80\\x99","'")
    gameName = gameName.replace("\\xc2","").replace("\\xae","").replace("\\xe2","")
    gameName = gameName.replace("\\n\'","")
    gameName = gameName.replace("\n","")
    log(str(datetime.now())+" [INFO] Cleaned up name from:"+originalGameName+" ==> "+gameName+"\n")
    return gameName

def log(text):
    f.write(str(text))
    

def updateDatabase(id, gameName):
    #Check if there is a record to update
    sqlQuery = "SELECT `name` FROM `steamgames` WHERE `appId` = '"+id+"'"
    mycursor.execute(sqlQuery)
    numberOfResults = 0
    for row in mycursor.fetchall():
            numberOfResults += 1
    if numberOfResults > 0 and gameName != "null":
        sqlQuery="UPDATE `steamgames` SET name = '"+gameName+"' WHERE `appId` = '"+str(id)+"')"
        log(str(datetime.now())+" [INFO] Running SQL query: "+sqlQuery+"\n")
        #print(sqlQuery)
    else:
        sqlQuery="INSERT INTO `steamgames` VALUES (NULL, "+id+", '"+str(gameName)+"', NULL)"
        log(str(datetime.now())+" [INFO] Running SQL query: "+sqlQuery+"\n")
        #mycursor.execute(sqlQuery)
        #mycursor.execute("COMMIT;")

def nameCheck(gameName):
    if gameName == "":
        return False
    if gameName == "null":
        return False
    if "Tracking What's Played" in gameName:
        return False
    return True
        

#####################################
# Magic
#####################################

log(str(datetime.now())+" [INFO] Script started for id: "+str(id)+"\n")
if checkDatabase(id) == False:
    gameName = checkSteam(id,4)
    if nameCheck(gameName):
        gameName = cleanUpName(gameName)
        print(str(gameName))
        log(str(datetime.now())+" [INFO] Game name received from Steam: "+str(gameName)+"\n")
    else:
        gameName = checkSteamCharts(id,4)
        if nameCheck(gameName):
            gameName = cleanUpName(gameName)
            print(gameName)
            log(str(datetime.now())+" [INFO] Game name received from Steam Charts: "+gameName+"\n")

if gameName:
    if nameCheck(gameName):
        updateDatabase(id, gameName)
    
f.close()