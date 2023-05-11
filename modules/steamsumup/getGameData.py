####################################
#
# 'steam - getName' module for qqBot by Paszq
# sub-module of 'steam - sumUp'
#
# using Steam APP ID the script queries steam API and steam charts for game's name several times
#
####################################

import mysql.connector
import subprocess
import sys
import re
import os
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

#Settings
pathToScript = os.path.dirname(os.path.realpath(__file__))
mydb = mysql.connector.connect(
          host=config["dbhost"],
            user=config["dbuser"],
              password=config["dbpass"],
                database=config["dbname"],
                )

mycursor = mydb.cursor()
#mycursor.execute("SELECT * FROM `totalTimes` ORDER BY `totalTime` DESC LIMIT 25")

#print(sys.argv[0]);
#print(sys.argv[1])
mode = sys.argv[1]
thingToCheck = sys.argv[2]

#####################################
# Functions
#####################################

#Return coverurl
def getCoverUrl(name):
    #Check for game's cover from IGDB
    command = "curl -s 'https://api.igdb.com/v4/games/' -d 'search \""+name.replace("\"","").replace(";","").replace("'","")+"\"; fields id; where category='0'; limit 1;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][]"
    #print(command)
    gameid=subprocess.check_output(command, shell=True).decode( "utf-8" ).strip()
    if gameid=="" or gameid == " " or gameid == "NULL" or gameid == "null":#If not found game id, search without where-category filter
        command = "curl -s 'https://api.igdb.com/v4/games/' -d 'search \""+name.replace("\"","").replace(";","").replace("'","")+"\"; fields id; limit 1;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][]"
        gameid=subprocess.check_output(command, shell=True).decode( "utf-8" ).strip()
    command = "curl -s 'https://api.igdb.com/v4/covers/' -d 'fields url; where game = "+str(gameid)+"; limit 1;' -H 'Client-ID: "+config["igdb_api_client"]+"' -H 'Authorization: Bearer "+config["igdb_api_token"]+"' -H 'Accept: application/json' | jq .[][] "    
    #print("---")
    #print(command)
    coverurl=str(subprocess.check_output(command, shell=True).decode( "utf-8" ).strip())
    if len(coverurl) > 3:
        coverurl = coverurl.split("\n")[1].replace("t_thumb","t_cover_small").replace("//","https://").replace("\"","")
    if "https" not in coverurl:
        coverurl = ""
    return coverurl




mycursor.execute("CREATE TABLE IF NOT EXISTS `steamgames` (`id` INT(11) NOT NULL AUTO_INCREMENT,`appId` INT(11) NULL DEFAULT NULL,`name` VARCHAR(80) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci', `coverurl` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci', PRIMARY KEY (`id`) USING BTREE) COMMENT='Titles associated with appIDs' COLLATE='utf8mb4_general_ci' ENGINE=InnoDB AUTO_INCREMENT=38;") #Installation if no table found


####################################
# Get name and add name & cover to DB if dont exist
####################################
if mode == "getname":
    #####################################
    # Check if appID exists in DB
    #####################################
    numberOfResults = 0
    mycursor.execute("SELECT `name` FROM `steamgames` WHERE `appId` = '"+thingToCheck+"'")
    for row in mycursor.fetchall():
        numberOfResults += 1

    if numberOfResults == 0:
        for x in range(1,10):
            #Try Steam Store
            gameName=subprocess.check_output('curl -s https://store.steampowered.com/api/appdetails/?appids='+str(thingToCheck)+' | jq \'.[] | .data | .name\'', shell=True)
            if str(gameName) != "b'null\\n'":
                break; #Leave if name is not empty
            #Try Steam Charts
            url = "'https://steamcharts.com/app/"+str(thingToCheck)+"'"
            gameName=subprocess.check_output('curl -s '+url+' | grep -i "<title>"', shell=True)
            #Clean up the name
            gameName=str(gameName).replace(" - Steam Charts","")
            gameName=gameName.replace("Steam Charts - ","")
            gameName=gameName.replace("\\n","")
            gameName=gameName.replace("<title>","")
            gameName=gameName.replace("</title>","")
            gameName=gameName.replace("\t","")
            gameName = str(gameName[2:]).replace("\"","")
            gameName = gameName.replace("\\'","'") #fix apostrophe
            gameName = gameName.replace("\\xe2\\x84\\xa2","®")
            gameName = gameName.replace("\\xe2\\x80\\x99","'")
            gameName = gameName.replace("\\xc2","").replace("\\xae","").replace("\\xe2","")
            gameName = gameName.replace("\\n\'","")
            if(gameName != "null"):
                break;#Break if found game name
            r = requests.get(url, allow_redirects=True)
            time.sleep(4 * x)
        #Clean up the name
        #print("\n\t[getGameData.py] [INFO] Dirty name: "+str(gameName))
        gameName = str(gameName)
        if gameName[0] == "b" and gameName[1] == "'":
            gameName = str(gameName[2:]).replace("\"","")
        #print("\n\t[getGameData.py] [INFO] WIP-1 name: "+str(gameName))
        gameName = gameName.replace("\\'","'") #fix apostrophe
        #print("\n\t[getGameData.py] [INFO] WIP-2 name: "+str(gameName))
        gameName = gameName.replace("\\xe2\\x84\\xa2","®")
        #print("\n\t[getGameData.py] [INFO] WIP-3 name: "+str(gameName))
        gameName = gameName.replace("\\xe2\\x80\\x99","'")
        #print("\n\t[getGameData.py] [INFO] WIP-4 name: "+str(gameName))
        gameName = gameName.replace("\\xc2","").replace("\\xae","").replace("\\xe2","")
        #print("\n\t[getGameData.py] [INFO] WIP-5 name: "+str(gameName))
        gameName = gameName.replace("\\n\'","")
        gameName = re.sub('[^A-Za-z0-9\- ]+', '', gameName)
        #print("\n\t[getGameData.py] [INFO] Clean name: "+str(gameName))
        
        #print("-----> "+gameName)
        #Show output
        print(""+gameName)
        #Add to database for future and commit if not null
        if gameName != "null":
            coverurl = getCoverUrl(gameName)
            mycursor.execute("INSERT INTO `steamgames` VALUES (NULL, "+thingToCheck+", '"+str(gameName)+"', '"+str(coverurl)+"')")
            mycursor.execute("COMMIT;")
    ####################################
    # Get name if it exists
    ####################################
    else:
        mycursor.execute("SELECT name FROM `steamgames` WHERE `appId` = "+thingToCheck)
        gameName = mycursor.fetchone()
        #Show output
        print(str(gameName[0])) #Printing output is needed for showTop.py script

####################################
# add cover
####################################
if mode == "addcover":
    numberOfResults = 0
    #Check if there is a DB entry with already existing coverurl
    mycursor.execute("SELECT `name` FROM `steamgames` WHERE `name` = '"+thingToCheck+"' AND `coverurl` IS NOT NULL AND `coverurl` != ''")
    for row in mycursor.fetchall():
        numberOfResults += 1
    if numberOfResults > 0:
        coverurl = getCoverUrl(thingToCheck)
        command = "UPDATE `steamgames` SET `coverurl` = '"+str(coverurl)+"' WHERE `name` = '"+str(thingToCheck)+"';"
        mycursor.execute(command)
        mycursor.execute("COMMIT;")
        print(coverurl)
    else:    #There are ZERO RESULTS for already existing coverurl for this game name
        coverurl = getCoverUrl(thingToCheck)
        #Check if there is a DB entry with EMPTY coverurl
        mycursor.execute("SELECT `name` FROM `steamgames` WHERE `name` = '"+thingToCheck+"'")        
        for row in mycursor.fetchall():
            numberOfResults += 1
        if numberOfResults > 0:
            #print("there is already a DB entry with empty coverurl for "+thingToCheck)
            #print("Trying to download a cover again")
            command='python3 '+config["script_path"]+config["activity_path"]+'downloadCoverForName.py "'+str(thingToCheck)+'"'
            #print("Getgamedata: CMD:"+command)
            coverUrl = subprocess.check_output(command, shell=True)
            coverUrl = str(coverUrl).replace("'b","").replace("\n'","").replace("\n","")
            #print("hmm:"+coverurl)
        else:
            if coverurl != "" and coverurl != " " and coverurl != "NULL" and coverurl != "null":
                #print("Adding cover entry for "+thingToCheck+" CoverURL: "+coverurl)
                mycursor.execute("INSERT INTO `steamgames` VALUES (NULL, NULL, '"+thingToCheck+"', '"+str(coverurl)+"')")
            else:
                #print("Can't add cover entry for "+thingToCheck+" CoverURL: "+coverurl+" - adding null")
                mycursor.execute("INSERT INTO `steamgames` VALUES (NULL, NULL, '"+thingToCheck+"', NULL)")
        mycursor.execute("COMMIT;")
        print(coverurl)
####################################
# Finito
####################################
mydb.close();

