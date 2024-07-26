#!/bin/sh

. /home/sacha/.virtualenvs/sacha/bin/activate
HOST='happy.local'
USER='happy'
PASSWD='happy'

announcement=$(python3 /home/sacha/work/weather/weather.py)
# echo "$announcement"

ssh $USER@$HOST<<END_SSH
        say -v Fiona '$announcement'
END_SSH

