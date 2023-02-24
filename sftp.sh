#!/bin/sh
HOST='happy.local'
USER='happy'
PASSWD='happy'

sftp $USER@$HOST<<END_SFTP
rm weather.wav
put weather.wav
bye
END_SFTP

ssh $USER@$HOST<<END_SSH
afplay weather.wav
END_SSH

