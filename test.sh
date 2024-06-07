#!/usr/bin/bash
HOST='happy.local'
USER='happy'
PASSWD='happy'

announcement="Good morning. It is seven o clock on Wednesday the sixth of March.  It is seven degrees but feels like six."
my_array=("Daniel" "Kate" "Serena" "Agnes" "Alex" "Allison" "Ava" "Bruce" "Fred" "Junior" "Kathy" "Nicky" "Princess" "Ralph" "Susan" "Tom" "Vicky" "Victoria" "Albert" "Bahh" "Bells" "Boing" "Bubbles" "Cellos" "Deranged" "Hysterical" "Pipe Organ" "Trinoids" "Whisper" "Zarvox")

# Loop through the array
for string in "${my_array[@]}"; do
    echo "$string"
        ssh $USER@$HOST<<END_SSH
        say -v $string '$announcement'
END_SSH

done

