####################################
#
# 'steam - sumUp' module for qqBot by Paszq
#
# sums up DB contents from 'steam - tracker' module and creates a table with summed up times per appId
#
####################################


import mysql.connector
import os
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
#Check if script isn't running already
def FileCheck(fn):
    try:
      open(fn, "r")
      return 1
    except IOError:
      return 0
fileresult = FileCheck("/tmp/sumUp.tmp")
if fileresult == 1:
    print("Script already running")
    quit()
else:
    print("No script running")
    g = open(config["script_path"]+config["steam_sum_up_path"]+"/temp/sumUp.tmp", "w+")
    g.write("busy")
    g.close()


mydb = mysql.connector.connect(
          host=config["dbhost"],
            user=config["dbuser"],
              password=config["dbpass"],
                database=config["dbname"],
                )

mycursor = mydb.cursor()
#Clear DB
mycursor.execute("CREATE TABLE IF NOT EXISTS `totalTimes` (`id` INT(11) NOT NULL AUTO_INCREMENT,`appId` INT(11) NULL DEFAULT NULL,`gameName` VARCHAR(100) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',	`totalTime` INT(11) NULL DEFAULT NULL,`players` INT(11) NULL DEFAULT NULL,PRIMARY KEY (`id`) USING BTREE) COLLATE='utf8mb4_general_ci' ENGINE=InnoDB AUTO_INCREMENT=1268;"); #Installation if no table found
mycursor.execute("DELETE FROM `totalTimes`")
mycursor.execute("ALTER TABLE `totalTimes` AUTO_INCREMENT = 1;")
#Add SteamIDs from ProfileList to array
steamaccounts = []
with open('/home/pi/steamsumup/profileList') as my_file:
        for line in my_file:
                    steamaccounts.append(line)
#steamaccounts = [ "76561197994977404", "76561198000030995", "76561198004729616", "76561198009810227" ] 
for steamid in steamaccounts:
    steamid = steamid.replace("\n","")
    if steamid != "":
        print("Current Steam ID: "+str(steamid)+"...")
        mycursor.execute("SELECT * FROM (SELECT  * FROM (SELECT `appId`, `playedTotal`,`date` FROM `trackedtimes`.`"+steamid+"` ORDER BY `date` DESC LIMIT 1000) AS t GROUP BY `appId`) AS t2 ORDER BY `playedTotal` DESC")
        currentResult = mycursor.fetchall()
        #print(".....Fetched results with current hours")
        for row in currentResult:
            #print(".....Current row - appId:"+str(row[0])+" - currentTime:"+str(row[1]))
            mycursor.execute("SELECT * FROM `totalTimes` WHERE `appId` = "+str(row[0])+"")
            results = mycursor.fetchall()
            numberOfResults = len(results)
            #print("......Found "+str(numberOfResults)+" existing results for appId "+str(row[0]))
            if numberOfResults == 0:
                #gameName=os.system("curl -s https://store.steampowered.com/api/appdetails/?appids="+str(row[0])+" | jq '.[] | .data | .name'");
                #print(".........Game Name: "+str(gameName))
                #gameName = str(gameName).replace("\"","")
                mycursor.execute("INSERT INTO `totalTimes` VALUES (NULL, "+str(row[0])+", NULL, "+str(row[1])+", 1)")
                #print("..........Added new entry")
            else:
                #print("Results")
                #print(results)
                #print("Row")
                #print(row)
                #print("New Total Time = "+str(row[1]))
                #print("... + "+str(results[0][3]))
                newTotalTime = row[1] + results[0][3]
                newPlayerCount = results[0][4] + 1
#                print(str(results[0][0])+" "+str(results[0][1])+" time: "+str(row[1])+" + "+str(results[0][2])+" = "+ str(newTotalTime))
                mycursor.execute("UPDATE `totalTimes` SET `totalTime` = "+str(newTotalTime) +", `players` = "+str(newPlayerCount)+" WHERE `appId` = "+str(row[0]))
                #print("..........Updated entry for appId "+str(row[0])+": "+str(row[1])+" + "+str(results[0][3])+" = "+str(newTotalTime))

mycursor.execute("COMMIT;")
mycursor.execute("SELECT * FROM `totalTimes`")
print("Final total time")
print("ID\tappId\ttotalTime\tplayers")
for finalRow in mycursor.fetchall():
    print(str(finalRow[0])+"\t"+str(finalRow[1])+"\t"+str(finalRow[3])+"\t"+str(finalRow[4]))

os.remove(config["script_path"]+config["steam_sum_up_path"]+"/temp/sumUp.tmp")
#g = open("/tmp/sumUp.tmp", "w")
#g.write("")
#g.close()
