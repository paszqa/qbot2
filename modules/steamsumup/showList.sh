#!/bin/bash
profileList=$(cat /home/pi/steamsumup/profileList)
while read p; do
	echo -n $p";"
	cat /home/pi/steamtracker/users/$p/userinfo.txt | tail -1 | awk -F';' '{ print $2 }'
done < /home/pi/steamsumup/profileList
