######################
#
# Module which checks twitch activity for everyone in database and adds to temp file
#Count execution time
from datetime import datetime
from datetime import date
startTime = datetime.now()

#Imports
import time
import os
import sys
import mysql.connector
import subprocess
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


#activityString = sys.argv[1]
dateNow = str(int(time.time() * 1000) )
#print(dateNow)
today = date.today().strftime("%Y%m%d")
#discordName = activityString.split(";")[1]
#discordId = activityString.split(";")[2]
#isBot = activityString.split(";")[3]
#isOnline = activityString.split(";")[4]
mycursor = mydb.cursor()

#Run DB query to get user's twitch username
mycursor.execute("SELECT discord_user_id, twitch_username, discord_username FROM `userdata` WHERE twitch_username IS NOT NULL;")
# WHERE `discord_user_id` = '"+discordId+"' LIMIT 1")
results = mycursor.fetchall()


for row in results:
    discordId = str(row[0])
    twitchName = str(row[1])
    discordName = str(row[2])
   #Check stream status from Twitch API
    streamStatus=subprocess.check_output('curl -s -H \'Client-Id: '+config["twitch_api_client_id"]+'\' -H \'Authorization: Bearer '+config["twitch_api_secret"]+'\' -X GET \'https://api.twitch.tv/helix/streams?user_login='+twitchName+'\' | jq \'.[][].type\'', shell=True) 
    #Strip crap from stream status
    streamStatus = streamStatus.decode("utf-8")
    #Get game name from Twitch API
    gameName=subprocess.check_output('curl -s -H \'Client-Id: '+config["twitch_api_client_id"]+'\' -H \'Authorization: Bearer '+config["twitch_api_secret"]+'\' -X GET \'https://api.twitch.tv/helix/streams?user_login='+twitchName+'\' | jq \'.[][].game_name\'', shell=True) 
    #Strip crap from gameName
    gameName = gameName.decode("utf-8").replace('"','').replace("\n","")
    if "live" in streamStatus:
        #print("live - "+gameName)
        newActivityString = dateNow+";"+discordName+";"+discordId+";false;false;NONE;NONE;NONE;NONE;"+gameName+";"
        print(newActivityString)
        #add Activity to temp file if stream status is live:
        f = open(pathToScript+"/temp/temp"+today+".csv","a+")
        f.write(newActivityString+"\n")
        f.close()
    else:
        #print(row)
        print(discordName+" / "+twitchName+" is offline on Twitch.")
exit(0)
#Check twitch name  
#print(results)
exit(0)
#If twitch name is empty, then exit
if twitchName == "" or twitchName == " " or twitchName == "null":
    exit(0)
    

#Check stream status from Twitch API
streamStatus=subprocess.check_output('curl -s -H \'Client-Id: '+config["twitch_api_client_id"]+'\' -H \'Authorization: Bearer '+config["twitch_api_secret"]+'\' -X GET \'https://api.twitch.tv/helix/streams?user_login='+twitchName+'\' | jq \'.[][].type\'', shell=True) 
#Strip crap from stream status
streamStatus = streamStatus.decode("utf-8")

#Get game name from Twitch API
gameName=subprocess.check_output('curl -s -H \'Client-Id: '+config["twitch_api_client_id"]+'\' -H \'Authorization: Bearer '+config["twitch_api_secret"]+'\' -X GET \'https://api.twitch.tv/helix/streams?user_login='+twitchName+'\' | jq \'.[][].game_name\'', shell=True) 
#Strip crap from gameName
gameName = gameName.decode("utf-8").replace('"','').replace("\n","")
#If status is "live" or similar, then add current game to activity
if "live" in streamStatus:
    #print("live - "+gameName)
    newActivityString = dateNow+";"+discordName+";"+discordId+";"+isBot+";"+isOnline+";NULL;NULL;"+gameName+";NONE;"
    print(newActivityString)
    #add Activity to temp file if stream status is live:
    f = open(pathToScript+"/temp/temp"+today+".csv","a+")
    f.write(newActivityString+"\n")
    f.close()
else:
    print("off")
    exit(0)
    
