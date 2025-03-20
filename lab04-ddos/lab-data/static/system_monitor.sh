#!/bin/bash

while true; do
	HOSTNAME=$(hostname)
	RESULT=$(curl -s http://192.168.1.250:5000/register -X POST -H 'Content-type: application/json' -d '{"name":"'$HOSTNAME'"}')
	if [ "$RESULT" = "OK" ]; then
		break
	fi
	sleep 5
done

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
