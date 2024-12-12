import subprocess
import json #JSON read/write capability
from os.path import exists
import os

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
pathToScript = os.path.dirname(os.path.realpath(__file__))

listresult = open(pathToScript+'/output/listresult','w')


# Open the 'list' file and iterate over each line
with open(pathToScript+'/list', 'r') as file:
    for line in file:
        print("=================="+line.strip()+"===============")
        # Remove leading and trailing whitespaces from each line
        line = line.strip()

        # Run the printPrice.py script with the current line as an argument
        print("Running subprocess: python3 "+pathToScript+"/printPrice.py "+line+"\n")
        subprocess.run(['python3', pathToScript+'/printPrice.py', line])
        
        # Print the content of the output/result.csv file
        with open('output/result.csv', 'r') as result_file:
            #result_content = result_file.read()
            result_lines = result_file.readlines()
            #print(f"Content of result.csv after processing {line}:\n{str(result_lines)}")
            gameName = result_lines[0].strip()
            ggLink = result_lines[1].strip()
            ofiPrice = result_lines[2].strip()
            keyPrice = result_lines[3].strip()
            hisPrice = result_lines[4].strip()
            xgp = result_lines[5].strip()
            gfn = result_lines[6].strip()
            steamlink = result_lines[7].strip()
            news = result_lines[8].strip()
            reviews = result_lines[9].strip()
            release_date = result_lines[10].strip()
            early = result_lines[12].strip()
            print("game:"+gameName)
            print("ggLink:"+ggLink)
            print("ofiPrice:"+ofiPrice)
            print("keyPrice:"+keyPrice)
            print("hisPrice:"+hisPrice)
            print("xgp:"+xgp)
            print("gfn:"+gfn)
            print("steamlink:"+steamlink)
            print("news:"+news)
            print("reviews:"+reviews)
            print("release:"+release_date)
            print("early:"+early)
            if len(news) > 115:
                news = news[:112]+"..."
            listresult.write(gameName+";"+ggLink+";"+ofiPrice+";"+keyPrice+";"+hisPrice+";"+xgp+";"+gfn+";"+steamlink+";"+news[:115]+";"+reviews+";"+release_date+";"+early+"\n")
            #for result_line in enumerate(result_lines):
            #    print(f"Line {index}: {result_line.strip()}")
