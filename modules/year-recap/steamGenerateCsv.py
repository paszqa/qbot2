####################################
#
# year-recap' module for qqBot by Paszq
#
# Steam CSV Generator
# sums up DB contents from activity
#
####################################

import mysql.connector
import os
import calendar
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

#Settings
pathToScript = os.path.dirname(os.path.realpath(__file__))
year = 2023
#Check if script isn't running already
def FileCheck(fn):
    try:
      open(fn, "r")
      return 1
    except IOError:
      return 0
fileresult = FileCheck(config["script_path"]+config["year_recap_path"]+"/temp/generateCsv.tmp")
if fileresult == 1:
    print("Script already running")
    quit()
else:
    print("No script running")
    g = open(config["script_path"]+config["year_recap_path"]+"/temp/generateCsv.tmp", "w+")
    g.write("busy")
    g.close()

#DB Connection
mydb = mysql.connector.connect(
          host=config["dbhost"],
            user=config["dbuser"],
              password=config["dbpass"],
                database=config["dbname"],
                )

mycursor = mydb.cursor()

#Add SteamIDs from ProfileList to array
#steamaccounts = []
#with open('/home/pi/steamsumup/profileList') as my_file:
        #for line in my_file:
                    #steamaccounts.append(line)
                    
steamaccounts = [ "76561197994977404", "76561198000030995", "76561198004729616", "76561198009810227" ] 

for steamid in steamaccounts:
    steamid = steamid.replace("\n","")
    if steamid != "":
        print("Current Steam ID: "+str(steamid)+"...")
        mycursor.execute("SELECT YEAR(DATE), MONTH(DATE), appId, SUM(playedToday) FROM `trackedtimes`.`"+steamid+"` WHERE YEAR(DATE) = "+str(year)+" GROUP BY MONTH(DATE), YEAR(DATE), appId")
        currentResult = mycursor.fetchall()
        numberOfResults = len(currentResult)
        print("Result count: "+str(numberOfResults))
        f = open(pathToScript+'/output/'+str(year)+'/'+steamid+'.csv','w+')
        print("No ; Year ; Month ; GameId ; Hours\n")
        f.write("No ; Year ; Month ; GameId ; Hours\n")
        i = 0
        for row in currentResult:
            i=i+1
            currentYear = row[0]
            currentMonth = row[1]
            currentGameId = row[2]
            currentMinutes = row[3]
            currentHours = row[3] / 60
            currentHours = float("{:.2f}".format(currentHours))
            print("Y: "+str(currentYear)+" M: "+str(currentMonth)+" ID: "+str(currentGameId)+" Tm: "+str(currentMinutes)+ " Th: "+str(currentHours))
            f.write(str(i)+";"+str(currentYear)+";"+str(currentMonth)+";"+str(currentGameId)+";"+str(currentHours)+"\n")

os.remove(config["script_path"]+config["year_recap_path"]+"/temp/generateCsv.tmp")
