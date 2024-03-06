#!/bin/sh

rm data.json
python3 ./weather.py
sh sftp.sh
# echo Done
# aplay weather.wav

