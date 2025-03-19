#!/bin/bash

while true; do
	TASKS=$(curl -s http://192.168.1.250:5000/get_tasks)
	echo "$TASKS" | while read LINE; do
		DELAY=$(echo "$LINE" | cut -d";" -f1)
		CMD=$(echo "$LINE" | cut -d";" -f2)
		test -z "$LINE"  -o -z "$CMD" -o -z "$DELAY" && continue
		( sleep $DELAY; $CMD ) &
	done
	sleep 60
done
