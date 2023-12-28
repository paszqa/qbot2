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
totalPlayingCorner = (945,195)
totalPlayingTextSize = 70

#TOP GAMES
topGamesCorner = (490,275)
topGamesCoverSize = (90,120)
topGamesCoverPadding = (110,0)
topGamesCoverText = (topGamesCorner[0],int(topGamesCorner[1]+0.55*topGamesCoverSize[1]))
topGamesTextSize = 25
topGamesTextOffsetPerLetter = topGamesTextSize / 3.5
topGamesCenterFirstText = (topGamesCorner[0]+0.53 * topGamesCoverSize[0], topGamesCorner[1] + topGamesCoverSize[1])

#TOP PLAYERS
discordBlockImageLrCorner = (560,440)
discordPlayerImageLrCorner = (discordBlockImageLrCorner[0] + 15, discordBlockImageLrCorner[1] + 15)
discordPlayerImageSize = (75,75)
discordPlayerImagePadding = (0, 130)
discordPlayerNameLrCorner = (discordPlayerImageLrCorner[0], discordPlayerImageLrCorner[1] + discordPlayerImageSize[1] + 10)
discordCoverSize = (60,80)
discordCoverLrCorner = (700, 455)
discordCoverPadding = (87,0)


#####################################
#   Fonts
#####################################
yearFont = ImageFont.truetype(config["script_path"]+config["year_recap_path"]+'resources/kremlin.ttf',yearTextSize)
totalFont = ImageFont.truetype(config["script_path"]+config["year_recap_path"]+'resources/kremlin.ttf',totalPlayingTextSize)
hoursFont = ImageFont.truetype(config["script_path"]+config["activity_path"]+'resources/ShareTechMono-Regular.ttf',topGamesTextSize)

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
imgDraw.text(textStart, str(year), font=yearFont, fill=(255,0,0))
####################################
# Total played hours
####################################
totalTimePlayed = open(config["script_path"]+config["year_recap_path"]+'output/'+str(year)+'/totalHoursPlayed.csv', 'r')
for line in totalTimePlayed:
    print(str(line))
    textStart = (totalPlayingCorner)
    imgDraw.text(textStart, str(line) + " HOURS", font=totalFont, fill=(255,0,0))

####################################
# Top games
####################################
topGames = open(config["script_path"]+config["year_recap_path"]+'output/'+str(year)+'/topGames.csv', 'r')
index = 0
for line in topGames:
    gameTitle = line.split(";")[0]
    gameTimeHours = line.split(";")[1] + "h"
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
        if len(rowSplit) > 1:
            gameCoverUrl = rowSplit[1]
        print("Looking for cover for game: "+gameTitlePrepared)
        coverPath = config["script_path"]+config["activity_path"]+'temp/'+gameTitlePrepared+".jpg"
        print("Cover path to best tested: "+coverPath)
        if not exists(coverPath) or os.path.getsize(coverPath) < 50:
            print ("Cover not found.........")
            coverPath = config["script_path"]+config["activity_path"]+'resources/NoCover.png'
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
        gameIndex += 1
    index += 1
####################################
# Save the image.
####################################
img.save(config["script_path"]+config["year_recap_path"]+'output/'+str(year)+'/recap.png', quality=95)