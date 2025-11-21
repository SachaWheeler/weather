#!/bin/sh

. /home/sacha/.virtualenvs/sacha/bin/activate
HOST='happy.local'
USER='happy'
# PASSWD='happy'

# cd /work/weather/
announcement=$(python3 /work/weather/weather.py)
# echo "$announcement"

ssh -T $USER@$HOST<<END_SSH
        say -v Fiona '$announcement'
END_SSH

