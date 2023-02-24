#!/bin/sh

. /home/sacha/virtual_envs/sacha/bin/activate
rm data.json
python3 ./weather.py
sh sftp.sh
# echo Done
# aplay weather.wav

