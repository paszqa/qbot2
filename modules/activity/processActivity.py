############################
#
#   process activity module for qqBot by Paszq
#   module which adds activity from CSV files to database
#
#############################
#Count execution time
from datetime import datetime, timedelta
startTime = datetime.now()
from datetime import date

#Imports
import os
import sys
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

#Vars
yesterday = (date.today()  - timedelta(1)).strftime("%Y%m%d") 
yesterdaySql = (date.today() - timedelta(1)).strftime("%Y-%m-%d")
if len(sys.argv) > 1:
    yesterdaySql = sys.argv[1]
    yesterday = sys.argv[1].replace("-","")
#Arguments

mycursor = mydb.cursor()
#Installation in case there is no table
mycursor.execute("CREATE TABLE IF NOT EXISTS `activity` (`id` INT(11) NOT NULL AUTO_INCREMENT, `userId` BIGINT(20) NULL DEFAULT NULL, `username` VARCHAR(100) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci', `date` DATE NULL DEFAULT NULL, `type` VARCHAR(15) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci', `activityName` VARCHAR(100) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci', `activityTime` INT(11) NULL DEFAULT NULL, PRIMARY KEY (`id`) USING BTREE) COLLATE='utf8mb4_general_ci' ENGINE=InnoDB AUTO_INCREMENT=531;")

#mycursor.execute("SELECT * FROM `votes` ORDER BY `totalTime` DESC LIMIT 25")

#os.rename(pathToScript+"/temp"+yesterday+".csv",pathToScript+"/proc"+yesterday+".csv")
f = open(pathToScript+"/temp/temp"+yesterday+".csv","r")
content = f.readlines()
for line in content:
    username = line.split(";")[1]
    userId = line.split(";")[2]
    gameName = line.split(";")[5].replace("'","")
    music = line.split(";")[6]
    stream = line.split(";")[7]
    if len(line.split(";")) > 8:
        avatar = line.split(";")[8]
    else:
        avatar = "null"
    if len(line.split(";")) > 9:
        twitch = line.split(";")[9].replace("\n","")
        if twitch == "":
            twitch = "null"
    else:
        twitch = "null"
        
    print("username: "+username+" // userId: "+userId+" // ",end='')
    #Add game activity to DB
    print("gameName: "+gameName+" // ", end='')
    if gameName != "NONE":
        mycursor.execute("SELECT `activityTime` FROM `activity` WHERE `activityName` = '"+gameName+"' AND `userId` = '"+userId+"' AND `date` = '"+yesterdaySql+"'");
        results = mycursor.fetchall()
        numberOfResults = len(results)
        print(gameName+" :::::: "+str(numberOfResults), end='');
        if numberOfResults == 0:
            mycursor.execute("INSERT INTO `activity` VALUES (NULL, '"+userId+"', '"+username+"', '"+yesterdaySql+"', 'game', '"+gameName+"', "+config["activity_schedule_cron_tick"]+")");
        else:
            mycursor.execute("UPDATE `activity` SET `activityTime` = activityTime + "+config["activity_schedule_cron_tick"]+" WHERE `type` = 'game' AND `activityName` = '"+gameName+"' AND `userId` = '"+userId+"' AND `date` = '"+yesterdaySql+"'");
    #Add music activity to DB
    print("music: "+music+" // ",end='')
    if music != "NONE":
        mycursor.execute("SELECT `activityTime` FROM `activity` WHERE `type` = 'music' AND `userId` = '"+userId+"' AND `date` = '"+yesterdaySql+"'");
        results = mycursor.fetchall()
        numberOfResults = len(results)
        if numberOfResults == 0:
            mycursor.execute("INSERT INTO `activity` VALUES (NULL, '"+userId+"', '"+username+"', '"+yesterdaySql+"', 'music', NULL, "+config["activity_schedule_cron_tick"]+")");
        else:
            mycursor.execute("UPDATE `activity` SET `activityTime` = activityTime + "+config["activity_schedule_cron_tick"]+" WHERE `type` = 'music' AND `userId` = '"+userId+"' AND `date` = '"+yesterdaySql+"'");
    #Add stream activity to DB
    print("stream: "+stream+" // ", end='')
    if stream != "NONE":
        mycursor.execute("SELECT `activityTime` FROM `activity` WHERE `type` = 'stream' AND `activityName` = '"+stream+"' AND `userId` = '"+userId+"' AND `date` = '"+yesterdaySql+"'");
        results = mycursor.fetchall()
        numberOfResults = len(results)
        if numberOfResults == 0:
            mycursor.execute("INSERT INTO `activity` VALUES (NULL, '"+userId+"', '"+username+"', '"+yesterdaySql+"', 'stream', '"+stream+"', "+config["activity_schedule_cron_tick"]+")");
        else:
            mycursor.execute("UPDATE `activity` SET `activityTime` = activityTime + "+config["activity_schedule_cron_tick"]+" WHERE `type` = 'stream' AND `activityName` = '"+stream+"' AND `userId` = '"+userId+"' AND `date` = '"+yesterdaySql+"'");
    #Add twitch activity do DB
    print("twitch: "+twitch+" // ", end='')
    if twitch != "null" and twitch != "NULL" and twitch != "":
        mycursor.execute("SELECT `activityTime` FROM `activity` WHERE `type` = 'stream' AND `activityName` = '"+twitch+"' AND `userId` = '"+userId+"' AND `date` = '"+yesterdaySql+"'");
        results = mycursor.fetchall()
        if username == "Vyqe":
            print("Y", end='')
            print(results, end='')
        numberOfResults = len(results)
        if numberOfResults == 0:
            mycursor.execute("INSERT INTO `activity` VALUES (NULL, '"+userId+"', '"+username+"', '"+yesterdaySql+"', 'stream', '"+twitch+"', "+config["activity_schedule_cron_tick"]+")");
            #if username == "Vyqe":
            #    print("X", end='')
            #    print(mycursor.fetchall(), end='')
        else:
            mycursor.execute("UPDATE `activity` SET `activityTime` = activityTime + "+config["activity_schedule_cron_tick"]+" WHERE `type` = 'stream' AND `activityName` = '"+twitch+"' AND `userId` = '"+userId+"' AND `date` = '"+yesterdaySql+"'");
            #mycursor.execute("SELECT `activityTime` FROM `activity` WHERE `type` = 'twitch' AND `activityName` = '"+twitch+"' AND `userId` = '"+userId+"' AND `date` = '"+yesterdaySql+"'");
            #print("Z", end='')
            #print(mycursor.fetchall(), end='')
    print("\n------")


mycursor.execute("COMMIT;")
f.close()
