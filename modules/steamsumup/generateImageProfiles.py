#Count execution time
from datetime import datetime
startTime = datetime.now()
#Imports
import os
from PIL import Image, ImageDraw, ImageFont
import mysql.connector
import subprocess
from datetime import datetime

#Connect to DB
mydb = mysql.connector.connect(
          host="localhost",
            user="loser",
              password="dupa",
                database="trackedtimes"
                )
mycursor = mydb.cursor(buffered=True)

#Settings
pathToScript='/home/pi/steamsumup/'

#Choose size and color
#img = Image.new('RGB', (550, 400), color = (73, 109, 137))
img = Image.open(pathToScript+'background.png')
img = img.convert("RGB")
#Choose fonts
fnt = ImageFont.truetype(pathToScript+'ShareTechMono-Regular.ttf', 17)
smallfnt = ImageFont.truetype(pathToScript+'ShareTechMono-Regular.ttf',11)
#Settings
rowHeight=17
firstRowStart=3

#Draw background
d = ImageDraw.Draw(img,'RGBA')

#Get text from file
f = open(pathToScript+'profileList','r')

#Analyze each line from the file
rowNumber = 0
for steamId in f:
    #remove \n from steamId
    steamId=steamId[0:-1]
    #load user info file
    p = open('/home/pi/steamtracker/users/'+steamId+'/userinfo.txt')
    lines = p.read().splitlines()
    last_line = lines[-1].split(";")[1]
    if last_line == "\n" or last_line == "":
        last_line = lines[-2].split(";")[1]
    currentColor = (49, 199, 38) #green
    #Add extra row for titles
    if rowNumber == 0:
#        d.text((10,firstRowStart+rowHeight*rowNumber), "No", font=fnt, fill=(100,100,100))
#        d.text((70,firstRowStart+rowHeight*rowNumber), "Nickname", font=fnt, fill=(100,100,100))
#        d.text((250,firstRowStart+rowHeight*rowNumber), "Hours", font=fnt, fill=(100,100,100))
        d.text((300,firstRowStart+rowHeight*rowNumber), "Games", font=fnt, fill=(100,100,100))
        d.text((380,firstRowStart+rowHeight*rowNumber), "Games", font=fnt, fill=(100,100,100))
        rowNumber += 1
        d.text((10,firstRowStart+rowHeight*rowNumber), "No", font=fnt, fill=(100,100,100))
        d.text((40,firstRowStart+rowHeight*rowNumber), "Nickname", font=fnt, fill=(100,100,100))
        d.text((200,firstRowStart+rowHeight*rowNumber), "Hours", font=fnt, fill=(100,100,100))
        d.text((300,firstRowStart+rowHeight*rowNumber), "owned", font=fnt, fill=(100,100,100))
        d.text((380,firstRowStart+rowHeight*rowNumber), "played", font=fnt, fill=(100,100,100))
        rowNumber += 1
    #Print No to image
    d.text((10,firstRowStart+rowHeight*rowNumber), str(rowNumber-1), font=fnt, fill=currentColor)
    #Add tint to every second row
    if (rowNumber+1) % 2:
        d.rectangle([(0,(firstRowStart+rowHeight*rowNumber)+2),(530,firstRowStart+rowHeight*(rowNumber+1)+1)], fill=(0,0,0,57))
    #Print nickname to image
    d.text((40,firstRowStart+rowHeight*rowNumber), last_line, font=fnt, fill=currentColor)
    #Get total hours
    mycursor.execute("SELECT SUM(`playedTotal`) FROM (SELECT  * FROM (SELECT `appId`, `playedTotal`,`date` FROM `"+steamId+"` ORDER BY `date` DESC LIMIT 5000) AS t GROUP BY `appId`) AS t2 ORDER BY `playedTotal` DESC")
    personalTotalTime = mycursor.fetchall()[0][0]
    personalTotalTime = str(round(personalTotalTime/60,2))
    #Get number of games played
    mycursor.execute("SELECT COUNT(*) FROM (SELECT  * FROM (SELECT `appId`, `playedTotal`,`date` FROM `"+steamId+"` ORDER BY `date` DESC LIMIT 5000) AS t GROUP BY `appId`) AS t2 ORDER BY `playedTotal` DESC")
    gamesPlayed = mycursor.fetchall()[0][0]
    #Print total hours
    d.text((200,firstRowStart+rowHeight*rowNumber), personalTotalTime, font=fnt, fill=currentColor)
    #Get games owned
    gamesOwned=subprocess.check_output('curl -s "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=EB73438BE5A148D08473BFDFC8D6EEBC&steamid='+str(steamId)+'&format=json" | jq \'.[] | .game_count\'', shell=True)
    gamesOwned=str(gamesOwned)[2:-3]
    #Print games owned
    d.text((300,firstRowStart+rowHeight*rowNumber), str(gamesOwned), font=fnt,fill=currentColor)
    #Get percent of games played
    playedPercent = str(round(int(gamesPlayed)/int(gamesOwned)*100,1))
    #Print games played
    d.text((380,firstRowStart+rowHeight*rowNumber), str(gamesPlayed)+" ("+playedPercent+"%)", font=fnt,fill=currentColor)
    #Iterate rowNumber
    rowNumber += 1

executionTime=str(round(datetime.now().timestamp() - startTime.timestamp(),2))
print("EX:"+executionTime+" NOW:"+str(datetime.now()))
d.text((0,390), "Generated in ~"+str(executionTime)+" seconds by qBot on "+str(datetime.now())[0:-7]+". Long live Slav Squat Squad!", font=smallfnt, fill=(20,20,20))
#Save for the glory of Slav Squat Squad
img.save(pathToScript+'current-slavs.png')
