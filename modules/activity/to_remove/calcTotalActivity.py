####################################
#
# 'userdata - calc total activity' module for qqBot by Paszq
#
# sums up total activity for each user for each game
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

#Installation in case there is no table
mycursor.execute("CREATE TABLE IF NOT EXISTS `activityTotal` (`id` INT(11) NOT NULL AUTO_INCREMENT, `userId` BIGINT(20) NULL DEFAULT NULL, `username` VARCHAR(100) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci', `type` VARCHAR(15) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci', `activityName` VARCHAR(100) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci', `activityTime` INT(11) NULL DEFAULT NULL, PRIMARY KEY (`id`) USING BTREE) COLLATE='utf8mb4_general_ci' ENGINE=InnoDB AUTO_INCREMENT=1;")


mycursor.execute("SELECT DISTINCT `userId`, `activityName` FROM `activity` WHERE `type`='game';")
activityTable = mycursor.fetchall()

for row in activityTable:
    print(str(row[0])+" --- "+str(row[1]))