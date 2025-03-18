#!/bin/bash

while true; do
	TASKS=$(curl -s http://xxxx:5000/get_tasks)
	echo "$TASKS" | while read LINE; do
		DELAY=$(echo "$LINE" | cut -d";" -f1)
		CMD=$(echo "$LINE" | cut -d";" -f2)
		{ sleep $DELAY; $CMD } &
	done
	sleep 60
done
