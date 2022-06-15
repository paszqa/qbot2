####################################
#
# 'steam - image' module for qqBot by Paszq
#
# generates a pretty image with contents of sumUp's CSV file
#
####################################
#Imports
import os
from PIL import Image, ImageDraw, ImageFont

pathToScript = os.path.dirname(os.path.realpath(__file__))

#Choose size and color
#img = Image.new('RGB', (550, 400), color = (73, 109, 137))
img = Image.open(pathToScript+'/resources/background.png')
img = img.convert("RGB")
#Choose fonts
fnt = ImageFont.truetype(pathToScript+'/resources/ShareTechMono-Regular.ttf', 15)
#Settings
rowHeight=15
firstRowStart=3

#Draw background
d = ImageDraw.Draw(img,'RGBA')

#Get text from file
f = open(pathToScript+'/output/most-played-total.csv','r')

#Analyze each line from the file
rowNumber = 0
for row in f:
    rowSplit = row.split(";")
    if rowNumber == 0:
        currentColor = (122,122,122) #grey
    elif rowNumber == 1:
        currentColor = (49, 199, 38) #green
    elif rowNumber == 2:
        currentColor = (169, 199, 38) #light green
    elif rowNumber == 3:
        currentColor = (199, 194, 38) # yellowish
    else:
        currentColor = (199, 140, 38) #orange
    d.text((10,firstRowStart+rowHeight*rowNumber), rowSplit[0], font=fnt, fill=currentColor)
    if rowNumber % 2:
        d.rectangle([(0,(firstRowStart+rowHeight*rowNumber)+2),(530,firstRowStart+rowHeight*(rowNumber+1)+1)], fill=(0,0,0,57))
    d.text((50,firstRowStart+rowHeight*rowNumber), rowSplit[1][0:45], font=fnt, fill=currentColor)
    d.text((400,firstRowStart+rowHeight*rowNumber), rowSplit[2], font=fnt, fill=currentColor)
    d.text((470+min(1,rowNumber)*15,firstRowStart+rowHeight*rowNumber), rowSplit[3], font=fnt, fill=currentColor)
    rowNumber += 1
#Save for the glory of Slav Squat Squad
img.save(pathToScript+'/output/most-played-total.png')
