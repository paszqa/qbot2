####################################
#
# year-recap' module for qqBot by Paszq
#
# General CSV Generator
# sums up DB contents from activity
#
####################################

import mysql.connector
import os
import calendar
from os.path import exists
import re
import json #JSON read/write capability
import subprocess
import requests#For getting covers from IGDB

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
tmpFileName = 'generalGenerateCsv.tmp'

#Check if script isn't running already
def FileCheck(fn):
    try:
      open(fn, "r")
      return 1
    except IOError:
      return 0
fileresult = FileCheck(config["script_path"]+config["year_recap_path"]+"/temp/"+tmpFileName)
if fileresult == 1:
    print("Script already running")
    quit()
else:
    print("No script running")
    g = open(config["script_path"]+config["year_recap_path"]+"/temp/"+tmpFileName, "w+")
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
#######################################################
################################### FUNCTIONSSSSSSSSSSSSS IMPORTED FROM GETACTIVITY TO CSV SCRIPT IN ACTIVITY
def downloadCoverFromUrl(name, coverUrl):
    print("[Debug DCFU] Downloading cover for: "+name+" ...from URL: "+coverUrl)
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
    print("Getting cover for: "+name)
    nameWithoutApostrophes = name.replace("'"," ").replace("  "," ").replace("  "," ")
    nameWithoutSpecialSymbolsExceptApostrophes = re.sub('[^A-Za-z0-9 \'\-]+', '', name)
    print("nameWithoutSpecialSymbolsExceptApostrophes:" + nameWithoutSpecialSymbolsExceptApostrophes)
    nameWithoutSpecialSymbols = re.sub('[^A-Za-z0-9 \-]+', '', name)
    print("nameWithoutSpecialSymbols:"+nameWithoutSpecialSymbols)
    fixedName = re.sub('[^A-Za-z0-9 \-]+', '', name)
    mysqlCommand = "SELECT coverurl FROM `steamgames` WHERE `name`='"+nameWithoutApostrophes+"' AND `coverurl` IS NOT NULL AND `coverurl` != '' LIMIT 1;"
    print("QUERY: "+mysqlCommand)
    mycursor.execute(mysqlCommand)
    coverresult = mycursor.fetchall()
    coverIsMissing = 0;
    if len(coverresult) > 0:#If cover was found in DB
        coverUrl = str(coverresult[0][0]).replace("'b","").replace("\n'","").replace("\n","")
        if coverresult[0][0] == "" or coverresult[0][0] == " ": # If cover in db is empty
            coverIsMissing = 1
        else:
            #Downloading cover for game name
            command='python3 '+config["script_path"]+config["activity_path"]+'downloadCoverForName.py "'+str(nameWithoutSpecialSymbolsExceptApostrophes)+'"'
            print("1. CMD:"+command)
            coverUrl = subprocess.check_output(command, shell=True)
            coverUrl = coverUrl.decode("utf-8")#.replace("'b","").replace("\n'","").replace("\n","")
            print("COVeR:"+str(coverUrl))
            #downloadCoverFromUrl(name, coverUrl)
            return coverUrl
    else:#should download
        coverIsMissing = 1
    
    if coverIsMissing == 1:#If cover was not found in DB
        print("Cover is missing = 1")
        command = "python3 "+config["script_path"]+config["steam_sum_up_path"]+"getGameData.py addcover \""+nameWithoutApostrophes+"\""
        print("[generalGenerateCsv] [getCoverFromName] command to run getGameData:  "+command)
        os.system(command)
        mydb.reconnect(attempts=1, delay=1)
        mycursor.execute("SELECT coverurl FROM `steamgames` WHERE `name`='"+nameWithoutApostrophes+"' LIMIT 1;")
        coverresult = mycursor.fetchall()
        if len(coverresult) > 0:
            coverUrl = str(coverresult[0][0]).replace("'b","").replace("\n'","").replace("\n","")
            command='python3 '+config["script_path"]+config["activity_path"]+'downloadCoverForName.py "'+str(nameWithoutApostrophes)+'"'
            #print("CMD:"+command)
            coverUrl = subprocess.check_output(command, shell=True)
            coverUrl = coverUrl.decode("utf-8")#.replace("'b","").replace("\n'","").replace("\n","")
            #print("COVERRR:"+str(coverUrl))
            #downloadCoverFromUrl(name, coverUrl)
            return coverUrl
        return ""
        
#Return coverurl
def getCoverUrl(name):
    #Check for game's cover from IGDB
    print("[DEBUG] Running getCoverUrl function for name: "+name)
    nameWithoutSpecialSymbols = re.sub('[^A-Za-z0-9 \-]+', '', name)
    #previousNameMightDelete = name.replace("\"","").replace(";","").replace("'","") ### TO BE DELETED?
    command = "curl -s 'https://api.igdb.com/v4/games/' -d 'search \""+nameWithoutSpecialSymbols+"\"; fields id; where category='0'; limit 1;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][]"
    print("[DEBUG] First getCoverUrl command to get game ID:"+command)
    gameid=subprocess.check_output(command, shell=True).decode( "utf-8" ).strip()
    if gameid=="" or gameid == " " or gameid == "NULL" or gameid == "null":#If not found game id, search without where-category filter
        command = "curl -s 'https://api.igdb.com/v4/games/' -d 'search \""+nameWithoutSpecialSymbols+"\"; fields id; limit 1;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][]"
        print("[DEBUG] Second getCoverUrl command to get ID:"+command)
        gameid=subprocess.check_output(command, shell=True).decode( "utf-8" ).strip()
    command = "curl -s 'https://api.igdb.com/v4/covers/' -d 'fields url; where game = "+str(gameid)+"; limit 1;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][] "    
    print("---")
    print("[DEBUG] getCoverURL command to get coverURL: "+command)
    coverurl=str(subprocess.check_output(command, shell=True).decode( "utf-8" ).strip())
    if len(coverurl) > 3:
        coverurl = coverurl.split("\n")[1].replace("t_thumb","t_cover_small").replace("//","https://").replace("\"","")
    if "https" not in coverurl:
        coverurl = ""
    print("[DEBUG] Returning cover URL: "+coverurl)
    return coverurl
###############################################################################################################################
################## New cover getting script 2023-12
###############################################################################################################################
#1 - Check if cover exists in directory ===> Check if it's correct size > 20 ===> if yes, accept it
#2 - Check if coverUrl is available in DB ===> Download it to the directory =====> if goes OK accept it
#3 - Query IGDB to get cover image ====> add it to DB =====> download it to the directory =====> if goes Ok accept it
###############################################################################################################################
##################
###############################################################################################################################
def checkIfCoverFileIsAvailable(name):
    nameWithoutSpecialSymbolsAndSpaces = re.sub('[^A-Za-z0-9\-]+', '', name)
    coverPath = config["script_path"]+config["year_recap_path"]+"covers/"+nameWithoutSpecialSymbolsAndSpaces+".jpg"
    print("[DEBUG] Checking if cover file exists at: "+coverPath)
    if os.path.isfile(coverPath):
        if os.path.getsize(coverPath) > 50:
            print("[DEBUG] Returning coverurl: "+coverPath)
            return coverPath
        print("[DEBUG] Cover is faulty. Returning nothing.")
        return None
    print("[DEBUG] No local cover found.")
    return None

def makeSureCoverUrlIsInDatabase(name):
    nameWithoutSpecialSymbols = re.sub('[^A-Za-z0-9 \-]+', '', name)
    query = "SELECT coverurl FROM `steamgames` WHERE `name`='"+nameWithoutSpecialSymbols+"' LIMIT 1;"
    print("[DEBUG] Running query: "+query)
    mycursor.execute(query)
    coverResult = mycursor.fetchall()
    coverIsMissing = 0
    if len(coverResult) > 0:
        coverurl = str(coverResult[0][0])
        if coverurl == " " or coverurl == "":
            print("[DEBUG] Cover in DB is empty:"+coverurl+"/linebreak/")
            coverIsMissing = 1
        else:
            print("[DEBUG] Found Cover URL in DB: "+coverurl)
    else:
        coverIsMissing = 1
    if coverIsMissing == 1:
        print("[DEBUG] Cover is not present in the DB.")
        #Get cover image 
        coverurl = getCoverUrl(name)
        print("[DEBUG] Received coverurl: "+coverurl)
        #Add this cover image to DB
        if len(coverResult) > 0: #If entry already exists, update it
            query = "UPDATE `steamgames` SET `coverurl` = '"+coverurl+"' WHERE `name`='"+nameWithoutSpecialSymbols+"' LIMIT 1;"
            print("[DEBUG] Updating coverurl with query: "+query)
            mycursor.execute(query)
        else:
            query = "INSERT INTO `steamgames` VALUES (NULL, NULL, '"+nameWithoutSpecialSymbols+"', '"+str(coverurl)+"')" # If not entry exists, insert a new one 
            print("[DEBUG] Inserting coverurl with query: "+query)
            mycursor.execute(query)
    return coverurl

def downloadCoverFromUrl(name, coverUrl):
    #print("Trying to download Cover IMAGE from Cover URL for game name: "+name+" ....using URL: "+coverUrl)
    if "https:" in coverUrl:
        print("[DEBUG] Correct URL was FOUND for game name: "+name)
        r = requests.get(coverUrl)  #Download cover from coverurl
        nameWithoutSpecialSymbolsAndSpaces = re.sub('[^A-Za-z0-9\-]+', '', name)
        with open(config["script_path"]+config["year_recap_path"]+"covers/"+nameWithoutSpecialSymbolsAndSpaces+".jpg", 'wb') as f:
            f.write(r.content)
        f.close()
        #print(coverUrl.replace("\n",""))
        return coverUrl
    else:
        print("[DEBUG] Correct URL was NOT FOUND for game name: "+name)
        return ""

    
###############################################################################################################################
################## THE END OF ===> New cover getting script 2023-12
###############################################################################################################################

######################################################
########## Total hours played
print("Total hours played: ")
mycursor.execute("SELECT SUM(activityTime) FROM `qqbot`.`activity` WHERE `type` = 'game' AND activityName NOT LIKE 'Visual Studio Code' AND activityName NOT LIKE 'Blender' AND YEAR(DATE) = '"+str(year)+"' GROUP BY `type`;")
totalHoursPlayed = mycursor.fetchone()[0] / 60
totalHoursPlayed = float("{:.1f}".format(totalHoursPlayed))
print(totalHoursPlayed)

#### Save to CSV
pathToThisCsv = pathToScript+'/output/'+str(year)+'/'+'totalHoursPlayed.csv';
os.makedirs(os.path.dirname(pathToThisCsv), exist_ok=True)
f = open(pathToThisCsv,'w+')
f.write(str(totalHoursPlayed))
f.close()

########## Top games played
print("\nIncluding: ")
mycursor.execute("SELECT activityName, SUM(activityTime) FROM `qqbot`.`activity` WHERE activityName NOT LIKE 'Visual Studio Code' AND activityName NOT LIKE 'Blender' AND YEAR(DATE) = '"+str(year)+"' GROUP BY YEAR(DATE), activityName ORDER BY SUM(activityTime) DESC LIMIT 12;")
topGames = mycursor.fetchall()
pathToThisCsv = pathToScript+'/output/'+str(year)+'/'+'topGames.csv';
os.makedirs(os.path.dirname(pathToThisCsv), exist_ok=True)
f = open(pathToThisCsv,'w+')
for game in topGames:
    gameName = str(game[0])
    print("############## GAME: "+gameName+"####################")
    gameHours = int(game[1]/60)
    #gameHours = int(format(gameHours))
    gameHours = str(gameHours)
    print(gameName+" - "+gameHours+"h")
    f.write(str(gameName+";"+gameHours+"\n"))
    #getCoverFromName(gameName)
    coverfile = checkIfCoverFileIsAvailable(gameName) # Check if local cover file is there
    if not coverfile: # If local cover is NOT THERE
        coverurl = makeSureCoverUrlIsInDatabase(gameName) # Check if cover URL is in DB - add Cover URL to DB if it's needed
        downloadCoverFromUrl(gameName, coverurl)  # Download the cover from thsi url 
        
        
f.close()
    
########## Top players
print("\nPlayed by: ")
mycursor.execute("SELECT userId, username, SUM(activityTime) FROM `qqbot`.`activity` WHERE `type` = 'game' AND activityName NOT LIKE 'Visual Studio Code' AND activityName NOT LIKE 'Blender' AND YEAR(DATE) = '"+str(year)+"' GROUP BY YEAR(DATE), `userId` ORDER BY SUM(activityTime) DESC LIMIT 10;")
topPlayers = mycursor.fetchall()
pathToThisCsv = pathToScript+'/output/'+str(year)+'/'+'topPlayers.csv';
os.makedirs(os.path.dirname(pathToThisCsv), exist_ok=True)
f = open(pathToThisCsv,'w+')
for player in topPlayers:
    playerId = player[0]
    mycursor.execute("SELECT `discord_avatar` FROM `userdata` WHERE `discord_user_id`='"+str(playerId)+"' LIMIT 1;")
    avatarid = mycursor.fetchall()
    # print user info
    if avatarid[0][0]:
        avatarid = avatarid[0][0]
        if avatarid != "null":
            avatarurl = "https://cdn.discordapp.com/avatars/"+str(playerId)+"/"+str(avatarid)+".png?size=128"
        else:
            avatarurl = "null"
    else:
        avatarurl = "https://cdn.discordapp.com/avatars/"+str(playerId)+"/NoDiscordAvatar.png?size=128"
    print("Avatar URL: "+avatarurl)
    playerName = str(player[1])
    print("############################################ "+playerName+" ###############################################")
    playerHours = int(player[2]/60)
    #gameHours = int(format(gameHours))
    playerHours = str(playerHours)
    print(playerName+" - Total hours: "+playerHours+"h") #<-------- total hours for this player
    f.write(str(playerId)+";"+playerName+";"+str(playerHours)+";"+str(avatarurl)+"\n")
    
    mycursor.execute("SELECT activityName, SUM(activityTime) FROM `qqbot`.`activity` WHERE `type` = 'game' AND activityName NOT LIKE 'Visual Studio Code' AND activityName NOT LIKE 'Blender' AND YEAR(DATE) = '"+str(year)+"' AND `userId` = '"+str(playerId)+"' GROUP BY YEAR(DATE), `activityName`, `userId` ORDER BY SUM(activityTime) DESC LIMIT 10;")
    playerTopGames = mycursor.fetchall()
    pathToThisCsv = pathToScript+'/output/'+str(year)+'/playerId_'+str(playerId)+'.csv';
    os.makedirs(os.path.dirname(pathToThisCsv), exist_ok=True)
    g = open(pathToThisCsv,'w+')
    for playerGame in playerTopGames:
        playerGameName = str(playerGame[0])
        print("################ "+playerGameName+" ###############")
        #getCoverFromName(playerGameName)
        coverfile = checkIfCoverFileIsAvailable(playerGameName) # Check if local cover file is there
        if not coverfile: # If local cover is NOT THERE
            coverurl = makeSureCoverUrlIsInDatabase(playerGameName) # Check if cover URL is in DB - add Cover URL to DB if it's needed
            downloadCoverFromUrl(playerGameName, coverurl)  # Download the cover from thsi url 
        playerGameHours = str(int(playerGame[1]/60))
        print("\t... "+playerGameName+" - "+playerGameHours)
        g.write(str(playerGameName+";"+playerGameHours+"\n"))
    g.close()



######### Total hours streamed
print("\nTotal hours stream: ")
mycursor.execute("SELECT SUM(activityTime) FROM `qqbot`.`activity` WHERE `type` = 'stream'  AND YEAR(DATE) = '"+str(year)+"' GROUP BY `type`;")
totalHoursStream = mycursor.fetchone()[0] / 60
totalHoursStream = float("{:.1f}".format(totalHoursStream))
print(totalHoursStream)
#### Save to CSV
pathToThisCsv = pathToScript+'/output/'+str(year)+'/'+'totalHoursStreamed.csv';
os.makedirs(os.path.dirname(pathToThisCsv), exist_ok=True)
f = open(pathToThisCsv,'w+')
f.write(str(totalHoursStream))
f.close()

#### Top streamers
print("\nStreamed by: ")
mycursor.execute("SELECT username, SUM(activityTime), userId FROM `qqbot`.`activity` WHERE `type` = 'stream' AND activityName NOT LIKE 'Visual Studio Code' AND activityName NOT LIKE 'Blender' AND YEAR(DATE) = '"+str(year)+"' GROUP BY YEAR(DATE), `userId` ORDER BY SUM(activityTime) DESC LIMIT 7;")
topStreamers = mycursor.fetchall()
pathToThisCsv = pathToScript+'/output/'+str(year)+'/'+'topStreamers.csv';
os.makedirs(os.path.dirname(pathToThisCsv), exist_ok=True)
f = open(pathToThisCsv,'w+')
for streamer in topStreamers:
    streamerName = str(streamer[0])
    streamerHours = int(streamer[1]/60)
    streamerDiscordId = str(streamer[2])
    #gameHours = int(format(gameHours))
    streamerHours = str(streamerHours)
    print(streamerName+" - "+streamerDiscordId+" - "+streamerHours+"h") #<-------- total hours for this player
    f.write(streamerName+";"+str(streamerHours)+";"+streamerDiscordId+"\n")
f.close()


####### Top music
print("\nTotal hours music: ")
mycursor.execute("SELECT SUM(activityTime) FROM `qqbot`.`activity` WHERE `type` = 'music'  AND YEAR(DATE) = '"+str(year)+"' GROUP BY `type`;")
totalHoursMusic = mycursor.fetchone()[0] / 60
totalHoursMusic = float("{:.1f}".format(totalHoursMusic))
print(totalHoursMusic)

#### Save to CSV
pathToThisCsv = pathToScript+'/output/'+str(year)+'/'+'totalHoursMusic.csv';
os.makedirs(os.path.dirname(pathToThisCsv), exist_ok=True)
f = open(pathToThisCsv,'w+')
f.write(str(totalHoursMusic))
f.close()

######### Top listeners
print("\nListened by: ")
mycursor.execute("SELECT username, SUM(activityTime), userId FROM `qqbot`.`activity` WHERE `type` = 'music' AND YEAR(DATE) = '"+str(year)+"' GROUP BY YEAR(DATE), `userId` ORDER BY SUM(activityTime) DESC LIMIT 10;")
topListeners = mycursor.fetchall()
pathToThisCsv = pathToScript+'/output/'+str(year)+'/'+'topListeners.csv';
os.makedirs(os.path.dirname(pathToThisCsv), exist_ok=True)
f = open(pathToThisCsv,'w+')
for listener in topListeners:
    listenerName = str(listener[0])
    listenerHours = int(listener[1]/60)
    listenerDiscordId = str(listener[2])
    #gameHours = int(format(gameHours))
    listenerHours = str(listenerHours).strip()+"h"
    mycursor.execute("SELECT `discord_avatar` FROM `userdata` WHERE `discord_user_id`='"+str(listenerDiscordId)+"' LIMIT 1;")
    avatarid = mycursor.fetchall()
    # print user info
    if avatarid[0][0]:
        avatarid = avatarid[0][0]
        if avatarid != "null":
            avatarurl = "https://cdn.discordapp.com/avatars/"+str(listenerDiscordId)+"/"+str(avatarid)+".png?size=128"
        else:
            avatarurl = "null"
    else:
        avatarurl = "https://cdn.discordapp.com/avatars/"+str(listenerDiscordId)+"/NoDiscordAvatar.png?size=128"
    print("Avatar URL: "+avatarurl)
    print(listenerName+" - "+listenerHours+"h") #<-------- total hours for this player
    f.write(listenerName+";"+str(listenerHours)+";"+avatarurl+"\n")
f.close()

os.remove(config["script_path"]+config["year_recap_path"]+"/temp/"+tmpFileName)