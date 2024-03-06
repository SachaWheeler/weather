import requests
import json
import time
import pprint
import inflect
import datetime
from num2words import num2words
# from TTS.api import TTS
import os.path
from licence import API_KEY
import subprocess


host = 'happy.local'
user = 'happy'
passwd = 'happy'
cmd = 'say -v Samantha'

announcement = """Good morning. It is seven o clock on Wednesday the sixth of March.  It is seven degrees but feels like six.  Currently Moderate rain with wind speed of two meters per second from the North East.  Moderate rain expected at eight hundred hours.  a high of nine and a low of six degrees Celcius.  Sunset will be at five forty-nine for eleven hours and thirteen minutes of daylight.  """
command = f"ssh {user}@{host} {cmd} '{announcement}'"
print(command)
subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        ).communicate()

