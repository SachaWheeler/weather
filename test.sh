#!/bin/sh
HOST='happy.local'
USER='happy'
PASSWD='happy'

announcement="testing testing testing"

ssh $USER@$HOST<<END_SSH
        say -v Samantha '$announcement'
END_SSH

