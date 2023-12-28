####################################
#
# year-recap' module for qqBot by Paszq
#
# Steam CSV Transform
# analyzes CSV files, sorts them and translates to human-readable format
#
####################################

import mysql.connector
import subprocess
import os
import calendar
from os.path import exists
import json #JSON read/write capability
import pandas #Sorting

#Read JSON config
if exists("../../config.json"):
    json_file = open("../../config.json")
elif exists("config.json"):
    json_file = open("config.json")
else:
    print("No config.json found")
    exit(2)
config = json.load(json_file)

#Settings
pathToScript = os.path.dirname(os.path.realpath(__file__))
year = 2022

#Check if script isn't running already
def FileCheck(fn):
    try:
      open(fn, "r")
      return 1
    except IOError:
      return 0
fileresult = FileCheck(config["script_path"]+config["year_recap_path"]+"/temp/transformCsv.tmp")
if fileresult == 1:
    print("Script already running")
    quit()
else:
    print("No script running")
    g = open(config["script_path"]+config["year_recap_path"]+"/temp/transformCsv.tmp", "w+")
    g.write("busy")
    g.close()

#DB Connection
mydb = mysql.connector.connect(
          host=config["dbhost"],
            user=config["dbuser"],
              password=config["dbpass"],
                database=config["dbname"],
                )

mycursor = mydb.cursor()

###########
# Functions
###########
def cleanUpName(gameName):        #Clean up the name
    #originalGameName = str(gameName).replace("\n","")
    gameName=str(gameName).replace(" - Steam Charts","")
    gameName=gameName.replace("Steam Charts - ","")
    gameName=gameName.replace("\\n","")
    gameName=gameName.replace("<title>","")
    gameName=gameName.replace("</title>","")
    gameName=gameName.replace("\t","")
    gameName = gameName.replace("\"","")
    gameName = gameName.replace("\\'","'") #fix apostrophe
    gameName = gameName.replace("\\xe2\\x84\\xa2","®")
    gameName = gameName.replace("\\xe2\\x80\\x99","'")
    gameName = gameName.replace("\\xc2","").replace("\\xae","").replace("\\xe2","")
    gameName = gameName.replace("\\n\'","")
    gameName = gameName.replace("\n","")
    #log(str(datetime.now())+" [INFO] Cleaned up name from:"+originalGameName+" ==> "+gameName+"\n")
    return gameName

###########
# Magic
###########

csvList=subprocess.check_output('ls '+pathToScript+'/output/'+str(year)+"/", shell=True)
csvList=csvList.decode().split("\n")
#print(csvList) 
for file in csvList:
    if file != "":
        #subprocess.check_output('mkdir -p '+pathToScript+'/output/'+str(year)+"/"+file+, shell=True)
        s = open(pathToScript+'/output/'+str(year)+"/"+file,'r')
        t = []
        for i in range(1,13):
            t.append(open(pathToScript+'/output/'+str(year)+"-transformed/"+file+"_"+str(i),'w+'))
        #print(str(t));
        #for line in s:
            #elements = line.split(";")
            ##month = elements[2]
            #id = elements[3]
            #gameName=subprocess.check_output('python3 '+config["script_path"]+config["gamename_path"]+'/outputNameFromId.py '+str(id), shell=True)
            #gameName = gameName.decode().replace("\n","")
            ##gameName = cleanUpName(gameName)
            #hours = elements[4]
            #stringToWrite = str(month)+";"+str(gameName)+";"+str(hours)
            #print("[DEBUG] "+stringToWrite)
            #t[int(month)-1].write(stringToWrite)
        #print(str(file))
        
        r = []
        for i in range(1,13):
            r.append(open(pathToScript+'/output/'+str(year)+"-transformed/"+file+"_"+str(i),'r'))
        tsorted = []
        for i in range(1,13):
            tsorted.append(open(pathToScript+'/output/'+str(year)+"-transformed/"+file+"_"+str(i)+"_sorted",'w+'))
        for csvFile in r:
            csvData = pandas.read_csv(csvFile, sep = ';')
            # displaying unsorted data frame
            print("\nBefore sorting:")
            print(csvData)
            # sort data frame
            csvData.sort_values(csvData.columns[3], axis=0, ascending=[False], inplace=True)
            #csvData.sort_values(csvData.columns[2], axis=0, ascending=[False], inplace=True)
            # displaying sorted data frame
            print("\nAfter sorting:")
            print(csvData)
    
os.remove(config["script_path"]+config["year_recap_path"]+"/temp/transformCsv.tmp")
for i in range(1,13):
    t[i].close()
s.close()