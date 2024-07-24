
from datetime import datetime
startTime = datetime.now()

#Imports
import os
from os.path import exists
import sys
from PIL import Image, ImageDraw, ImageFont
import json #JSON read/write capability

#Settings
pathToScript = os.path.dirname(os.path.realpath(__file__))

#Read JSON config
if exists("../../config.json"):
    json_file = open("../../config.json")
elif exists("config.json"):
    json_file = open("config.json")
else:
    json_file = open(pathToScript+"/defaults.json")

config = json.load(json_file)


#Choose size and color
#img = Image.new('RGB', (550, 400), color = (73, 109, 137))
img = Image.open(pathToScript+'/resources/sss_background.png')
img = img.convert("RGB") 

largefnt = ImageFont.truetype(pathToScript+'/resources/ShareTechMono-Regular.ttf', 18)
fnt = ImageFont.truetype(pathToScript+'/resources/ShareTechMono-Regular.ttf', 13)
smallfnt = ImageFont.truetype(pathToScript+'/resources/ShareTechMono-Regular.ttf',11)
currentColor = (199, 194, 38) # yellowish
supergreen = (0,255,0)
green = (40,215,0)
kindagreen = (70,175,0)
yellow = (175,175,0)
red = (245,75,0)
grey = (112,112,102)
kindawhite = (175,175,154)
white = (255,255,244)
#Settings
rowHeight=33
firstRowStart=38

#Draw background
d = ImageDraw.Draw(img,'RGBA')
f = open(pathToScript+'/output/listresult','r')
filename = "/output/listresult.png"
#Analyze each line from the file
#listresult.write(gameName+";"+ggLink+";"+ofiPrice+";"+keyPrice+";"+hisPrice+";"+xgp+";"+gfn+";"+steamlink+";"+news+";"+reviews+";"+release_date+"\n")
rowNumber = 0
#Generate columns
#d.rectangle([(10,(firstRowStart-1)),(170,firstRowStart+50)], fill=(255,255,255,37)])
d.rectangle([(10+187,firstRowStart-1),(10+187+55,firstRowStart+755)],fill=(255,255,255,17))
d.rectangle([(390,firstRowStart-1),(390+224,firstRowStart+755)],fill=(255,255,255,27))
for row in f:
    columnOffset = 0
    #columnWidth = 50
    if rowNumber > 25:
        break;
    rowSplit = row.split(";")
    rowOffset = 0
    if rowSplit[11].strip() == "EA":
        d.text((10+columnOffset+2,firstRowStart+rowHeight*rowNumber+2), "EA", font=largefnt, fill=(255,0,0))
    columnOffset += 30
    if len(rowSplit[0]) > 22:
        rowSplit[0] = rowSplit[0][:19]+"..."
    d.text((10+columnOffset+2,firstRowStart+rowHeight*rowNumber+2), rowSplit[0][:22], font=fnt, fill=(0,0,0))
    d.text((10+columnOffset+1,firstRowStart+rowHeight*rowNumber+0), rowSplit[0][:22], font=fnt, fill=(0,0,0))
    d.text((10+columnOffset+0,firstRowStart+rowHeight*rowNumber+2), rowSplit[0][:22], font=fnt, fill=(0,0,0))
    d.text((10+columnOffset,firstRowStart+rowHeight*rowNumber), rowSplit[0][:22], font=fnt, fill=white)
    columnOffset += 160
    if rowSplit[2] == "Unavailable":
        rowSplit[2] = "n/a"
    d.text((10+columnOffset,firstRowStart+rowHeight*rowNumber), rowSplit[2], font=fnt, fill=kindagreen)
    columnOffset += 60
    if rowSplit[3] == "Unavailable":
        rowSplit[3] = "n/a"
    #d.text((10+columnOffset,firstRowStart+rowHeight*rowNumber), rowSplit[3], font=fnt, fill=yellow)
    columnOffset += 10
    if rowSplit[4] == "Unavailable":
        rowSplit[4] = "n/a"
    d.text((10+columnOffset,firstRowStart+rowHeight*rowNumber), rowSplit[4], font=fnt, fill=grey)
    columnOffset += 76
    if rowSplit[5] == "yes":
        rowSplit[5] = "XGP"
        d.text((10+columnOffset,firstRowStart+rowHeight*rowNumber), rowSplit[5], font=fnt, fill=currentColor)
    else:
        d.text((10+columnOffset,firstRowStart+rowHeight*rowNumber), rowSplit[5], font=fnt, fill=grey)
    columnOffset += 14
    #d.text((10+columnOffset,firstRowStart+rowHeight*rowNumber), rowSplit[6], font=fnt, fill=currentColor)
    columnOffset += 50 
    d.text((10+30,firstRowStart+rowHeight*rowNumber+14), rowSplit[8], font=smallfnt, fill=kindawhite)
    columnOffset += 0
    if "Overwhelmingly Positive" in rowSplit[9]:
        reviewColor = supergreen
    elif "Very Positive" in rowSplit[9]:
        reviewColor = green
    elif "Mostly Positive" in rowSplit[9]:
        reviewColor = kindagreen
    elif "Mixed" in rowSplit[9]:
        reviewColor = yellow
    else:
        reviewColor = red
    d.text((10+columnOffset,firstRowStart+rowHeight*rowNumber), rowSplit[9].split("(")[0], font=fnt, fill=reviewColor)
    columnOffset += 210
    d.text((10+columnOffset,firstRowStart+rowHeight*rowNumber), rowSplit[10], font=fnt, fill=yellow)
    if rowNumber % 2:
        d.rectangle([(10,(firstRowStart+rowHeight*rowNumber)-1),(770,firstRowStart+rowHeight*(rowNumber+1)-4)], fill=(255,255,255,17))
    rowNumber += 1
#Save for the glory of Slav Squat Squad
img.save(pathToScript+filename)