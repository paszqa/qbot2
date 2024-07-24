####################################
#
# 'userdata - add' module for qqBot by Paszq
#
# adds user information to database
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
import urllib.request   #For URL querying purposes - ex. to get Steam ID
import requests         #For URL querying purposes - ex. to get Steam ID
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
mycursor.execute("CREATE TABLE IF NOT EXISTS `userdata` (`id` INT(11) NOT NULL AUTO_INCREMENT, `discord_user_id` BIGINT(20) NOT NULL DEFAULT '0', `discord_username` VARCHAR(50) NULL DEFAULT '0' COLLATE 'utf8mb4_general_ci', `steam_user_id` BIGINT(20) NULL DEFAULT '0', `steam_username` VARCHAR(50) NULL DEFAULT '0' COLLATE 'utf8mb4_general_ci', `twitch_user_id` BIGINT(20) NULL DEFAULT '0',`twitch_username` VARCHAR(50) NULL DEFAULT '0' COLLATE 'utf8mb4_general_ci', `twitch_image` VARCHAR(150) NULL DEFAULT '0' COLLATE 'utf8mb4_general_ci', `join_date` DATE NULL DEFAULT NULL, `discord_avatar` BIGINT(20) NULL DEFAULT NULL, PRIMARY KEY (`id`) USING BTREE) COLLATE='utf8mb4_general_ci' ENGINE=InnoDB AUTO_INCREMENT=5;")

#Function to update an attribute. Discord ID is required.
def set_attribute(discord_id, attribute_name, input_string):
    print("[addUserData] discord_id "+discord_id+":"+attribute_name+" [set to] "+input_string)
    mycursor.execute("SELECT * FROM `userdata` WHERE `discord_user_id` = '"+discord_id+"'")
    results = mycursor.fetchall()
    numberOfResults = len(results)
    if numberOfResults == 0:
        mycursor.execute("INSERT INTO `userdata` VALUES (NULL, '"+discord_user_id+"', NULL, NULL, NULL, NULL, NULL, NULL, CURRENT_DATE, NULL);")
    else:
        mycursor.execute("UPDATE `userdata` SET `"+attribute_name+"` = '"+input_string+"' WHERE `discord_user_id` = '"+discord_id+"'")

#Function to find SteamID64 and Steam name from a Steam profile link
def get_steam(steamlink):
    linkarray=steamlink.replace("https://","").replace("http://","").split("/")
    print(linkarray)
    if "steamcommunity.com" in linkarray[0]:
        if linkarray[1] == "id":
            print("[addUserData] [INFO] GetSteam recognized a custom Steam profile.")
            url = "https://www.steamidfinder.com/lookup/"+linkarray[2] #URL for this custom profile
            content = str(requests.get(url).content).replace("\\n","\n").replace("\\t","\t").split("\n")#Fix newlines/tabs and divide into array with newlines as separator
            for line in content:#Check all lines
                if "steamID64 (Dec)" in line:#If this is found in string, it's the id line
                    id = line.split("<code>")[1].split("</code>")[0]#Extract the id from html tags
                if "<br>name <code>" in line:#If this is found in string, it's the name line
                    name = line.split("<code>")[1].split("</code>")[0]#Extract the name from html tags
            return [id, name]
        elif linkarray[1] == "profiles":
            print("[addUserData] [INFO] GetSteamID recognized a standard Steam profile.")
            id = linkarray[2]
            url = "https://www.steamidfinder.com/lookup/"+linkarray[2] #URL for this custom profile
            content = str(requests.get(url).content).replace("\\n","\n").replace("\\t","\t").split("\n")#Fix newlines/tabs and divide into array with newlines as separator
            for line in content:#Check all lines
                if "<br>name <code>" in line:#If this is found in string, it's the name line
                    name = line.split("<code>")[1].split("</code>")[0]#Extract the name from html tags
            return [id, name]
        else:
            print("[addUserData] [ERROR] GetSteamID couldn't recognize the link.")
            return null

#Function to find Twitch ID and Twitch name from Twitch URL
def get_twitch(twitchlink):
    linkarray=twitchlink.replace("https://","").replace("http://","").split("/")
    print(linkarray)
    if "twitch.tv" in linkarray[0]:
        print("[addUserData] [INFO] GetTwitch recognized a twitch link.")
        #Query the API
        url = "https://api.twitch.tv/helix/users?login="+linkarray[1]
        headers = { 'Client-Id' : config["twitch_api_client_id"], 'Authorization' : 'Bearer '+config["twitch_api_secret"] }
        response = requests.get(url, headers=headers)
        content = response.json()
        name = content["data"][0]['display_name']
        id = content["data"][0]['id']
        profile_image = content["data"][0]['profile_image_url']
        return [id, name, profile_image]
        #content
    return null

#Get arguments, main function
try:
    opts, args = getopt.getopt(sys.argv[1:], "d:u:i:s:t:n:L:T:a:")
except getopt.GetoptError:
    print('Wrong argument. Accepted arguments:\n-d mandatory_discord_id -u discord_name -i steam_id -s steam_name -L steam_profile_url -t twitch_id -n twitch_name -T twitch_url -p twitch_image -a discord_avatar_id')
    sys.exit(2)
for opt,arg in opts:
    if opt == '-d':
        discord_user_id = arg
        set_attribute(discord_user_id, "discord_user_id", arg)
    elif opt == '-u':
        set_attribute(discord_user_id, "discord_username", arg)
    elif opt == '-i':
        set_attribute(discord_user_id, "steam_user_id", arg)
    elif opt == '-s':
        set_attribute(discord_user_id, "steam_username", arg)
    elif opt == '-L':
        steam_array = get_steam(arg)
        if len(steam_array) > 1:
            steam_id = steam_array[0]
            steam_name = steam_array[1]
            set_attribute(discord_user_id, "steam_user_id", steam_id)
            set_attribute(discord_user_id, "steam_username", steam_name)
    elif opt == '-t':
        set_attribute(discord_user_id, "twitch_user_id", arg)
    elif opt == '-n':
        set_attribute(discord_user_id, "twitch_username", arg)
    elif opt == "-T":
        twitch_array = get_twitch(arg)
        if len(twitch_array) > 2:
            twitch_id = twitch_array[0]
            twitch_name = twitch_array[1]
            twitch_image = twitch_array[2]
            set_attribute(discord_user_id, "twitch_user_id", twitch_id)
            set_attribute(discord_user_id, "twitch_username", twitch_name)
            set_attribute(discord_user_id, "twitch_image", twitch_image)
    elif opt == "-a":
        if arg != "null":
            set_attribute(discord_user_id, "discord_avatar", arg)

#Commit changes
mycursor.execute("COMMIT;")
