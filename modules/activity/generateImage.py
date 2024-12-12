####################################
#
# 'activity - generate image' module for qqBot by Paszq
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

##Functions


####################################
#   Get image background
####################################
img = Image.open(config["script_path"]+config["activity_path"]+'resources/background1584x1215.png')
img = img.convert("RGB")
imgDraw = ImageDraw.Draw(img,'RGBA')

####################################
#   Sizes, dimensions, padding
####################################

# Last week general section
lastWeekLrCorner = (210,135)
lastWeekCoverSize = (90,120)
lastWeekCoverWidth = (0,0)
lastWeekCoverPadding = (135,0)
lastWeekCenterFirstText = (260, 260)
lastWeekCenterSecondText = (280, 320)
lastWeekTextSize = 25
lastWeekTextOffsetPerLetter = lastWeekTextSize / 3.5
lastWeekCoverTextSize = 12
lastWeekCoverTextOffsetPerLetter = lastWeekCoverTextSize / 2.7
lastWeekCenterCoverText = (278, 240)

# Activity section - Discord
discordBlockImageLrCorner = (389,319)
#discordPlayerImageSize = (75,75)
discordPlayerImageSize = (70,70)
discordPlayerImageLrCorner = (401, 328)
discordPlayerImagePadding = (228, 0)
discordPlayerNameLrCorner = (472, 329)
discordFontSize = 14
discordCoverSize = (40,53)
#discordCoverSize = (55,53)
discordCoverLrCorner = (482, 345)
discordCoverPadding = (37,0)


# Activity section - Twitch
twitchBlockImageLrCorner = (389,421)
twitchPlayerImageSize = (70,70)
twitchPlayerImageLrCorner = (401, 430) 
twitchPlayerImagePadding = (228, 0)
twitchPlayerNameLrCorner = (480, 445)
twitchFontSize = 18
twitchSecondTextPadding = ((-5), 30)

# Activity section - Steam
steamBlockImageLrCorner = (389,529)
steamPlayerImageSize = (70,70)
steamPlayerImageLrCorner = (401, 537) 
steamPlayerImagePadding = (228, 0)
steamPlayerNameLrCorner = (472, 537)
steamFontSize = 14
steamCoverSize = (40,53)
steamCoverLrCorner = (482, 553)
steamCoverPadding = (37,0)

# Total times general section
totalTimesLrCorner = (218,680)
totalTimesCoverSize = (80,112)
totalTimesCoverWidth = (80,0)
totalTimesCoverPadding = (13,0)
totalTimesCenterFirstText = (257, 793)
totalTimesTextSize = 19 
totalTimesTextOffsetPerLetter = totalTimesTextSize / 3.7
totalTimesSmallTextPadding = (0,20)
totalTimesSmallTextSize = 12
totalTimesSmallTextOffsetPerLetter = totalTimesSmallTextSize / 3.7


# Best ranks general section
rankingLrCorner = (218,851)
rankingCoverSize = (80,112)
rankingCoverWidth = (80,0)
rankingCoverPadding = (13,0)
rankingStarsLrCorner = (217,960)
rankingCenterFirstText = (258, 972)
rankingCenterSecondText = (279, 988)
rankingTextSize = 20
rankingTextOffsetPerLetter = rankingTextSize / 3.7
rankingSmallTextPadding = (0,20)
rankingSmallTextSize = 12
rankingSmallTextOffsetPerLetter = rankingSmallTextSize / 3.7


# Worst ranks general section
worstLrCorner = (218,1024)
worstCoverSize = (80,112)
worstCoverWidth = (80,0)
worstCoverPadding = (13,0)
worstStarsLrCorner = (217,1133)
worstCenterFirstText = (258, 1145)
worstTextSize = 20
worstTextOffsetPerLetter = worstTextSize / 3.7
worstSmallTextPadding = (0,20)
worstSmallTextSize = 12
worstSmallTextOffsetPerLetter = worstSmallTextSize / 3.7

# Worst ranks general section
musicTextCenter = (1110,1060)
musicTextSize = 42
musicTextOffsetPerLetter = musicTextSize / 3.7
musicSmallTextCenter = (1110,1110)
musicSmallTextSize = 12
musicSmallTextOffsetPerLetter = worstSmallTextSize / 3.7

#User count
countTextCenter = (1380,1060)
countSmallTextCenter = (1400,1110)

#####################################
#   Fonts
#####################################
titleFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',lastWeekTextSize)
titleCoverFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',lastWeekCoverTextSize)
smallFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',discordFontSize)
totalTimesFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',totalTimesTextSize)
totalTimesSmallFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',totalTimesSmallTextSize)
rankingFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',rankingTextSize)
rankingSmallFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',rankingSmallTextSize)
worstFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',worstTextSize)
worstSmallFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',worstSmallTextSize)
musicFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',musicTextSize)
musicSmallFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',musicSmallTextSize)
####################################
# Draw title from config
####################################
#imageTitle = config["activity_image_title"]
#imgDraw.text((80, 10), imageTitle, font=titleFont, fill=(255,255,255))

####################################
# Get most played games title
####################################
#mostPlayedTitle = " Most\nPlayed"
#imgDraw.text((10, 50), mostPlayedTitle, font=titleFont, fill=(255,255,255))

####################################
# Most played games
####################################
mostPlayedGames = open(config["script_path"]+config["activity_path"]+'output/recent-games.csv', 'r')
index = 0
for line in mostPlayedGames:
    gameTitle = line.split(";")[0]
    gameTime = line.split(";")[1]
    gameTimeHours = str(round((float(gameTime) / 60),1))+"h"
    gameCoverUrl = line.split(";")[2]
    gameTitlePrepared = re.sub('[^A-Za-z0-9\-]+', '', gameTitle)
    gameTitleWithSymbolsAsSpaces = re.sub('[^A-Za-z0-9\-]+', ' ', gameTitle)
    gameTitleWithSymbolsAsSpaces = gameTitleWithSymbolsAsSpaces.replace("  "," ").replace("  "," ")
    print("Game title: "+gameTitle)
    print("Game title prepared: "+gameTitlePrepared)
    print("Game title with symbols as spaces: "+gameTitleWithSymbolsAsSpaces)
    firstOffset = len(gameTimeHours) * lastWeekTextOffsetPerLetter # Offset according to length of hours text
    #secondOffset = len(gameTimeHours) * lastWeekTextOffsetPerLetter # Offset according to length of hours text
    coverPath = config["script_path"]+config["activity_path"]+'temp/'+gameTitlePrepared+".jpg"
    #Paste game cover image if exists
    printCoverText = False
    if not exists(coverPath):
        command = "python3 "+config["script_path"]+config["activity_path"]+"addCoverUrlToDB.py nameyear \""+gameTitleWithSymbolsAsSpaces+"\""
        os.system(command)
        if not exists(coverPath):
            coverPath = config["script_path"]+config["activity_path"]+'resources/NoCover.png'
            #Add text if cover is not there:
            gameTitle = gameTitle[:15]
            coverOffset = len(gameTitle) * lastWeekCoverTextOffsetPerLetter # Offset according to length of hours text
            textStart = (lastWeekCenterCoverText[0] + index * (lastWeekCoverWidth[0] + lastWeekCoverPadding[0]) - coverOffset, lastWeekCenterCoverText[1] + index * (lastWeekCoverWidth[1] + lastWeekCoverPadding[1]))
            printCoverText = True
    coverImage = Image.open(coverPath)
    coverImage = coverImage.convert("RGBA")
    coverImage = coverImage.resize(lastWeekCoverSize, resample=1)
    lrCorner = (lastWeekLrCorner[0] + index * (lastWeekCoverWidth[0] + lastWeekCoverPadding[0]), lastWeekLrCorner[1] + index * (lastWeekCoverWidth[1] + lastWeekCoverPadding[1]))
    print("LR:"+str(lrCorner))
    img.paste(coverImage, lrCorner, coverImage)
    #Paste cover text OVER COVER if no cover found
    if printCoverText:
        imgDraw.text(textStart, gameTitle, font=titleCoverFont, fill=(255,255,255))
    #First line of text (name)
    #textStart = lastWeekCenterFirstText
    textStart = (lastWeekCenterFirstText[0] + index * (lastWeekCoverWidth[0] + lastWeekCoverPadding[0]) - firstOffset, lastWeekCenterFirstText[1] + index * (lastWeekCoverWidth[1] + lastWeekCoverPadding[1]))
    imgDraw.text(textStart, gameTimeHours, font=titleFont, fill=(255,255,255))
    #Second line of text (hours)
    #textStart = lastWeekCenterSecondText
    #textStart = (lastWeekCenterSecondText[0] + index * (lastWeekCoverWidth[0] + lastWeekCoverPadding[0]) - secondOffset, lastWeekCenterSecondText[1] + index * (lastWeekCoverWidth[1] + lastWeekCoverPadding[1]))
    #imgDraw.text(textStart, gameTimeHours, font=titleFont, fill=(255,255,255))
    index += 1


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
    
####################################
# GetDiscord activity title
####################################
#discordActivityTitle = "Discord activity"
#imgDraw.text((45, 142), discordActivityTitle, font=titleFont, fill=(255,255,255))
####################################
# Discord activity
####################################
discordActivity = open(config["script_path"]+config["activity_path"]+'output/recent-players.csv', 'r')
index = 0
for line in discordActivity:
    #print(str(line), end='')
    blockImagePath = config["script_path"]+config["activity_path"]+'resources/playerBlock.png'
    blockImage = Image.open(blockImagePath)
    blockImage = blockImage.convert("RGBA")
    lrCornerBlock = (discordBlockImageLrCorner[0] + index * (discordPlayerImagePadding[0]), discordBlockImageLrCorner[1] + index * (discordPlayerImagePadding[1]))
    img.paste(blockImage, lrCornerBlock, blockImage)
    playerName = line.split(";")[0]
    playerTime = line.split(";")[1]
    playerTimeHours = str(round((float(playerTime) / 60),1))+"h"
    playerImageUrl = line.split(";")[2]
    playerId = line.split(";")[3].strip()
    #if player Image is not null:
    if playerImageUrl != "null" and playerImageUrl != "":
        #Download player image
        r = requests.get(playerImageUrl)  #Download player image from url
        print("---------------------------> PLAYER IMAGE URL: "+playerImageUrl)
        playerImagePath = config["script_path"]+config["activity_path"]+"temp/playerImage.jpg" 
        #open player image or no avatar image
        with open(playerImagePath, 'wb') as f:
            f.write(r.content)
        f.close()
        if os.path.getsize(playerImagePath) < 10:
            playerImagePath = config["script_path"]+config["activity_path"]+"resources/noavatar.png"
    else:#If player image is null = no avatar
        playerImagePath = config["script_path"]+config["activity_path"]+"resources/noavatar.png"
    #Write player name
    lrCornerImage = (discordPlayerImageLrCorner[0] + index * (discordPlayerImagePadding[0]), discordPlayerImageLrCorner[1] + index * (discordPlayerImagePadding[1]))
    lrCornerText = (discordPlayerNameLrCorner[0] + index * (discordPlayerImagePadding[0]), discordPlayerNameLrCorner[1] + index * (discordPlayerImagePadding[1]))
    print("LR DI:"+str(lrCornerImage))
    print("LR DT:"+str(lrCornerText))
    nameText = generate_text(playerName+" ["+playerTimeHours+"]")
    nameText = add_border(nameText, 20)
    #nameText = shear(nameText, 0.4)
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
    gameList = open(config["script_path"]+config["activity_path"]+"output/recent-games-"+playerId+".csv","r")
    gameIndex = 0
    for row in gameList:
        if gameIndex == 3:
            break
        rowSplit = row.split(";")
        gameTitle = rowSplit[0]
        gameTitlePrepared = re.sub('[^A-Za-z0-9\-]+', '', gameTitle)
        if len(rowSplit) > 1:
            gameCoverUrl = rowSplit[1]
        coverPath = config["script_path"]+config["activity_path"]+'temp/'+gameTitlePrepared+".jpg"
        if not exists(coverPath):
            coverPath = config["script_path"]+config["activity_path"]+'resources/NoCover.png'
        coverImage = Image.open(coverPath)
        coverImage = coverImage.convert("RGBA")
        #coverImage = coverImage.resize(discordCoverSize, resample=1)
        coverImage = coverImage.resize((33,53), resample=1)
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
        gameIndex += 1
    index += 1
    

####################################
# Twitch streaming title
####################################
#discordActivityTitle = "Streamers"
#imgDraw.text((45, 135), discordActivityTitle, font=titleFont, fill=(255,255,255))
####################################
# stream activity
####################################
streamActivity = open(config["script_path"]+config["activity_path"]+'output/recent-streamers.csv', 'r')
index = 0
for line in streamActivity:
    blockImagePath = config["script_path"]+config["activity_path"]+'resources/playerBlock.png'
    blockImage = Image.open(blockImagePath)
    blockImage = blockImage.convert("RGBA")
    lrCornerBlock = (twitchBlockImageLrCorner[0] + index * (twitchPlayerImagePadding[0]), twitchBlockImageLrCorner[1] + index * (twitchPlayerImagePadding[1]))
    img.paste(blockImage, lrCornerBlock, blockImage)
    streamerName =  line.split(";")[0]
    streamerTime =  line.split(";")[1]
    streamerTimeHours = str(round((float(streamerTime) / 60),1))+"h"
    streamerImageUrl =  line.split(";")[2]
    #Check if streamer image is correct format
    streamerImageExists = False
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    if "None" not in streamerImageUrl:
        r = requests.head(streamerImageUrl)
        #print(r.headers["content-type"])
        if r.headers["content-type"] in image_formats:
            #Download player image
            r = requests.get(streamerImageUrl)  #Download streamer profile image
            streamerImagePath = config["script_path"]+config["activity_path"]+"temp/streamerImage.jpg" 
            with open(streamerImagePath, 'wb') as f:
                f.write(r.content)
            f.close()
            streamerImageExists = True
            
    if streamerImageExists:
        streamerImagePath = config["script_path"]+config["activity_path"]+"temp/streamerImage.jpg"
    else:
        streamerImagePath = config["script_path"]+config["activity_path"]+"resources/noavatar.png"
    #Calc corners
    lrCornerImage = (twitchPlayerImageLrCorner[0] + index * (twitchPlayerImagePadding[0]), twitchPlayerImageLrCorner[1] + index * (twitchPlayerImagePadding[1]))
    lrCornerName = (twitchPlayerNameLrCorner[0] + index * (twitchPlayerImagePadding[0]), twitchPlayerNameLrCorner[1] + index * (twitchPlayerImagePadding[1]))
    lrCornerText = (twitchPlayerNameLrCorner[0] + index * (twitchPlayerImagePadding[0]) + twitchSecondTextPadding[0], twitchPlayerNameLrCorner[1] + index * (twitchPlayerImagePadding[1]) + twitchSecondTextPadding[1])
    #Write streamer name....
    #Skew streamer name:
    nameText = generate_text(streamerName)#+" ["+playerTimeHours+"]")
    nameText = add_border(nameText, 20)
    #nameText = shear(nameText, 0.4)
    nameText = nameText.convert("RGBA")
    nameText = blackToTransparent(nameText)
    nameText = resizeNameText(nameText, 3)
    if nameText.size[0] > 120:
        nameText = nameText.resize((120, nameText.size[1]), resample=1)
    #Skew streamer streaming time:
    timeText = generate_text("Streamed for "+streamerTimeHours+"")
    timeText = add_border(timeText, 20)
    #timeText = shear(timeText, 0.4)
    timeText = timeText.convert("RGBA")
    timeText = blackToTransparent(timeText)
    timeText = resizeNameText(timeText, 3)
    if timeText.size[0] > 120:
        timeText = timeText.resize((120, timeText.size[1]), resample=1)
    #imgDraw.text(lrCornerText, playerName+" ["+playerTimeHours+"]", font=smallFont, fill=(255,255,255))
    img.paste(nameText, lrCornerName, nameText)
    img.paste(timeText, lrCornerText, timeText)
    
    #imgDraw.text(lrCornerName, streamerName, font=titleFont, fill=(255,255,255))
    #imgDraw.text(lrCornerText, "Streamed for "+streamerTimeHours+"", font=smallFont, fill=(175,175,175))
    #Paste streamer image if exists
    if exists(streamerImagePath):
        streamerImage = Image.open(streamerImagePath)
        streamerImage = streamerImage.convert("RGBA")
        #streamerImage = streamerImage.resize(twitchPlayerImageSize, resample=1)
        #Convert to transparent and resize
        streamerImage = streamerImage.resize(twitchPlayerImageSize, resample=1)
        #Skewing the image
        #width, height = streamerImage.size
        #m = 0.3
        #xshift = abs(m) * width
        #new_width = width + int(round(xshift))
        #streamerImage = streamerImage.transform((new_width, height), Image.AFFINE, (1, m, -xshift if m > 0 else 0, 0, 1, 0), Image.BICUBIC)
        img.paste(streamerImage, lrCornerImage, streamerImage)
    index += 1


####################################
# Steam activity
####################################
steamActivity = open(config["script_path"]+config["activity_path"]+'output/recent-steam.csv', 'r')
#steamCsv = csv.reader(open(config["script_path"]+config["activity_path"]+'output/recent-steam.csv'), delimiter=";")
#sortedCsv = sorted(steamCsv, key=operator.itemgetter(2), reverse=False)
#print(sortedCsv)
steamCsv = csv.reader(open(config["script_path"]+config["activity_path"]+'output/recent-steam.csv'), delimiter=";")
sortedCsv = sorted(steamCsv, key=lambda x: int(x[2]), reverse=True)
print("---STEAM activity---")
print("Sorted CSV: ")
print(sortedCsv)
print("\n")

index = 0
for line in sortedCsv:
    blockImagePath = config["script_path"]+config["activity_path"]+'resources/playerBlock.png'
    blockImage = Image.open(blockImagePath)
    blockImage = blockImage.convert("RGBA")
    lrCornerBlock = (steamBlockImageLrCorner[0] + index * (steamPlayerImagePadding[0]), steamBlockImageLrCorner[1] + index * (steamPlayerImagePadding[1]))
    img.paste(blockImage, lrCornerBlock, blockImage)
    #splitLine = line.split(";")
    playerName = line[1]
    playerTime = line[2]
    playerTimeHours = str(round((float(playerTime) / 60),1))+"h"
    playerImageUrl = line[3]
    playerId = line[0].strip()
    print("Steam player data:\n\t"+str(line))
    #Download player image
    r = requests.get(playerImageUrl)  #Download cover from coverurl
    playerImagePath = config["script_path"]+config["activity_path"]+"temp/steamImage.jpg" 
    with open(playerImagePath, 'wb') as f:
        f.write(r.content)
    f.close()
    #Calculate corners
    lrCornerImage = (steamPlayerImageLrCorner[0] + index * (steamPlayerImagePadding[0]), steamPlayerImageLrCorner[1] + index * (steamPlayerImagePadding[1]))
    lrCornerText = (steamPlayerNameLrCorner[0] + index * (steamPlayerImagePadding[0]), steamPlayerNameLrCorner[1] + index * (steamPlayerImagePadding[1]))
    #Write player name
    #Skew player name:
    nameText = generate_text(playerName+" ["+playerTimeHours+"]")#+" ["+playerTimeHours+"]")
    nameText = add_border(nameText, 20)
    #nameText = shear(nameText, 0.4)
    nameText = nameText.convert("RGBA")
    nameText = blackToTransparent(nameText)
    nameText = resizeNameText(nameText, 3.5)
    if nameText.size[0] > 120:
        nameText = nameText.resize((120, nameText.size[1]), resample=1)
    #imgDraw.text(lrCornerText, playerName+" ["+playerTimeHours+"]", font=smallFont, fill=(255,255,255))
    img.paste(nameText, lrCornerText, nameText)
    #Paste player image if exists
    if exists(playerImagePath):
        #playerImage = Image.open(playerImagePath)
        #playerImage = playerImage.convert("RGBA")
        #playerImage = playerImage.resize(steamPlayerImageSize, resample=1)
        playerImage = Image.open(playerImagePath)
        #Convert to transparent and resize
        playerImage = playerImage.convert("RGBA")
        playerImage = playerImage.resize(steamPlayerImageSize, resample=1)
        ##Skewing the image
        #width, height = playerImage.size
        #m = 0.3
        #xshift = abs(m) * width
        #new_width = width + int(round(xshift))
        #playerImage = playerImage.transform((new_width, height), Image.AFFINE, (1, m, -xshift if m > 0 else 0, 0, 1, 0), Image.BICUBIC)
        img.paste(playerImage, lrCornerImage, playerImage)
    #Paste images of games
    gameList = open(config["script_path"]+config["activity_path"]+"output/recent-steam-"+playerId+".csv","r")
    gameIndex = 0
    for row in gameList:
        if gameIndex == 3:
            break
        gameTitle = row.split(";")[1]
        gameTitlePrepared = re.sub('[^A-Za-z0-9\-]+', '', gameTitle)
        gameCoverUrl = row.split(";")[3]
        coverPath = config["script_path"]+config["activity_path"]+'temp/'+gameTitlePrepared+".jpg"
        command = "python3 "+config["script_path"]+config["activity_path"]+"downloadCoverForName.py \""+gameTitle+"\""
        print("DOWNLOAD COVER COMMAND: "+command)
        os.system(command)
        if not exists(coverPath):
            coverPath = config["script_path"]+config["activity_path"]+'resources/NoCover.png'
        coverImage = Image.open(coverPath)
        coverImage = coverImage.convert("RGBA")
        #coverImage = coverImage.resize(discordCoverSize, resample=1)
        coverImage = coverImage.resize((33,53), resample=1)
        #Skewing the image
        #width, height = coverImage.size
        #m = 0.53
        #xshift = abs(m) * width
        #new_width = width + int(round(xshift))
        #coverImage = coverImage.transform((new_width, height), Image.AFFINE, (1, m, -xshift if m > 0 else 0, 0, 1, 0), Image.BICUBIC)
        #pasting image
        #coverImage = coverImage.resize(discordCoverSize, resample=1)
        #coverImage = coverImage.resize((53,53), resample=1)
        #coverImage = Image.open(coverPath)
        #coverImage = coverImage.convert("RGBA")
        #coverImage = coverImage.resize(steamCoverSize, resample=1)
        #lrCover = (steamCoverLrCorner[0] + gameIndex * (steamCoverSize[0] + steamCoverPadding[0]), steamCoverLrCorner[1] + index * (steamPlayerImagePadding[1]))
        lrCover = (steamCoverLrCorner[0] + gameIndex * (steamCoverPadding[0]) + index * (steamPlayerImagePadding[0]), steamCoverLrCorner[1] + gameIndex * (steamCoverPadding[1]) + index *  (steamPlayerImagePadding[1]))
        img.paste(coverImage, lrCover, coverImage)
        gameIndex += 1
    index += 1
    

####################################
# Total times
####################################
totalTimes = open(config["script_path"]+config["steam_sum_up_path"]+'output/most-played-total.csv', 'r')
totalTimes = totalTimes.readlines()[1:]
print("\n---Total Times---")
index = 0
for line in totalTimes:
    if index > 13:
        break
    gameTitle = line.split(";")[1]
    print(str(gameTitle))
    gameTimeHours = line.split(";")[2].split(".")[0]+"h"
    print("\tHours: "+str(gameTimeHours))
    gameSlavs = line.split(";")[3].replace("\n","")
    #gameTimeHours = str(round((float(gameTime) / 60),1))+"h"
    #gameCoverUrl = line.split(";")[2]
    gameTitlePrepared = re.sub('[^A-Za-z0-9\-]+', '', gameTitle)
    print("\tGame title prepared: "+str(gameTitlePrepared))
    offset = len(gameTimeHours) * totalTimesTextOffsetPerLetter # Offset according to length of hours text
    coverPath = config["script_path"]+config["activity_path"]+'temp/'+gameTitlePrepared+".jpg"
    stateOfFile = str(exists(coverPath))
    print("\tCoverpath:"+coverPath+" ==== "+stateOfFile)
    #Paste game cover image if exists
    if stateOfFile == "False":
        command='python3 '+config["script_path"]+config["activity_path"]+'downloadCoverForName.py "'+str(gameTitle)+'"'
        print("\tCMD:"+command)
        subprocess.check_output(command, shell=True)
        coverPath = config["script_path"]+config["activity_path"]+'temp/'+gameTitlePrepared+".jpg"
        stateOfFile = str(exists(coverPath))
        if stateOfFile == "False":
            coverPath = config["script_path"]+config["activity_path"]+'resources/NoCover.png'
    coverImage = Image.open(coverPath)
    coverImage = coverImage.convert("RGBA")
    coverImage = coverImage.resize(totalTimesCoverSize, resample=1)
    lrCorner = (totalTimesLrCorner[0] + index * (totalTimesCoverWidth[0] + totalTimesCoverPadding[0]), totalTimesLrCorner[1] + index * (totalTimesCoverWidth[1] + totalTimesCoverPadding[1]))
    print("\tLR:"+str(lrCorner))
    img.paste(coverImage, lrCorner, coverImage)
    textStart = (totalTimesCenterFirstText[0] + index * (totalTimesCoverWidth[0] + totalTimesCoverPadding[0]) - offset, totalTimesCenterFirstText[1] + index * (totalTimesCoverWidth[1] + totalTimesCoverPadding[1]))
    imgDraw.text(textStart, gameTimeHours, font=totalTimesFont, fill=(255,255,255))
    offset = len("BY "+gameSlavs+" SLAVS") * totalTimesSmallTextOffsetPerLetter # Offset according to length of hours text
    smallTextStart = (totalTimesCenterFirstText[0] + totalTimesSmallTextPadding[0] + index * (totalTimesCoverWidth[0] + totalTimesCoverPadding[0]) - offset, totalTimesCenterFirstText[1] + totalTimesSmallTextPadding[1] + index * (totalTimesCoverWidth[1] + totalTimesCoverPadding[1]))
    if int(gameSlavs) > 1:
        slavText = "BY "+gameSlavs+" SLAVS"
    else:
        slavText = "BY "+gameSlavs+" SLAV"
    imgDraw.text(smallTextStart, slavText, font=totalTimesSmallFont, fill=(255,204,0))
    index += 1
    
####################################
# Best ranks
####################################

bestRanks = open('/home/pi/qBot/votes/ranking_sorted.csv', 'r') # TODO: CHANGE PATH WHEN VOTESYSTEM IS READY
bestRanks = bestRanks.readlines()[1:]
print("\n---Best ranks---")
index = 0
for line in bestRanks:
    if index > 13:
        break
    gameTitle = line.split(";")[0].split(" (")[0]
    print(gameTitle)
    gameSlavs = line.split(";")[2].replace("\n","")
    gameRank = line.split(";")[3].replace("\n","")
    #gameTimeHours = str(round((float(gameTime) / 60),1))+"h"
    #gameCoverUrl = line.split(";")[2]
    gameTitlePrepared = re.sub('[^A-Za-z0-9\-]+', '', gameTitle)
    #print(gameTitlePrepared)
    gameRank = gameRank[:4]
    offset = len(gameRank) * rankingTextOffsetPerLetter # Offset according to length of hours text
    coverPath = config["script_path"]+config["activity_path"]+'temp/'+gameTitlePrepared+".jpg"
    stateOfFile = str(exists(coverPath))
    print("\tCoverpath:"+coverPath+" ==== "+stateOfFile)
    #Paste game cover image if exists
    if stateOfFile == "False":
        command='python3 '+config["script_path"]+config["activity_path"]+'downloadCoverForName.py "'+str(gameTitle)+'"'
        print("\tCMD:"+command)
        subprocess.check_output(command, shell=True)
        coverPath = config["script_path"]+config["activity_path"]+'temp/'+gameTitlePrepared+".jpg"
        stateOfFile = str(exists(coverPath))
        if stateOfFile == "False":
            coverPath = config["script_path"]+config["activity_path"]+'resources/NoCover.png'
    coverImage = Image.open(coverPath)
    coverImage = coverImage.convert("RGBA")
    coverImage = coverImage.resize(rankingCoverSize, resample=1)
    lrCorner = (rankingLrCorner[0] + index * (rankingCoverWidth[0] + rankingCoverPadding[0]), rankingLrCorner[1] + index * (rankingCoverWidth[1] + rankingCoverPadding[1]))
    print("\tLR:"+str(lrCorner))
    img.paste(coverImage, lrCorner, coverImage)
    
    blackStar = Image.open(config["script_path"]+config["activity_path"]+'resources/0star.png')
    blackStar = blackStar.convert("RGBA")
    blackStar = blackStar.resize((20,20), Image.ANTIALIAS)
    star = Image.open(config["script_path"]+config["activity_path"]+'resources/1star.png')
    star = star.convert("RGBA")
    star = star.resize((15,15), Image.ANTIALIAS)
    fullStars = int(float(gameRank))
    fraction = float(gameRank) - int(float(gameRank))
    
    for x in range(5):
        starLrCorner = (rankingStarsLrCorner[0] + index * (rankingCoverWidth[0] + rankingCoverPadding[0]) + x * 16 - 2, rankingStarsLrCorner[1] + index * (rankingCoverWidth[1] + rankingCoverPadding[1]) - 2)
        img.paste(blackStar, starLrCorner, blackStar) 
        
    for i in range(fullStars):
        starLrCorner = (rankingStarsLrCorner[0] + index * (rankingCoverWidth[0] + rankingCoverPadding[0]) + i * 16, rankingStarsLrCorner[1] + index * (rankingCoverWidth[1] + rankingCoverPadding[1]))
        img.paste(star, starLrCorner, star) 
    if fraction > 0:
        starWidth, starHeight = star.size
        partialWidth = fraction*starWidth
        #print("Part width: "+str(partialWidth))
        partialStar = star.crop((0,0,partialWidth,15))
        partialStar.convert("RGBA")
        #print(str(starWidth)+" .... "+str(starHeight))
        starLrCorner = (rankingStarsLrCorner[0] + index * (rankingCoverWidth[0] + rankingCoverPadding[0]) + (i + 1) * 16, rankingStarsLrCorner[1] + index * (rankingCoverWidth[1] + rankingCoverPadding[1]))
        img.paste(partialStar, starLrCorner, partialStar)
        
    textStart = (rankingCenterFirstText[0] + index * (rankingCoverWidth[0] + rankingCoverPadding[0]) - offset, rankingCenterFirstText[1] + index * (rankingCoverWidth[1] + rankingCoverPadding[1]))
    imgDraw.text(textStart, gameRank, font=rankingFont, fill=(255,255,255))
    
    
    
    if int(gameSlavs) > 1:
        slavText = "BY "+gameSlavs+" SLAVS"
    else:
        slavText = "BY "+gameSlavs+" SLAV"
    offset = len(slavText) * rankingSmallTextOffsetPerLetter # Offset according to length of hours text
    smallTextStart = (rankingCenterFirstText[0] + index * (rankingCoverWidth[0] + rankingCoverPadding[0]) + rankingSmallTextPadding[0] - offset, rankingCenterFirstText[1] + index * (rankingCoverWidth[1] + rankingCoverPadding[1]) + rankingSmallTextPadding[1])
    
    
    imgDraw.text(smallTextStart, slavText, font=rankingSmallFont, fill=(255,204,0))
    index += 1
        
####################################
# Worst ranks
####################################

worstRanks = open('/home/pi/qBot/votes/ranking_sorted.csv', 'r') # TODO: CHANGE PATH WHEN VOTESYSTEM IS READY
worstRanks = reversed(worstRanks.readlines())

index = 0
for line in worstRanks:
    if index > 6:
        break
    gameTitle = line.split(";")[0].split(" (")[0]
    print(gameTitle)
    gameSlavs = line.split(";")[2].replace("\n","")
    gameRank = line.split(";")[3].replace("\n","")
    gameRank = gameRank[:4]
    #gameTimeHours = str(round((float(gameTime) / 60),1))+"h"
    #gameCoverUrl = line.split(";")[2]
    gameTitlePrepared = re.sub('[^A-Za-z0-9\-]+', '', gameTitle)
    #print(gameTitlePrepared)
    offset = len(gameRank) * totalTimesTextOffsetPerLetter # Offset according to length of hours text
    coverPath = config["script_path"]+config["activity_path"]+'temp/'+gameTitlePrepared+".jpg"
    stateOfFile = str(exists(coverPath))
    print("Coverpath:"+coverPath+" ==== "+stateOfFile)
    #Paste game cover image if exists
    if stateOfFile == "False":
        command='python3 '+config["script_path"]+config["activity_path"]+'downloadCoverForName.py "'+str(gameTitle)+'"'
        print("CMD:"+command)
        subprocess.check_output(command, shell=True)
        coverPath = config["script_path"]+config["activity_path"]+'temp/'+gameTitlePrepared+".jpg"
        stateOfFile = str(exists(coverPath))
        if stateOfFile == "False":
            coverPath = config["script_path"]+config["activity_path"]+'resources/NoCover.png'
    coverImage = Image.open(coverPath)
    coverImage = coverImage.convert("RGBA")
    coverImage = coverImage.resize(worstCoverSize, resample=1)
    lrCorner = (worstLrCorner[0] + index * (worstCoverWidth[0] + worstCoverPadding[0]), worstLrCorner[1] + index * (worstCoverWidth[1] + worstCoverPadding[1]))
    print("LR:"+str(lrCorner))
    img.paste(coverImage, lrCorner, coverImage)
    
    blackStar = Image.open(config["script_path"]+config["activity_path"]+'resources/0star.png')
    blackStar = blackStar.convert("RGBA")
    blackStar = blackStar.resize((20,20), Image.ANTIALIAS)
    star = Image.open(config["script_path"]+config["activity_path"]+'resources/1star.png')
    star = star.convert("RGBA")
    star = star.resize((15,15), Image.ANTIALIAS)
    fullStars = int(float(gameRank))
    fraction = float(gameRank) - int(float(gameRank))
    
    for x in range(5):
        starLrCorner = (worstStarsLrCorner[0] + index * (worstCoverWidth[0] + worstCoverPadding[0]) + x * 16 - 2, worstStarsLrCorner[1] + index * (worstCoverWidth[1] + worstCoverPadding[1]) - 2)
        img.paste(blackStar, starLrCorner, blackStar) 
        
    for i in range(fullStars):
        starLrCorner = (worstStarsLrCorner[0] + index * (worstCoverWidth[0] + worstCoverPadding[0]) + i * 16, worstStarsLrCorner[1] + index * (worstCoverWidth[1] + worstCoverPadding[1]))
        img.paste(star, starLrCorner, star) 
    if fraction > 0:
        starWidth, starHeight = star.size
        partialWidth = fraction*starWidth
        #print("Part width: "+str(partialWidth))
        partialStar = star.crop((0,0,partialWidth,15))
        partialStar.convert("RGBA")
        #print(str(starWidth)+" .... "+str(starHeight))
        starLrCorner = (worstStarsLrCorner[0] + index * (worstCoverWidth[0] + worstCoverPadding[0]) + (i + 1) * 16, worstStarsLrCorner[1] + index * (worstCoverWidth[1] + worstCoverPadding[1]))
        img.paste(partialStar, starLrCorner, partialStar)
        
    textStart = (worstCenterFirstText[0] + index * (worstCoverWidth[0] + worstCoverPadding[0]) - offset, worstCenterFirstText[1] + index * (worstCoverWidth[1] + worstCoverPadding[1]))
    imgDraw.text(textStart, gameRank, font=worstFont, fill=(255,255,255))
    
    
    
    if int(gameSlavs) > 1:
        slavText = "BY "+gameSlavs+" SLAVS"
    else:
        slavText = "BY "+gameSlavs+" SLAV"
    offset = len(slavText) * worstSmallTextOffsetPerLetter # Offset according to length of hours text
    smallTextStart = (worstCenterFirstText[0] + index * (worstCoverWidth[0] + worstCoverPadding[0]) + worstSmallTextPadding[0] - offset, worstCenterFirstText[1] + index * (worstCoverWidth[1] + worstCoverPadding[1]) + worstSmallTextPadding[1])
    
    
    imgDraw.text(smallTextStart, slavText, font=worstSmallFont, fill=(255,204,0))
    index += 1
    

####################################
# Music activity
####################################

musicActivity = open(config["script_path"]+config["activity_path"]+'output/recent-music.csv', 'r')
musicLine = musicActivity.readlines()[0]
musicHours = musicLine.split(";")[0].replace("\n","")
musicHours = float(int(musicHours)) / 60
musicHours = str(musicHours)[:4]+"h"
musicUsers = musicLine.split(";")[1].replace("\n","")
offset = len(musicHours) * musicTextOffsetPerLetter 
textStart = (musicTextCenter[0] - offset, musicTextCenter[1])
imgDraw.text(textStart, musicHours, font=musicFont, fill=(255,255,255))


if int(musicUsers) > 1:
    musicText = "BY "+musicUsers+" SLAVS"
else:
    musicText = "BY "+musicUsers+" SLAV"
offset = len(musicText) * musicSmallTextOffsetPerLetter
textStart = (musicSmallTextCenter[0] - offset, musicSmallTextCenter[1])
imgDraw.text(textStart, musicText, font=musicSmallFont, fill=(255,204,0))



####################################
# User count
####################################
mycursor.execute("SELECT memberCount FROM `trackedtimes`.`membercount` ORDER BY `date` DESC LIMIT 1;")
userCount = mycursor.fetchone()
userCount = str(userCount[0])
print("Usercount:"+userCount)

offset = len(userCount) * musicSmallTextOffsetPerLetter
textStart = (countTextCenter[0] - offset, countTextCenter[1])
imgDraw.text(textStart, userCount, font=musicFont, fill=(255,255,255))

mycursor.execute("SELECT memberCount FROM `trackedtimes`.`membercount` WHERE `date` < (date_sub(now(),INTERVAL 1 MONTH)) ORDER BY `date` DESC LIMIT 1;")
lastUserCount = mycursor.fetchone()
changeUserCount = int(userCount) - int(lastUserCount[0])
if changeUserCount < 0:
    changeUserCount = str(changeUserCount)+" SINCE LAST MONTH"
    changeColor = (195,73,73)
elif changeUserCount == 0:
    changeUserCount = "NO CHANGE SINCE LAST MONTH"
    changeColor = (255,204,0)
else:
    changeUserCount = "+"+str(changeUserCount)+" SINCE LAST MONTH"
    changeColor = (102,203,107)
    
print("Usercount:"+changeUserCount)

offset = len(changeUserCount) * musicSmallTextOffsetPerLetter
textStart = (countSmallTextCenter[0] - offset, countSmallTextCenter[1])
imgDraw.text(textStart, changeUserCount, font=musicSmallFont, fill=changeColor)

####################################
# Save
####################################

img.save(config["script_path"]+config["activity_path"]+'output/activity.png', quality=95)
