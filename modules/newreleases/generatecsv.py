####################################
#
# 'newreleases - csv' module for qqBot by Paszq
# 
# a tool generating a CSV reports with upcoming and fresh releases
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
from bs4 import BeautifulSoup
import requests
import re
import os

pathToScript = os.path.dirname(os.path.realpath(__file__))

###########################################################
#
# GET SITE, SAVE AS HTML, GENERATE SIMPLE CSV
#
###########################################################

def saveCSV(siteurl,htmlname,csvname):
    ##Download website
    #url =  'https://www.gry-online.pl/daty-premier-gier.asp?PLA=1'
    r = requests.get(siteurl, allow_redirects=True)
    open(htmlname, 'wb').write(r.content)


    #Change data to csv
    html = open(htmlname, encoding="utf8", errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    credits = soup.find_all("div", {"class" : "daty-premier-2017"})
    credits = re.sub(r'<a class="box"(.*)">\n', '', str(credits))
    credits = re.sub(r'<div>','', str(credits))
    credits = re.sub(r' <i>',';',credits)
    credits = re.sub(r'</i>','',credits)
    credits = re.sub(r'<div data-cnt(.*)">','', str(credits))
    credits = re.sub(r'</div>\n',';', str(credits))
    credits = re.sub(r';</a>','', credits)
    credits = re.sub(r'<div class="clr">;</div>]','',credits)
    credits = re.sub(r'\[<div class="daty-premier-2017">\n','', credits)
    credits = re.sub(r'<span(.*)</span>\n','', credits)
    credits = re.sub(r'\n</a>\n','',credits)
    credits = re.sub(r'\n</p>\n','',credits)
    credits = re.sub(r'</p>','',credits)
    credits = re.sub(r'<p (.*)>','',credits)
    credits = re.sub(r'\t','',credits)
    credits = re.sub(r'&amp;','&',credits) #fix ampersand
    print (credits)

    csv = open(csvname,'w')
    csv.write("Date;Name;Genre;Platform;Other\n")
    csv.write(credits)
    csv.close()


saveCSV('https://www.gry-online.pl/daty-premier-gier.asp?PLA=1',pathToScript+'/temp/new.html',pathToScript+'/output/new.csv')
saveCSV('https://www.gry-online.pl/daty-premier-gier.asp?PLA=1&CZA=2',pathToScript+'/temp/month.html',pathToScript+'/output/month.csv')
saveCSV('https://www.gry-online.pl/daty-premier-gier.asp?PLA=1&CZA=3',pathToScript+'/temp/6m.html',pathToScript+'/output/6m.csv')

##############################################################
#
# GENERATE SHORT TRANSLATED FILE
#
##############################################################

def translate(sourcecsv,outputcsv):
    f = open(outputcsv,'w')
    with open(sourcecsv) as file:
        array = file.readlines()
        for line in array[0:40]:
            lineSplit = line.split(';')
            # Date transform
            dateSplit = lineSplit[0].split(' ')
            dateFinal = ""
            if len(dateSplit) > 1:
                if len(dateSplit) > 2:
                    dateFinal += dateSplit[0] + " ";

                if "sty" in dateSplit[-2]:
                    dateFinal += "Jan"
                elif "lut" in dateSplit[-2]:
                    dateFinal += "Feb"
                elif "mar" in dateSplit[-2]:
                    dateFinal += "Mar"
                elif "kwi" in dateSplit[-2]:
                    dateFinal += "Apr"
                elif "maj" in dateSplit[-2]:
                    dateFinal += "May"
                elif "czer" in dateSplit[-2]:
                    dateFinal += "Jun"
                elif "lip" in dateSplit[-2]:
                    dateFinal += "Jul"
                elif "sier" in dateSplit[-2]:
                    dateFinal += "Aug"
                elif "wrze" in dateSplit[-2]:
                    dateFinal += "Sep"
                elif "ernik" in dateSplit[-2]:
                    dateFinal += "Oct"
                elif "list" in dateSplit[-2]:
                    dateFinal += "Nov"
                elif "grud" in dateSplit[-2]:
                    dateFinal += "Dec"
                dateFinal += " "+dateSplit[-1]
            else:
                dateFinal = dateSplit[-1]
            #
            # Genre transform
            genre = lineSplit[2];
            if "Zrcz" in genre:
                genre = "Action"
            elif "czno" in genre:
                genre = "Action"
            elif "Bija" in genre:
                genre = "Fighting"
            elif "Fabul" in genre:
                genre = "RPG"
            elif "Symu" in genre:
                genre = "Sim"
            elif "Wyci" in genre:
                genre = "Racing"
            elif "cigi" in genre:
                genre = "Racing"
            elif "Akcj" in genre:
                genre = "Action"
            elif "Przyg" in genre:
                genre = "Adventure"
            elif "Strat" in genre:
                genre = "Strategy"
            elif "Sport" in genre:
                genre = "Sports"
            elif "Logic" in genre:
                genre = "Puzzle"

            # Write to file
            f.write(dateFinal+";"+lineSplit[1]+";"+genre+"\n")
            print(dateFinal+";"+lineSplit[1]+";"+genre)
    print("=================================================")
    f.close()
translate(pathToScript+'/output/new.csv',pathToScript+'/output/new-eng.csv')
translate(pathToScript+'/output/month.csv',pathToScript+'/output/month-eng.csv')
translate(pathToScript+'/output/6m.csv',pathToScript+'/output/6m-eng.csv')


