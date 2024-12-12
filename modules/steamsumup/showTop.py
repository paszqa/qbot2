import mysql.connector
import os
import subprocess
import time
import requests
import cloudscraper
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
mydb = mysql.connector.connect(
          host=config["dbhost"],
            user=config["dbuser"],
              password=config["dbpass"],
                database=config["dbname"],
                )

mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM `totalTimes` ORDER BY `totalTime` DESC LIMIT 25")
#print("Final total time")
f = open(pathToScript+'/output/most-played-total.csv','w+')
print("No ; Game ; Hours ; Slavs")
f.write("No;Game;Hours;Slavs\n")
no=1
for finalRow in mycursor.fetchall():
    print("\t[showTop.py] [INFO] Working on: "+str(finalRow[1]))
    gameName=subprocess.check_output('python3 '+config["script_path"]+config["steam_sum_up_path"]+'/getGameData.py getname '+str(finalRow[1]), shell=True)
    print("\t[showTop.py] [INFO] GameName after getting: "+str(gameName))
    gameName = str(gameName).replace("\\n\'","")
    gameName = gameName[2:].replace("\"","")
    gameName = gameName.replace("\\'","'") #fix apostrophe
    gameName = gameName.replace("\\xe2\\x84\\xa2","®")
    gameName = gameName.replace("\\xe2\\x80\\x99","'")
    gameName = gameName.replace("\\xc2","").replace("\\xae","").replace("\\xe2","")
    gameName = gameName.replace("\\n\'","")
    gameName = gameName.replace("\\n","")
    appId=str(finalRow[1])
    hours=str(round(finalRow[3]/60,2))
    players=str(finalRow[4])
    print(str(no)+";"+str(gameName)+";"+hours+";"+players)
    f.write(str(no)+";"+str(gameName)+";"+hours+";"+players+"\n")
    no+=1
