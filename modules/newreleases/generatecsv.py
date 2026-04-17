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

def extract_release_rows(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = []

    release_boxes = soup.select("a.box, div.box, li.box")
    for box in release_boxes:
        date = ""
        name = ""
        genre = ""

        genre_tag = box.find("i")
        if genre_tag:
            genre = genre_tag.get_text(" ", strip=True)

        for date_tag in box.find_all(["div", "span", "time"]):
            date_candidate = date_tag.get_text(" ", strip=True)
            if date_candidate:
                date = date_candidate
                break

        for name_tag in box.find_all(["p", "h1", "h2", "h3", "h4", "strong"]):
            name_candidate = name_tag.get_text(" ", strip=True)
            if name_candidate and name_candidate != date and name_candidate != genre:
                name = name_candidate
                break

        if not name:
            name = box.get_text(" ", strip=True)
            if date:
                name = name.replace(date, "", 1).strip()
            if genre:
                name = name.replace(genre, "", 1).strip()

        if name and genre:
            rows.append((date, name, genre))

    if rows:
        return rows

    for release in soup.find_all(class_=re.compile(r"daty-premier", re.IGNORECASE)):
        text = release.get_text(" ", strip=True)
        if text:
            chunks = [chunk.strip() for chunk in text.split("  ") if chunk.strip()]
            if len(chunks) >= 3:
                rows.append((chunks[0], chunks[1], chunks[2]))
    return rows

def saveCSV(siteurl,htmlname,csvname):
    ##Download website
    #url =  'https://www.gry-online.pl/daty-premier-gier.asp?PLA=1'
    os.makedirs(os.path.dirname(htmlname), exist_ok=True)
    os.makedirs(os.path.dirname(csvname), exist_ok=True)
    r = requests.get(siteurl, allow_redirects=True)
    open(htmlname, 'wb').write(r.content)


    #Change data to csv
    with open(htmlname, encoding="utf8", errors='ignore') as html_file:
        html = html_file.read()
    releases = extract_release_rows(html)
    release_lines = "\n".join([f"{date};{name};{genre};;" for date, name, genre in releases])
    print(release_lines)

    with open(csvname,'w') as csv:
        csv.write("Date;Name;Genre;Platform;Other\n")
        if release_lines:
            csv.write(release_lines + "\n")

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
def main():
    saveCSV('https://www.gry-online.pl/daty-premier-gier.asp?PLA=1',pathToScript+'/temp/new.html',pathToScript+'/output/new.csv')
    saveCSV('https://www.gry-online.pl/daty-premier-gier.asp?PLA=1&CZA=2',pathToScript+'/temp/month.html',pathToScript+'/output/month.csv')
    saveCSV('https://www.gry-online.pl/daty-premier-gier.asp?PLA=1&CZA=3',pathToScript+'/temp/6m.html',pathToScript+'/output/6m.csv')

    translate(pathToScript+'/output/new.csv',pathToScript+'/output/new-eng.csv')
    translate(pathToScript+'/output/month.csv',pathToScript+'/output/month-eng.csv')
    translate(pathToScript+'/output/6m.csv',pathToScript+'/output/6m-eng.csv')


if __name__ == "__main__":
    main()
