####################################
#
# 'userdata - calc total activity' module for qqBot by Paszq
#
# sums up total activity for each user for each game and saves it with cover images to output
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

def downloadCoverFromUrl(name, coverUrl):
    if "https:" in coverUrl:
        r = requests.get(coverUrl)  #Download cover from coverurl
        name = re.sub('[^A-Za-z0-9\-]+', '', name)
        with open(config["script_path"]+config["activity_path"]+"temp/"+name.replace(" ","")+".jpg", 'wb') as f:
            f.write(r.content)
        f.close()
        return coverUrl

#Get cover function
def getCoverFromName(name):
    #get url from db
    print("Getting cover for "+name)
    mycursor.execute("SELECT coverurl FROM `steamgames` WHERE `name`='"+name+"' AND `coverurl` IS NOT NULL AND `coverurl` != '' LIMIT 1;")
    coverresult = mycursor.fetchall()
    if len(coverresult) > 0:#If cover was found in DB
        print("Cover was found in DB.")
        coverUrl = str(coverresult[0][0]).replace("'b","").replace("\n'","").replace("\n","")
        #Downloading cover for game name
        command='python3 '+config["script_path"]+config["activity_path"]+'downloadCoverForName.py "'+str(name)+'"'
        #print("1. CMD:"+command)
        coverUrl = subprocess.check_output(command, shell=True)
        coverUrl = coverUrl.decode("utf-8")#.replace("'b","").replace("\n'","").replace("\n","")
        #print("COVeR:"+str(coverUrl))
        #downloadCoverFromUrl(name, coverUrl)
        return coverUrl
    else:#If cover was not found in DB
        print("Cover was NOT found in DB.")
        command = "python3 "+config["script_path"]+config["steam_sum_up_path"]+"getGameData.py addcover \""+name+"\""
        #print("2. CMD:    "+command)
        os.system(command)
        mydb.reconnect(attempts=1, delay=1)
        mycursor.execute("SELECT coverurl FROM `steamgames` WHERE `name`='"+name+"' LIMIT 1;")
        coverresult = mycursor.fetchall()
        if len(coverresult) > 0:
            coverUrl = str(coverresult[0][0]).replace("'b","").replace("\n'","").replace("\n","")
            command='python3 '+config["script_path"]+config["activity_path"]+'downloadCoverForName.py "'+str(name)+'"'
            #print("CMD:"+command)
            coverUrl = subprocess.check_output(command, shell=True)
            coverUrl = coverUrl.decode("utf-8")#.replace("'b","").replace("\n'","").replace("\n","")
            #print("COVERRR:"+str(coverUrl))
            #downloadCoverFromUrl(name, coverUrl)
            return coverUrl
        return ""
        


##########################################################
#Results - Top 5 games in last week with times
##########################################################
print("GAMES")
mycursor.execute("SELECT  activityName,SUM(`activityTime`) FROM `activity` WHERE `type`='game' AND `activityName` NOT LIKE '%Visual Studio%' AND `date` > (date_sub(now(),INTERVAL 1 WEEK)) GROUP BY `activityName` ORDER BY SUM(`activityTime`) DESC LIMIT 10;")
results = mycursor.fetchall()
f = open(pathToScript+"/output/recent-games.csv","w+")
for line in results:
    gameName = str(line[0])
    time = str(line[1])
    print("Game name from CSV: "+gameName)
    cover = str(getCoverFromName(gameName))
    csvline = gameName+";"+time+";"+cover
    csvline = csvline.replace("\n","")
    if csvline != "":
        print(csvline)
        f.write(csvline+"\n")
f.close()

##########################################################
#Results - Top 5 players in last week with avatars and ranked game titles
##########################################################
print(" ")    
print("PLAYERS")
mycursor.execute("SELECT  userId, username, SUM(`activityTime`) FROM `activity` WHERE `type`='game' AND `activityName` NOT LIKE '%Visual Studio%' AND `date` > (date_sub(now(),INTERVAL 1 WEEK)) GROUP BY `userId` ORDER BY SUM(`activityTime`) DESC LIMIT 5;")
results = mycursor.fetchall()
f = open(pathToScript+"/output/recent-players.csv","w+")
for line in results:
    userId = str(line[0])
    #  get avatar id:
    mycursor.execute("SELECT `discord_avatar` FROM `userdata` WHERE `discord_user_id`='"+str(line[0])+"' LIMIT 1;")
    avatarid = mycursor.fetchall()
    # print user info
    if avatarid[0][0]:
        avatarid = avatarid[0][0]
        if avatarid != "null":
            csvline = str(line[1])+";"+str(line[2])+";https://cdn.discordapp.com/avatars/"+str(line[0])+"/"+avatarid+".png?size=128"+";"+userId
        else:
            csvline = str(line[1])+";"+str(line[2])+";null;"+userId
    else:
        csvline = str(line[1])+";"+str(line[2])+";https://cdn.discordapp.com/avatars/"+str(line[0])+"/NoDiscordAvatar.png?size=128"+";"+userId
    print(""+csvline)
    # get ranked game titles - top3 for this player
    mycursor.execute("SELECT  userId, username, activityName, SUM(`activityTime`) FROM `activity` WHERE  `activityName`<>'online' AND `type`='game' AND `userId`='"+str(line[0])+"' AND `date` > (date_sub(now(),INTERVAL 1 WEEK)) GROUP BY `activityName` ORDER BY SUM(`activityTime`) DESC LIMIT 3;;")
    topGames = mycursor.fetchall()
    g = open(pathToScript+"/output/recent-games-"+str(line[0])+".csv","w+")
    for game in topGames:
        gameName = str(game[2])
        g.write(gameName.replace("\n","")+";"+getCoverFromName(gameName).replace("\n","")+"\n")
        if gameName != "":
            print("\t"+gameName+";"+getCoverFromName(gameName)+"")
    g.close()
    f.write(csvline+"\n")
f.close()

##########################################################    
#Results - Top 5 streamers in last week
##########################################################
print(" ")    
print("STREAMERS")
mycursor.execute("SELECT  userId, username, SUM(`activityTime`) FROM `activity` WHERE `type`='stream' AND `date` > (date_sub(now(),INTERVAL 1 WEEK)) GROUP BY `userId` ORDER BY SUM(`activityTime`) DESC LIMIT 5;;")
results = mycursor.fetchall()
f = open(pathToScript+"/output/recent-streamers.csv","w+")
for line in results:
    #get twitch avatar:
    mycursor.execute("SELECT twitch_image FROM `userdata` WHERE `discord_user_id`='"+str(line[0])+"' LIMIT 1;")
    avatarurl = mycursor.fetchall()
    avatarurl = str(avatarurl[0][0])
    csvline = str(line[1])+";"+str(line[2])+";"+avatarurl
    print(csvline)
    f.write(csvline+"\n")
f.close()

##########################################################
#Results - Top 5 steam players in last week - USES Steam Tracker data and USES Steam Sum Up script
##########################################################
print("\nSTEAM PLAYERS")
# - get all players that have steam id added
mycursor.execute("SELECT steam_user_id FROM `userdata` WHERE `steam_user_id` IS NOT NULL;")
steamplayers = mycursor.fetchall()
f = open(pathToScript+"/output/recent-steam.csv","w+")
for steamdata in steamplayers:
    print("")
    steamid = str(steamdata[0])
    #Get user's discord avatar url
    mycursor.execute("SELECT discord_user_id, discord_avatar FROM `userdata` WHERE `steam_user_id`='"+steamid+"';")
    queryresults = mycursor.fetchall()
    discord_id = str(queryresults[0][0])
    avatar_id = str(queryresults[0][1])
    avatarurl = "https://cdn.discordapp.com/avatars/"+discord_id+"/"+avatar_id+".png?size=128"
    #print(avatarurl)
    mycursor.execute("SELECT appId, SUM(`playedToday`) FROM `trackedtimes`.`"+steamid+"` WHERE `date` > (date_sub(now(),INTERVAL 1 WEEK)) GROUP BY `appId` ORDER BY SUM(`playedToday`) DESC LIMIT 5;")
    results = mycursor.fetchall()
    mycursor.execute("SELECT appId, SUM(`playedToday`) FROM `trackedtimes`.`"+steamid+"` WHERE `date` > (date_sub(now(),INTERVAL 1 WEEK)) ORDER BY SUM(`playedToday`) DESC LIMIT 1;")
    sum = str(mycursor.fetchall()[0][1])
    mycursor.execute("SELECT steam_username FROM `userdata` WHERE `steam_user_id` = '"+steamid+"' LIMIT 1;")
    steamname = str(mycursor.fetchall()[0][0])
    if sum != 'None':
        f.write(steamid+";"+steamname+";"+str(sum)+";"+avatarurl+"\n")
        g = open(pathToScript+"/output/recent-steam-"+steamid+".csv","w+")
        for line in results:
            print("STEAM HMMMMM")
            print(line)
            command = "python3 "+config["script_path"]+config["steam_sum_up_path"]+"getGameData.py getname "+str(line[0])
            print(command)
            os.system(command)
            mydb.reconnect(attempts=1, delay=1)
            mycursor.execute("SELECT name, coverurl FROM `steamgames` WHERE `appId`='"+str(line[0])+"' LIMIT 1;")
            gameInfo = mycursor.fetchall()
            if len(gameInfo) > 0:
                gameName = str(gameInfo[0][0])
                coverUrl = str(gameInfo[0][1])
            else:
                gameInfo
            g.write(str(line[0])+";"+gameName.replace(";","")+";"+str(line[1])+";"+coverUrl+"\n")
            print(steamname+" ===> "+gameName+" - Time "+str(line[1])+" [Total time = "+sum+"]")
            getCoverFromName(gameName)
        g.close()
f.close()

##########################################################
# Music minutes
##########################################################
print("\nMUSIC ACTIVITY")
musicquery="SELECT  SUM(`activityTime`) FROM `activity` WHERE `type`='music' AND `date` > (date_sub(now(),INTERVAL 1 WEEK)) GROUP BY `activityName` ORDER BY SUM(`activityTime`) DESC LIMIT 1;"
print(musicquery)
mycursor.execute(musicquery)
queryresults = mycursor.fetchall()[0][0]
mycursor.execute("SELECT  SUM(`activityTime`) FROM `activity` WHERE `type`='music' AND `date` > (date_sub(now(),INTERVAL 1 WEEK)) GROUP BY `username` ORDER BY SUM(`activityTime`);")
results = mycursor.fetchall()
count = 0
for r in results:
    count += 1
f = open(pathToScript+"/output/recent-music.csv","w+")
f.write(str(queryresults)+";"+str(count))
f.close()
