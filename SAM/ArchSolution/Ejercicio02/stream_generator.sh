#!/bin/sh
read -p "Enter the number of events: " events

python generate_track.py --repeat $events