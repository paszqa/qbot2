####################################
#
# 'getPrice' module for qqBot by Paszq
# 
# a tool generating an image with details regarding current and historical game pricing
# uses https://gg.deals to get pricing information
# uses https://static.nvidiagrid.net - to check for GeforceNOW support
# 
#   v1.0.0      2022-03-22      Paszq       first version, based on standalone script
#
#####################################
#Count execution time
from datetime import datetime
startTime = datetime.now()

#Imports
import requests #Downloading site
from bs4 import BeautifulSoup #Searching on site
import os #OS operations
import sys #OS operations
import subprocess #Running shell scripts
from difflib import SequenceMatcher #Comparing strings
from PIL import Image, ImageDraw, ImageFont, ImageFilter #Image generation
from io import BytesIO #Downloading an image from URL
import json #JSON read/write capability


#Read JSON config
json_file = open("config.json")
config = json.load(json_file)

#Basic vars
pathToScript = os.path.dirname(os.path.realpath(__file__))
prettyName = ""

#Functions
def getElementFromSite(site, elementName, elementAttributeName, elementAttribute):
    r = requests.get(site, allow_redirects=True)
    f = open(pathToScript+'/temp/temp.html', 'w+')
    f.write(str(r.content))
    f.close()
    html = open(pathToScript+'/temp/temp.html', encoding="utf8", errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    lines = soup.find_all(elementName, { elementAttributeName : elementAttribute})
    return lines

def getPrettyName(site):
    r = requests.get(site, allow_redirects=True)
    f = open(pathToScript+'/temp/prettyname.html','w+')
    f.write(str(r.content).replace("\\n","\n").replace("\\t",""))
    f.close()
    html = open(pathToScript+'/temp/prettyname.html', encoding="utf8", errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    lines = soup.find_all("h1")
    for line in lines:
        return (str(line).replace("<h1>Buy ","").replace(" PC</h1>","").replace("\\",""))


def checkGamePass(inputLines):
    if len(inputLines) > 0:
        gamePass = 0
        for line in inputLines:
            if "PC Game Pass" in str(line):
                gamePass = 1
        if gamePass == 1:
            return "GamePassPC;yes"
        else:
            return "GamePassPC;no"
    else:
        return "GamePassPC;no"

def checkGeforceNow(gameName):
    gameName = str(gameName).lower().replace(":","").replace("-"," ").replace("'","")
    #Old source - incomplete, doesn't include EA games
    #inputLines=str(subprocess.check_output("curl -s https://static.nvidiagrid.net/supported-public-game-list/locales/gfnpc-en-US.json|jq '.[] .title'|tr -d '\"' ", shell=True)).split("\\n")
    inputLines=str(subprocess.check_output("curl -s https://www.nvidia.com//content/dam/en-zz/Solutions/geforce/GeForce-experience/games/gamesdata.js| grep \"title:\"| awk -F'title: \"' '{print substr($2, 1, length($2)-3) }'", shell=True)).split("\\n")
    
    bestMatch = ""
    bestRatio = 0
    for line in inputLines:
        line = line.replace("\\xc2","").replace("\\x84","").replace("\\xa2","").replace("\\xe2","").replace("\\xae","").replace("\\x80","").replace("\\x99","").replace("'","").lower()
        s1 = SequenceMatcher(None, gameName, line)
        if s1.ratio() > bestRatio:
            bestMatch = line
            bestRatio = s1.ratio()
    #print(str(bestRatio)+" ==> "+str(bestMatch))
    inputLines=str(subprocess.check_output("curl -s https://static.nvidiagrid.net/supported-public-game-list/locales/gfnpc-en-US.json|jq '.[] .title'|tr -d '\"' ", shell=True)).split("\\n")
    for line in inputLines:
        line = line.replace("\\xc2","").replace("\\x84","").replace("\\xa2","").replace("\\xe2","").replace("\\xae","").replace("\\x80","").replace("\\x99","").replace("'","").lower()
        s1 = SequenceMatcher(None, gameName, line)
        if s1.ratio() > bestRatio:
            bestMatch = line
            bestRatio = s1.ratio()
    #print(str(bestRatio)+" ==> "+str(bestMatch))
    if bestRatio > 0.93:
        return "yes"
    else:
        return "no"

def printPrices(currentName, inputLines, siteurl):
    if len(inputLines) > 0:
        inputLines = str(inputLines[:10]).replace('</a>','\n')
        inputLines = inputLines.split("\n")
        #Get official price
        officialPrice = "-"
        foundOfficial = 0
        keyshopPrice = "-"
        gamePass = 0
        historicalLow = "1000000000"
        #Find first line with price
        x=0
        ofiNotFound = 1
        keyNotFound = 1
        hisNotFound = 2
        for line in inputLines:
            if "empty" in str(line) and "official" in str(line) and ofiNotFound == 1:
                officialPrice = "Unavailable"
                ofiNotFound = 0
            elif "empty" in str(line) and "keyshop" in str(line) and keyNotFound == 1:
                keyshopPrice = "Unavailable"
                keyNotFound = 0
            elif "empty" in str(line) and "histor" in str(line) and hisNotFound == 1:
                historicalLow = "Unavailable"
            elif "official" in str(line) and "numeric" in str(line) and ofiNotFound == 1:
                #Cut off everything before 'numerical' and after next SLASH
                if "Free" in str(line):
                    officialPrice = "Free"
                else:
                    officialPrice = str(line).split('<span class="price-inner numeric">')[1].split("\\")[0]
                ofiNotFound = 0
            elif "keyshop" in str(line) and "numeric" in str(line) and keyNotFound == 1:
                keyshopPrice = str(line).split('<span class="price-inner numeric">')[1].split("\\")[0]
                keyNotFound = 0
            elif "histor" in str(line) and "numeric" in str(line) and hisNotFound != 0:
                newCandidate = str(line).split('<span class="price-inner numeric">')[1].split("\\")[0]
                if "Free" not in str(newCandidate) and "Free" not in str(historicalLow):
                    if float(newCandidate.replace(",",".").replace("~","")) < float(historicalLow.replace(",",".").replace("~","")):
                        historicalLow = newCandidate
                else:
                    historicalLow = "Free"
                hisNotFound -= 1
            x+=1
        #-----------FINAL PRINT PART 1----------------
        csv = open(pathToScript+"/output/result.csv",'w+')
        getPrettyName(siteurl)
        csv.write("Game;"+currentName+"\n")
        csv.write(""+siteurl+"\n")
        if officialPrice != "Unavailable" and "Free" not in str(officialPrice):
            officialPrice += "€"
        if keyshopPrice != "Unavailable":
            keyshopPrice += "€"
        if historicalLow != "Unavailable":
            if "Free" not in str(historicalLow):
                if float(historicalLow.replace(",",".").replace("~","")) > 10000:
                    historicalLow = "Unavailable"
            else:
                historicalLow = "Free"
        if historicalLow != "Unavailable" and "Free" not in str(historicalLow):
            historicalLow += "€"
        #-----------FINAL PRINT PART 2--------------
        csv.write("Official;"+str(officialPrice)+"\n")
        csv.write("Keyshops;"+str(keyshopPrice)+"\n")
        csv.write("Historical;"+str(historicalLow)+"\n")
        csv.write(checkGamePass(getElementFromSite(siteurl, "span", "class", "game-info-title title no-icons"))+"\n")
        csv.write("GeforceNOW;"+str(checkGeforceNow(currentName))+"\n")#static.nvidiagrid.net/supported-public-game-list/locales/gfnpc-en-US.json", "span", "class", "game-name"))
        csv.write(getImageUrl(siteurl))
        return 0
    else:
        return 1

def getSimilarName(inputName):
    gameName=fixName(inputName)
    gameName = inputName.replace(" - ","-").replace("---","-").replace("-","+")
    siteurl='https://gg.deals/games/?title='+gameName
    r = requests.get(siteurl, allow_redirects=True)
    f = open(pathToScript+'/temp/temp.html', 'w+')
    f.write(str(r.content))
    f.close()
    html = open(pathToScript+'/temp/temp.html', encoding="utf8", errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    lines = soup.find_all("a", {"class" : "game-info-title title"})
    #"title-inner"})
    lines = str(lines).replace("<div","\n")
    lines = lines.split(">")[1].split("<")[0]
    returnArray = []
    returnArray.append(lines)
    lines = soup.find_all("a", {"class" : "full-link"})
    lines = str(lines).replace("</a>","\n").replace('<a class="full-link" href="','').split("\n")[0].split("/")[2]
    returnArray.append(lines)
    return returnArray

def buildSiteUrl(inputName):
    gameName=fixName(inputName)
    siteurl='https://gg.deals/eu/region/switch/?return=%2Fgame%2F'+str(gameName)+'%2F&showKeyshops=1'
    return siteurl

def fixName(inputName):

    gameName=str(inputName).replace(" - ","-")
    gameName=gameName.replace(" and ","")
    gameName=gameName.replace("&amp;","").replace("  "," ")
    gameName=gameName.replace("&","").replace("  "," ")
    gameName=str(gameName).replace('\'','-')
    gameName=str(gameName).replace(" ","-").replace("---","-").replace("   "," ").replace("  "," ").replace("  "," ")
    gameName=str(gameName).replace(":","").replace("/","").replace("+","")
    gameName=gameName.replace("&&amp;","").replace("  "," ")

    return gameName

def getImageUrl(siteurl):
    r = requests.get(siteurl, allow_redirects=True)
    lines = str(r.content).split("<")
    for line in lines:
        if "image-game" in str(line):
            return (str(line).split("src=")[1].split(" alt=")[0].replace('"',''))
            break;
        if "game-link-widget" in str(line):
            redirectLink = str(line).split('href="')[1].replace('">','')
            redirectRequest = requests.get(redirectLink, allow_redirects=True)
            targetUrl = str(redirectRequest.url)
            if "steampowered" in targetUrl:
                appId = str(targetUrl).split("/")[-2]
                return "https://steamcdn-a.akamaihd.net/steam/apps/"+appId+"/capsule_231x87.jpg"
                break;
        if "store.steampowered.com/app" in str(line):
            appId= str(line).split("/")[-2]
            return "https://steamcdn-a.akamaihd.net/steam/apps/"+appId+"/capsule_231x87.jpg"
            break;

def generateImage(siteurl):
    #Read data file and convert to array
    dataFile = open(pathToScript+"/output/result.csv", "r")
    line = dataFile.readlines()
    #Get file contents to easily readable variables
    gameName = str(line[0]).split(";")[1]
    prettyName = getPrettyName(siteurl)
    ggUrl = str(line[1])
    ofi = str(line[2]).split(";")[1]
    key = line[3].split(";")[1]
    his = line[4].split(";")[1]
    gamepass = line[5].split(";")[1].replace("\n","")
    gfnow = line[6].split(";")[1].replace("\n","")
    imgUrl = line[7]
    dataFile.close()
    #Setup base of image
    img = Image.open(pathToScript+'/resources/bg600x200.png')
    img = img.convert("RGB")
    imgDraw = ImageDraw.Draw(img,'RGBA')
    #Set fonts
    mainfont = ImageFont.truetype(pathToScript+"/resources/ShareTechMono-Regular.ttf", 16)
    smallfont = ImageFont.truetype(pathToScript+"/resources/ShareTechMono-Regular.ttf", 11)
    bigfont = ImageFont.truetype(pathToScript+"/resources/ShareTechMono-Regular.ttf", 20)
    #Get game image from URL and paste it
    response = requests.get(imgUrl)
    imageToPaste = Image.open(BytesIO(response.content))
    img.paste(imageToPaste, (7,7))
    imgTitle = Image.open(pathToScript+"/resources/titlebar.png")
    imgTitle = imgTitle.convert("RGBA")
    img.paste(imgTitle, (335,7), imgTitle)
    imgXgp = Image.open(pathToScript+'/resources/xgp.png')
    imgXgp = imgXgp.convert("RGBA")
    imgGfnow = Image.open(pathToScript+'/resources/gfnow.png')
    imgGfnow = imgGfnow.convert("RGBA")
    imgYes = Image.open(pathToScript+'/resources/yes.png')
    imgYes = imgYes.convert("RGBA")
    imgNo = Image.open(pathToScript+"/resources/no.png")
    imgNo = imgNo.convert("RGBA")
    img.paste(imgXgp, (355,110), imgXgp)
    #yes or no
    if str(gamepass) == "yes":
        img.paste(imgYes, (490,110), imgYes)
    else:
        img.paste(imgNo, (490,110), imgNo)
    img.paste(imgGfnow,(355,150), imgGfnow)
    if str(gfnow) == "yes":
        img.paste(imgYes, (490,150), imgYes)
    else:
        img.paste(imgNo, (490, 150), imgNo)
    #Write text  to image
    if len(prettyName) > 25:
        if len(prettyName) > 35:
            prettyName = prettyName[0:33]+"..."
        titleFont = smallfont
        margin = 13
        charwidth = 3
    elif len(prettyName) > 20:
        titleFont = mainfont
        margin = 10
        charwidth = 4
    else:
        titleFont = bigfont
        margin = 8
        charwidth = 5
    imgDraw.text((450-len(prettyName)*charwidth,5+margin), prettyName, font=titleFont, fill=(0,0,0))
    imgDraw.text((448-len(prettyName)*charwidth,3+margin), prettyName, font=titleFont, fill=(255,255,255))
    imgDraw.text((355,42), "Official:", font=mainfont, fill=(255,255,255))
    imgDraw.text((355,65), "Keyshops:", font=mainfont, fill=(255,255,255))
    imgDraw.text((355,90), "Historical low", font=smallfont, fill=(100,100,100))
    imgDraw.text((450,40), ofi, font=bigfont, fill=(150,255,5))
    imgDraw.text((450,63), key, font=bigfont, fill=(50,200,250))
    imgDraw.text((451,40), ofi, font=bigfont, fill=(150,255,5))
    imgDraw.text((451,63), key, font=bigfont, fill=(50,200,250))
    imgDraw.text((450,85), his, font=mainfont, fill=(200,200,200))
    #Save image
    executionTime=str(round(datetime.now().timestamp() - startTime.timestamp(),2))
    imgDraw.text((1,188), "Generated in ~"+str(executionTime)+" seconds by qqBot on "+str(datetime.now())[0:-7]+". "+config["image_extra_text"], font=smallfont, fill=(25,25,25))
    img.save(pathToScript+'/output/price.png', quality=95)
    urlFile = open(pathToScript+"/temp/url.temp","w+")
    urlFile.write("<"+ggUrl.replace("\n","")+">")
    if config["price_print_link"]:
        print("<"+ggUrl.replace("\n","")+">")
    urlFile.close()


#Run the script
inputName = str(sys.argv[1])
siteurl = buildSiteUrl(str(inputName))
if printPrices(str(inputName), getElementFromSite(siteurl, "a", "class", "game-price-anchor-link"), siteurl) == 1:
    prettyName = getSimilarName(str(inputName))[0]
    newName = getSimilarName(str(inputName))[1]
    siteurl = buildSiteUrl(newName)
    printPrices(prettyName, getElementFromSite(siteurl, "a", "class", "game-price-anchor-link"), siteurl)
generateImage(siteurl)
