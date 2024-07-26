#!/usr/bin/env python
from __future__ import print_function
import requests
import json
import time
import pprint
import inflect
import datetime
from num2words import num2words

import os.path
from licence import API_KEY

import re

from google_auth import authenticate_google_calendar, get_today_upcoming_events


def extract_time(start):
    """Extract the time from the datetime string."""
    # Using regular expression to find the time part
    match = re.search(r'T(\d{2}:\d{2}):\d{2}', start)
    if match:
        return match.group(1)
    return start

#  https://www.weatherapi.com/api-explorer.aspx#forecast
def degToCompass(num):
    val=int((num/22.5)+.5)
    arr=["North","North North East","North East","East North East",
            "East","East South East", "South East", "South South East",
            "South","South South West","South West","West South West",
            "West","West North West","North West","North North West"]
    return arr[(val % 16)]

time.sleep(10)
now = datetime.datetime.now()
def get_date_str():
    # date_str = datetime.datetime.now().strftime('%A, %-d  %B')
    hour = num2words(now.strftime('%I'), lang="en")
    day = now.strftime('%A')
    date = num2words(now.strftime('%-d'), lang="en", to="ordinal")
    month = now.strftime('%B')
    return f"{hour} o clock on {day} the {date} of {month}"

def get_time_str(time, twentyfour_hour=False):
    # time = datetime.datetime.fromtimestamp(timestamp)
    time = datetime.datetime.strptime(time, "%H:%M")
    BST = 0  # 1  # make zero again when BST ends
    if twentyfour_hour:
        full_hour = (int(time.strftime('%I')) + BST)
    else:
        full_hour = (int(time.strftime('%I')) + BST) % 12
    hour = p.number_to_words(full_hour)
    minute = int(time.strftime('%M'))
    if minute == 0:
        minute = "oh clock"
    elif minute < 10:
        minute = " oh " + p.number_to_words(minute)
    else:
        minute = p.number_to_words(minute)
    string = f"{hour} {minute}"
    return string

API_DOMAIN = "http://api.weatherapi.com/v1/forecast.json"
API_URL = f"{API_DOMAIN}?key={API_KEY}&q=London&days=1&aqi=no&alerts=no"

response = requests.get(API_URL)
data = json.loads(response.text)
# pprint.pprint(data)

p = inflect.engine()

current = data['current']
date_str = get_date_str()
current_hour = int(now.strftime('%H'))
if current_hour < 12:
    day_stage = "morning"
elif current_hour < 18:
    day_stage = "afternoon"
else:
    day_stage = "evening"

current_temp = f"{p.number_to_words(int(current['temp_c']))} degrees"
if int(current['temp_c']) != int(current['feelslike_c']):
    current_temp += f" but feels like {p.number_to_words(int(current['feelslike_c']))}"

wind_speed = p.number_to_words(int(float(current['wind_kph']) * 1000 / (60 * 60)))  # km/h -> m/s
wind_direction = degToCompass(current['wind_degree'])

conditions = current['condition']['text']

today = data['forecast']['forecastday'][0]
high = p.number_to_words(f"{today['day']['maxtemp_c']:0.0f}")
low = p.number_to_words(f"{today['day']['mintemp_c']:0.0f}")
temp_forecast = f"A high of {high} and a low of {low} degrees Celcius"

sunset = get_time_str(today['astro']['sunset'].split(" ")[0])
sunset_time = datetime.datetime.strptime(today['astro']['sunset'], "%I:%M %p")
sunrise_time = datetime.datetime.strptime(today['astro']['sunrise'], "%I:%M %p")

secs_of_day = sunset_time - sunrise_time
hours_of_day, mins_of_day, _ = str(secs_of_day).split(":")
# print(hours_of_day, mins_of_day)
hours_of_day_str = p.number_to_words(hours_of_day) + " hours"
if int(mins_of_day) > 0:
    hours_of_day_str += f" and {p.number_to_words(mins_of_day)} minutes"

hourly = today['hour']

current_pop = None
rain_change = None
rain_desc = None
rain_prediction = ""
for h in hourly:
    # figure out when the rain might start or stop

    hour = datetime.datetime.fromtimestamp(h['time_epoch']).strftime('%H')
    if hour < now.strftime('%I'):
        continue
    # print(hour)
    desc = h['condition']['text']
    pop = h['will_it_rain']
    if current_pop is None:
        current_pop = pop
    if rain_change is None:
        if (current_pop == 0 and pop == 1) or (current_pop == 1 and pop == 0):
            # check if there's a rain change coming
            rain_change = hour
            rain_desc = desc
    # print(hour, desc, pop)
    if int(hour) == 23: # only look at today
        break
    # print(rain_change, h['time_epoch'], h['time'])

if rain_change is not None:
    preface = f"{rain_desc} expected at {p.number_to_words(rain_change)}"
    if int(hour) > 13:
        suffix = "hundred hours"
    else:
        suffix = "o clock"
    rain_prediction = f"{preface} {suffix}"

# get appointments
service = authenticate_google_calendar()
appointments = get_today_upcoming_events(service)

events_str = ""
for event_time, event_name in appointments.items():
    time_str = get_time_str(extract_time(event_time), True)

    if events_str == "":
        events_str = f"Your next appointment is {event_name} at {time_str}"
    else:
        events_str += f", followed by {event_name} at {time_str}"
        break


announcement = f"""
Good {day_stage}.
It is {date_str}.
It is {current_temp}.
Currently {conditions} \
        with wind speed of {wind_speed} meters per second \
        from the {wind_direction}.
{rain_prediction}.
{temp_forecast}.
{events_str}.
Sunset will be at {sunset} for {hours_of_day_str} of daylight.
"""

announcement.replace('minus', 'negative').replace('\n', ' ')

print(announcement)

