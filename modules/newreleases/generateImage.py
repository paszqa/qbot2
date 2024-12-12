####################################
#
# 'newreleases - image' module for qqBot by Paszq
# 
# a tool generating a image reports with upcoming and fresh releases using 'newreleases - csv' module's output
# uses https://www.gry-online.pl to get releases information
# translates genres to english
# creates 6 reports:
#   - new.csv - new releases with original genre
#   - new-eng.csv - new releases, genres in english
#   - month.csv - releases within the next month with original genre
#   - month-eng.csv -  releases within the next month, genres in english
#   - 6m.csv - releases within the next 6 months with original genre
#   - 6m-eng.csv - releases within the next 6 months, genres in english
#
#   v1.0.0      2022-03-22      Paszq       first version, based on standalone script
#
#####################################
#Count execution time
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
img = Image.open(pathToScript+'/resources/background.png')
img = img.convert("RGB")
#Choose fonts
largefnt = ImageFont.truetype(pathToScript+'/resources/ShareTechMono-Regular.ttf', 18)
fnt = ImageFont.truetype(pathToScript+'/resources/ShareTechMono-Regular.ttf', 13)
smallfnt = ImageFont.truetype(pathToScript+'/resources/ShareTechMono-Regular.ttf',11)
#Settings
rowHeight=14
firstRowStart=18

#Draw background
d = ImageDraw.Draw(img,'RGBA')

#Get text from file
which=sys.argv[1]
if which == "month":
    filename = "/output/month-eng.png"
    titletext = "Games releasing soon"
    f = open(pathToScript+'/output/month-eng.csv','r')
    indent = 160
elif which == "6m":
    filename = "/output/6m-eng.png"
    f = open(pathToScript+'/output/6m-eng.csv','r')
    titletext = "Games releasing within 6 months"
    indent = 130
else:
    filename = "/output/new-eng.png"
    f = open(pathToScript+'/output/new-eng.csv','r')
    titletext = "Fresh releases"
    indent = 170


#Analyze each line from the file
rowNumber = 0
for row in f:
    if rowNumber > 25:
        break;
    rowSplit = row.split(";")
    if rowNumber == 0:
        currentColor = (122,122,122) #grey
    elif rowNumber > 0 and rowNumber < 5:
        currentColor = (49, 199, 38) #green
    elif rowNumber > 4 and rowNumber < 8:
        currentColor = (169, 199, 38) #light green
    elif rowNumber > 7 and rowNumber < 12:
        currentColor = (199, 194, 38) # yellowish
    else:
        currentColor = (199, 140, 38) #orange
    d.text((10,firstRowStart+rowHeight*rowNumber), rowSplit[0], font=fnt, fill=currentColor)
    if rowNumber % 2:
        d.rectangle([(0,(firstRowStart+rowHeight*rowNumber)+2),(530,firstRowStart+rowHeight*(rowNumber+1)+1)], fill=(0,0,0,57))
    d.text((100,firstRowStart+rowHeight*rowNumber), rowSplit[1][0:45], font=fnt, fill=currentColor)
    d.text((450,firstRowStart+rowHeight*rowNumber), rowSplit[2], font=fnt, fill=currentColor) 

    rowNumber += 1

#Add title
d.text((indent,3), titletext, font=largefnt, fill=(255,255,255))

#Add execution time info
executionTime=str(round(datetime.now().timestamp() - startTime.timestamp(),2))
print("EX:"+executionTime+" NOW:"+str(datetime.now()))
d.text((0,390), "Generated in ~"+str(executionTime)+" seconds by qqBot on "+str(datetime.now())[0:-7]+". "+config["image_extra_text"], font=smallfnt, fill=(20,20,20))
#Save for the glory of Slav Squat Squad
img.save(pathToScript+filename)
