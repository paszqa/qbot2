####################################
#
# 'year-recap - generate image' module for qqBot by Paszq
#
# generates an image from CSV files and images output of the module (getActivityToCsv)
#
# requires:
#
#   pip3 install scikit-image
#
####################################
#Count execution time
from datetime import datetime
startTime = datetime.now()
#Imports
import urllib
import requests #to get discord/twitch avatars
import sys
import subprocess
import re
import math   
import csv #to sort steam players by time
import operator #to sort steam players by time
import os
import jq
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from os.path import exists
import json #JSON read/write capability
from skimage import io #For skewing images
from skimage import transform as tf #For skewing images
import mysql.connector

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

year = "2023"

##Functions


####################################
#   Get image background
####################################
img = Image.open(config["script_path"]+config["year_recap_path"]+'resources/sss-recap-background.png')
img = img.convert("RGB")
imgDraw = ImageDraw.Draw(img,'RGBA')

####################################
#   Sizes, dimensions, padding
####################################

# TITLE MAIN recap
yearCorner = (560,15)
yearTextSize = 150

#TOTAL HOURS PLAYED
totalPlayingCorner = (700,195)
totalPlayingTextSize = 70

#TOP GAMES
topGamesCorner = (240,275)
topGamesCoverSize = (90,120)
topGamesCoverPadding = (110,0)
topGamesCoverText = (topGamesCorner[0],int(topGamesCorner[1]+0.55*topGamesCoverSize[1]))
topGamesTextSize = 25
topGamesTextOffsetPerLetter = topGamesTextSize / 3.5
topGamesCenterFirstText = (topGamesCorner[0]+0.53 * topGamesCoverSize[0], topGamesCorner[1] + topGamesCoverSize[1])

#TOP PLAYERS
discordBlockImageLrCorner = (460,440)
discordPlayerImageLrCorner = (discordBlockImageLrCorner[0] + 35, discordBlockImageLrCorner[1] + 15)
discordPlayerImageSize = (75,75)
discordPlayerImagePadding = (0, 130)
discordPlayerNameLrCorner = (discordPlayerImageLrCorner[0] - 25, discordPlayerImageLrCorner[1] + discordPlayerImageSize[1] + 10)
discordCoverSize = (60,80)
discordCoverLrCorner = (615, 455)
discordCoverPadding = (87,0)
discordCoverOverlayTextOffset = (0,65)
discordCoverOverlayTextSize = 10
discordCoverHoursTextSize = 12
discordCoverHoursTextOffsetPerLetter = discordCoverHoursTextSize / 4.5
#discordCoverHoursTextCenterOffset = (discordCoverLrCorner[0] + 0.53 * discordCoverSize[0], discordCoverLrCorner[1] + discordCoverSize[1] + 5)

#TOTAL HOURS STREAMED
totalStreamedCorner = (700,1753)
totalStreamedTextSize = 70

#TOP streamers
streamerBlockCorner = (535, 1845)
#streamerImageCorner = (548, 1858)
streamerImageCornerOffset = (5,10)
streamerImageSize = (110,110)
streamerPadding = (140,0)
streamerNameCenterOffset = (53,113)
streamerHoursCenterOffset = (53,140)
streamerTextSize = 22
streamerTextOffsetPerLetter = streamerTextSize / 4

#TOTAL HOURS MUSIC
totalMusicCorner = (700,2037)
totalMusicTextSize = 70


#TOP listeners
listenerBlockCorner = (403,2128)
#listenerImageCorner = (548, 2102)
listenerImageCornerOffset = (5,10)
listenerImageSize = (110,110)
listenerPadding = (140,180)
listenerNameCenterOffset = (53,113)
listenerHoursCenterOffset = (53,140)
listenerTextSize = 22
listenerTextOffsetPerLetter = listenerTextSize / 4

#Info text footer
footerCorner = (150, 2384)
footerTextSize = 20

#####################################
#   Fonts
#####################################
yearFont = ImageFont.truetype(config["script_path"]+config["year_recap_path"]+'resources/kremlin.ttf',yearTextSize)
totalFont = ImageFont.truetype(config["script_path"]+config["year_recap_path"]+'resources/kremlin.ttf',totalPlayingTextSize)
hoursFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',topGamesTextSize)
coverTitleFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',discordCoverOverlayTextSize)
coverHoursFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',discordCoverHoursTextSize)
streamerFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',streamerTextSize)
footerFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',footerTextSize)

####################################
# Skewed text functions
####################################
def generate_text(text):
    fnt = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf', 52)
    img = Image.new('1', fnt.getsize(text))
    mask = [x for x in fnt.getmask(text, mode='1')]
    img.putdata(mask)
    img = img.convert('RGBA')
    return img
    
def add_border(img, width):
    new = Image.new('RGBA', (img.width + 2 * width, img.height), (0, 0, 0, 0))
    new.paste(img, (width, 0))
    return new

def shear(img, shear):
    shear = img.transform(img.size, Image.AFFINE, (1, shear, 0, 0, 1, 0))
    return shear

def blackToTransparent(img):
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            newData.append((0, 0, 0, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    return img
    
def resizeNameText(img, factor=3):
    width, height = img.size
    img = img.resize((math.floor(round(width/factor)), math.floor(round(height/factor))), resample=1)
    return img
    
#####################################
############# DRAWING ###############
#####################################

####################################
#    Year
####################################
textStart = (yearCorner)
imgDraw.text(textStart, str(year), font=yearFont, fill=(208,124,13))
####################################
# Total played hours
####################################
totalTimePlayed = open(config["script_path"]+config["year_recap_path"]+'output/'+str(year)+'/totalHoursPlayed.csv', 'r')
for line in totalTimePlayed:
    print(str(line))
    textStart = (totalPlayingCorner)
    imgDraw.text(textStart, str(line) + "  HOURS", font=totalFont, fill=(228,184,73))

####################################
# Top games
####################################
topGames = open(config["script_path"]+config["year_recap_path"]+'output/'+str(year)+'/topGames.csv', 'r')
index = 0
for line in topGames:
    gameTitle = line.split(";")[0]
    gameTimeHours = line.split(";")[1].strip() + "h"
    gameTitlePrepared = re.sub('[^A-Za-z0-9\-]+', '', gameTitle)
    gameTitleWithSymbolsAsSpaces = re.sub('[^A-Za-z0-9\-]+', ' ', gameTitle)
    gameTitleWithSymbolsAsSpaces = gameTitleWithSymbolsAsSpaces.replace("  "," ").replace("  "," ")
    print("Game title: "+gameTitle)
    print("Game title prepared: "+gameTitlePrepared)
    print("Game title with symbols as spaces: "+gameTitleWithSymbolsAsSpaces)
    firstOffset = len(gameTimeHours) * topGamesTextOffsetPerLetter # Offset according to length of hours text
    #secondOffset = len(gameTimeHours) * lastWeekTextOffsetPerLetter # Offset according to length of hours text
    coverPath = config["script_path"]+config["activity_path"]+'temp/'+gameTitlePrepared+".jpg"
    print("DEEEEEEBUG1: "+str(line)+" ---> "+coverPath)
    printCoverText = False
    if not exists(coverPath):
        command = "python3 "+config["script_path"]+config["activity_path"]+"addCoverUrlToDB.py nameyear \""+gameTitleWithSymbolsAsSpaces+"\""
        os.system(command)
        if not exists(coverPath):
            coverPath = config["script_path"]+config["activity_path"]+'resources/NoCover.png'
            #Add text if cover is not there:
            gameTitle = gameTitle[:15]
            coverOffset = len(gameTitle) * topGamesTextOffsetPerLetter # Offset according to length of hours text
            textStart = (topGamesCoverText[0] + index * (topGamesCoverPadding[0]) - coverOffset, topGamesCoverText[1] + index * (topGamesCoverPadding[1]))
            printCoverText = True
    coverImage = Image.open(coverPath)
    coverImage = coverImage.convert("RGBA")
    coverImage = coverImage.resize(topGamesCoverSize, resample=1)
    lrCorner = (topGamesCorner[0] + index * (topGamesCoverPadding[0]), topGamesCorner[1] + index * (topGamesCoverPadding[1]))
    img.paste(coverImage, lrCorner, coverImage)
    #Paste cover text OVER COVER if no cover found
    if printCoverText:
        imgDraw.text(textStart, gameTitle, font=hoursFont, fill=(255,255,255))
    #First line of text (name)
    #textStart = lastWeekCenterFirstText
    textStart = (topGamesCenterFirstText[0] + index * (topGamesCoverPadding[0]) - firstOffset, topGamesCenterFirstText[1] + index * (topGamesCoverPadding[1]))
    imgDraw.text(textStart, gameTimeHours, font=hoursFont, fill=(255,255,255))
    index += 1
    
####################################
# Top players
####################################
topPlayers = open(config["script_path"]+config["year_recap_path"]+'output/'+str(year)+'/topPlayers.csv', 'r')
index = 0
for line in topPlayers:
    #print(str(line), end='')
    blockImagePath = config["script_path"]+config["year_recap_path"]+'resources/playerBlock1024.png'
    blockImage = Image.open(blockImagePath)
    blockImage = blockImage.convert("RGBA")
    lrCornerBlock = (discordBlockImageLrCorner[0] + index * (discordPlayerImagePadding[0]), discordBlockImageLrCorner[1] + index * (discordPlayerImagePadding[1]))
    img.paste(blockImage, lrCornerBlock, blockImage)
    playerName = line.split(";")[1]
    playerTimeHours = line.split(";")[2]+"h"    
    playerImageUrl = line.split(";")[3]
    playerId = line.split(";")[0].strip()
    #if player Image is not null:
    if playerImageUrl != "null" and playerImageUrl != "":
        #Download player image
        print("Getting player image from: "+playerImageUrl)
        r = requests.get(playerImageUrl)  #Download player image from url
        playerImagePath = config["script_path"]+config["activity_path"]+"temp/playerImage.jpg" 
        #open player image or no avatar image
        with open(playerImagePath, 'wb') as f:
            f.write(r.content)
        f.close()
    else:#If player image is null = no avatar
        playerImagePath = config["script_path"]+config["activity_path"]+"resources/noavatar.png"
    #Write player name
    lrCornerImage = (discordPlayerImageLrCorner[0] + index * (discordPlayerImagePadding[0]), discordPlayerImageLrCorner[1] + index * (discordPlayerImagePadding[1]))
    lrCornerText = (discordPlayerNameLrCorner[0] + index * (discordPlayerImagePadding[0]), discordPlayerNameLrCorner[1] + index * (discordPlayerImagePadding[1]))
    print("LR DI:"+str(lrCornerImage))
    print("LR DT:"+str(lrCornerText))
    nameText = generate_text(playerName+" ["+playerTimeHours+"]")
    nameText = add_border(nameText, 20)
    ##nameText = shear(nameText, 0.4)
    nameText = nameText.convert("RGBA")
    nameText = blackToTransparent(nameText)
    nameText = resizeNameText(nameText, 3.5)
    if nameText.size[0] > 120:
        nameText = nameText.resize((120, nameText.size[1]), resample=1)
    #imgDraw.text(lrCornerText, playerName+" ["+playerTimeHours+"]", font=smallFont, fill=(255,255,255))
    img.paste(nameText, lrCornerText, nameText)
    #Paste player image if exists
    print(playerName)
    if exists(playerImagePath):
        if os.path.getsize(playerImagePath) < 100:
            playerImagePath = config["script_path"]+config["activity_path"]+"resources/noavatar.png"
        print("player Image Path: "+playerImagePath)
        playerImage = Image.open(playerImagePath)
        #Convert to transparent and resize
        playerImage = playerImage.convert("RGBA")
        playerImage = playerImage.resize(discordPlayerImageSize, resample=1)
        #Skewing the image
        #width, height = playerImage.size
        #m = 0.3
        #xshift = abs(m) * width
        #new_width = width + int(round(xshift))
        #playerImage = playerImage.transform((new_width, height), Image.AFFINE, (1, m, -xshift if m > 0 else 0, 0, 1, 0), Image.BICUBIC)
        #Skew player image
        #playerImage = io.imread(playerImagePath)
        #afine_tf = tf.AffineTransform(shear=0.2)
        #modifiedPlayerImage = tf.warp(playerImage, inverse_map=afine_tf)
        #playerImage = Image.fromarray(modifiedPlayerImage, 'RGB')
        #Paste prepared player image
        img.paste(playerImage, lrCornerImage, playerImage)
    #Paste images of games
    gameList = open(config["script_path"]+config["year_recap_path"]+"output/"+str(year)+"/playerId_"+playerId+".csv","r")
    gameIndex = 0
    for row in gameList:
        if gameIndex == 11:
            break
        rowSplit = row.split(";")
        gameTitle = rowSplit[0]
        gameTitlePrepared = re.sub('[^A-Za-z0-9\-]+', '', gameTitle)
        gameHours = "0h"
        if len(rowSplit) > 1:
            gameHours = str(rowSplit[1]).strip() + "h"
            print(gameTitle+" = "+gameHours )
        print("Looking for cover for game: "+gameTitlePrepared)
        coverPath = config["script_path"]+config["year_recap_path"]+'covers/'+gameTitlePrepared+".jpg"
        print("Cover path to best tested: "+coverPath)
        shouldWriteName = 0
        if not exists(coverPath) or os.path.getsize(coverPath) < 50:
            print ("Cover not found.........")
            coverPath = config["script_path"]+config["activity_path"]+'resources/NoCover.png'
            shouldWriteName = 1
        coverImage = Image.open(coverPath)
        coverImage = coverImage.convert("RGBA")
        #coverImage = coverImage.resize(discordCoverSize, resample=1)
        coverImage = coverImage.resize(discordCoverSize, resample=1)
        ##Skewing the image
        #width, height = coverImage.size
        #m = 0.53
        #xshift = abs(m) * width
        #new_width = width + int(round(xshift))
        #coverImage = coverImage.transform((new_width, height), Image.AFFINE, (1, m, -xshift if m > 0 else 0, 0, 1, 0), Image.BICUBIC)
        #pasting image
        #coverImage = coverImage.resize(discordCoverSize, resample=1)
        #coverImage = coverImage.resize((53,53), resample=1)
        lrCover = (discordCoverLrCorner[0] + gameIndex * (discordCoverPadding[0]) + index * (discordPlayerImagePadding[0]), discordCoverLrCorner[1] + gameIndex * (discordCoverPadding[1]) + index *  (discordPlayerImagePadding[1]))
        img.paste(coverImage, lrCover, coverImage)
        # Write name on the cover
        if shouldWriteName:
            discordCoverOverlayTextOffset
            topGamesTextOffsetPerLetter
            gameTitle = gameTitle[:12]
            titleStart = (lrCover[0] + discordCoverOverlayTextOffset[0], lrCover[1] + discordCoverOverlayTextOffset[1])
            #textStart = (lrCover[0] + index * (topGamesCoverPadding[0]) - , topGamesCoverText[1] + index * (topGamesCoverPadding[1]))
            imgDraw.text(titleStart, gameTitle, font=coverTitleFont, fill=(255,255,255))
        #Write hours under cover
        coverOffset = len(gameHours) * discordCoverHoursTextOffsetPerLetter # Offset according to length of hours text
        hoursStart = (lrCover[0] + discordCoverSize[0] * 0.50 - coverOffset, lrCover[1] + discordCoverSize[1] + 5)
        imgDraw.text(hoursStart, gameHours, font=coverHoursFont, fill=(255,255,255))
        gameIndex += 1
    index += 1
####################################
# Total streamed hours
####################################
totalTimeStreamed = open(config["script_path"]+config["year_recap_path"]+'output/'+str(year)+'/totalHoursStreamed.csv', 'r')
for line in totalTimeStreamed:
    print(str(line))
    textStart = (totalStreamedCorner)
    imgDraw.text(textStart, str(line) + "  HOURS", font=totalFont, fill=(228,184,73))
####################################
# Top streamers
####################################
topStreamers = open(config["script_path"]+config["year_recap_path"]+'output/'+str(year)+'/topStreamers.csv', 'r')
index = 0
for line in topStreamers:
    #Paste block
    blockImagePath = config["script_path"]+config["year_recap_path"]+'resources/twitch_background.png'
    blockImage = Image.open(blockImagePath)
    blockImage = blockImage.convert("RGBA")
    lrCornerBlock = (streamerBlockCorner[0] + index * (streamerPadding[0]), streamerBlockCorner[1] + index * (streamerPadding[1]))
    img.paste(blockImage, lrCornerBlock, blockImage)
    #Prepare & insert Block contents
    streamerName = line.split(";")[0]
    streamerHours = line.split(";")[1].strip() + "h"
    discordId = line.split(";")[2].strip()
    print("Streamer: "+streamerName+ " - "+streamerHours+" - discord id: "+discordId)
    query = "SELECT twitch_image FROM `qqbot`.`userdata` WHERE `discord_user_id` = '"+discordId+"' LIMIT 1"
    print("Streamer query: "+query)
    mycursor.execute(query)
    twitchUrl = mycursor.fetchone()[0]
    if twitchUrl != "null" and twitchUrl != "" and twitchUrl != "None" and twitchUrl != None:
        #Download player image
        print("Getting player image from: "+str(twitchUrl))
        r = requests.get(twitchUrl)  #Download player image from url
        playerImagePath = config["script_path"]+config["year_recap_path"]+"output/"+year+"/streamerImage_"+discordId+".jpg" 
        #open player image or no avatar image
        with open(playerImagePath, 'wb') as f:
            f.write(r.content)
        f.close()
    else:#If player image is null = no avatar
        playerImagePath = config["script_path"]+config["activity_path"]+"resources/noavatar.png"
    print("Streamer image: "+playerImagePath)
    playerImage = Image.open(playerImagePath)
    #Convert to transparent and resize
    playerImage = playerImage.convert("RGBA")
    playerImage = playerImage.resize(streamerImageSize, resample=1)
    #Paste prepared player image
    print("Pasting image: "+playerImagePath)
    #lrCorner = (streamerImageCorner[0] + index * streamerPadding[0], streamerImageCorner[1] + index * streamerPadding[1])
    lrCorner = (lrCornerBlock[0] + streamerImageCornerOffset[0], lrCornerBlock[1] + streamerImageCornerOffset[1])
    img.paste(playerImage, lrCorner, playerImage)
    #First line of text (name)
    nameStart = (lrCorner[0] + streamerNameCenterOffset[0] - len(streamerName) * streamerTextOffsetPerLetter, lrCorner[1] + streamerNameCenterOffset[1])
    imgDraw.text(nameStart, streamerName, font=streamerFont, fill=(255,255,255))
    hoursStart = (lrCorner[0] + streamerHoursCenterOffset[0] - len(streamerHours) * streamerTextOffsetPerLetter, lrCorner[1] + streamerHoursCenterOffset[1])
    imgDraw.text(hoursStart, streamerHours, font=streamerFont, fill=(255,255,255))
    index += 1
    
####################################
# Total music hours
####################################
totalTimeMusic = open(config["script_path"]+config["year_recap_path"]+'output/'+str(year)+'/totalHoursMusic.csv', 'r')
for line in totalTimeMusic:
    print(str(line))
    textStart = (totalMusicCorner)
    imgDraw.text(textStart, str(line) + "  HOURS", font=totalFont, fill=(228,184,73))
####################################
# Top music
####################################
topListeners = open(config["script_path"]+config["year_recap_path"]+'output/'+str(year)+'/topListeners.csv', 'r')
print("############ LISTENERS ##############")
index = 0
verticalIndex = 0
for line in topListeners:
    #Paste block
    blockImagePath = config["script_path"]+config["year_recap_path"]+'resources/twitch_background.png'
    blockImage = Image.open(blockImagePath)
    blockImage = blockImage.convert("RGBA")
    lrCornerBlock = (listenerBlockCorner[0] + index * (listenerPadding[0]), listenerBlockCorner[1] + verticalIndex * (listenerPadding[1]))
    img.paste(blockImage, lrCornerBlock, blockImage)
    #Prepare & insert Block contents
    streamerName = line.split(";")[0]
    streamerHours = line.split(";")[1].strip() + ""
    avatarUrl = line.split(";")[2].strip()
    print("##############################_")
    print("Listener: "+streamerName+ " - "+streamerHours)
    #query = "SELECT discord_user_id, discord_avatar FROM `qqbot`.`userdata` WHERE `discord_userid` = '"+streamerName+"' LIMIT 1"
    #print("Listener query: "+query)
    #mycursor.execute(query)
    #discord_id = mycursor.fetchone()[0]
    #discord_avatar = mycursor.fetchone()[1]
    #avatarUrl = "https://cdn.discordapp.com/avatars/"+discord_id+"/"+discord_avatar+".png?size=128"
    if avatarUrl != "null" and avatarUrl != "" and avatarUrl != "None" and avatarUrl != None:
        #Download player image
        print("Getting player image from: "+str(avatarUrl))
        r = requests.get(avatarUrl)  #Download player image from url
        playerImagePath = config["script_path"]+config["year_recap_path"]+"output/"+year+"/playerImage_"+discordId+".jpg" 
        #open player image or no avatar image
        with open(playerImagePath, 'wb') as f:
            f.write(r.content)
        f.close()
    else:#If player image is null = no avatar
        playerImagePath = config["script_path"]+config["activity_path"]+"resources/noavatar.png"
    print("Streamer image: "+playerImagePath)
    
    if exists(playerImagePath):
        if os.path.getsize(playerImagePath) < 100:
            playerImagePath = config["script_path"]+config["activity_path"]+"resources/noavatar.png"
    print("player Image Path: "+playerImagePath)
    playerImage = Image.open(playerImagePath)
    #Convert to transparent and resize
    playerImage = playerImage.convert("RGBA")
    playerImage = playerImage.resize(listenerImageSize, resample=1)
    #Paste prepared player image
    print("Pasting image: "+playerImagePath)
    #lrCorner = (listenerImageCorner[0] + index * listenerPadding[0], listenerImageCorner[1] + index * listenerPadding[1])
    lrCorner = (lrCornerBlock[0] + listenerImageCornerOffset[0], lrCornerBlock[1] + listenerImageCornerOffset[1])
    img.paste(playerImage, lrCorner, playerImage)
    #First line of text (name)
    nameStart = (lrCorner[0] + listenerNameCenterOffset[0] - len(streamerName) * listenerTextOffsetPerLetter, lrCorner[1] + listenerNameCenterOffset[1])
    imgDraw.text(nameStart, streamerName, font=streamerFont, fill=(255,255,255))
    hoursStart = (lrCorner[0] + listenerHoursCenterOffset[0] - len(streamerHours) * listenerTextOffsetPerLetter, lrCorner[1] + listenerHoursCenterOffset[1])
    imgDraw.text(hoursStart, streamerHours, font=streamerFont, fill=(255,255,255))
    index += 1
    if index > 7:
        break;
        index = 0
        verticalIndex += 1
####################################
#    Footer
####################################
footerStart = (footerCorner)
executionTime=str(round(datetime.now().timestamp() - startTime.timestamp(),2))
footerText = "Generated by qBot2 in "+executionTime+" on "+str(datetime.now())[0:-7]+" for the sole purpose of naming & shaming. Long live Slav Squat Squad!"
#imgDraw.text((1,188), "Generated in ~"+str(executionTime)+" seconds by qqBot on "+str(datetime.now())[0:-7]+". "+config["image_extra_text"], font=smallfont, fill=(25,25,25))
imgDraw.text(footerStart, footerText, font=footerFont, fill=(25,25,25))
####################################
# Save the image.
####################################
img.save(config["script_path"]+config["year_recap_path"]+'output/'+str(year)+'/recap.png', quality=95)