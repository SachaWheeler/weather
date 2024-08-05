#!/usr/bin/env python
from __future__ import print_function
import requests
import json
import time
import pprint
import datetime
from num2words import num2words
import re
import os.path
import pytz

from licence import API_KEY
from google_auth import (authenticate_google_calendar, get_today_upcoming_events,
        is_date_time, is_not_date_time)


def extract_time(start):
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
london_tz = pytz.timezone('Europe/London')
now = datetime.datetime.now(london_tz)
def get_date_str():
    hour = num2words(now.strftime('%I'), lang="en")
    day = now.strftime('%A')
    date = num2words(now.strftime('%-d'), lang="en", to="ordinal")
    month = now.strftime('%B')
    return f"{hour} o clock on {day} the {date} of {month}"

def get_time_str(time, twentyfour_hour=False):
    time = datetime.datetime.strptime(time, "%H:%M")
    BST = 0  # 1  # make zero again when BST ends
    if twentyfour_hour:
        full_hour = (int(time.strftime('%I')) + BST)
    else:
        full_hour = (int(time.strftime('%I')) + BST) % 12
    # hour = p.number_to_words(full_hour)
    hour = num2words(full_hour, lang="en")
    minute = int(time.strftime('%M'))
    if minute == 0:
        minute = "oh clock"
    elif minute < 10:
        minute = " oh " + num2words(minute, lang="en")
    else:
        minute = num2words(minute, lang="en")
    string = f"{hour} {minute}"
    return string

# get Weather
API_DOMAIN = "http://api.weatherapi.com/v1/forecast.json"
API_URL = f"{API_DOMAIN}?key={API_KEY}&q=London&days=1&aqi=no&alerts=no"

response = requests.get(API_URL)
data = json.loads(response.text)

current = data['current']
date_str = get_date_str()
current_hour = int(now.strftime('%H'))
if current_hour < 12:
    day_stage = "morning"
elif current_hour < 18:
    day_stage = "afternoon"
else:
    day_stage = "evening"

# current_temp
current_temp = f"{num2words(int(current['temp_c']), lang='en')} degrees"
if int(current['temp_c']) != int(current['feelslike_c']):
    current_temp += f" but feels like {num2words(int(current['feelslike_c']), lang='en')}"

# Wind speed
wind_speed = num2words(int(float(current['wind_kph']) * 1000 / (60 * 60)), lang="en")  # km/h -> m/s
wind_direction = degToCompass(current['wind_degree'])

conditions = current['condition']['text']

# Temp forecast
today = data['forecast']['forecastday'][0]
high = num2words(f"{today['day']['maxtemp_c']:0.0f}", lang="en")
low = num2words(f"{today['day']['mintemp_c']:0.0f}", lang="en")
temp_forecast = f"A high of {high} and a low of {low} degrees Celcius"

# Sunset
sunset = get_time_str(today['astro']['sunset'].split(" ")[0])
sunset_time = datetime.datetime.strptime(today['astro']['sunset'], "%I:%M %p")
sunrise_time = datetime.datetime.strptime(today['astro']['sunrise'], "%I:%M %p")

secs_of_day = sunset_time - sunrise_time
hours_of_day, mins_of_day, _ = str(secs_of_day).split(":")
hours_of_day_str = num2words(hours_of_day, lang="en") + " hours"
if int(mins_of_day) > 0:
    hours_of_day_str += f" and {num2words(mins_of_day, lang='en')} minutes"

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

# Rain
if rain_change is not None:
    preface = f"{rain_desc} expected at {num2words(rain_change, lang='en')}"
    if int(hour) > 13:
        suffix = "hundred hours"
    else:
        suffix = "o clock"
    rain_prediction = f"{preface} {suffix}"


# get Calendar appointments
try:
    count = 0
    for acct in ['sacha@jftwines.com', 'sacha@sachawheeler.com']:
        count += 1
        service, account = authenticate_google_calendar(acct)
        events = get_today_upcoming_events(service, account)

        time_events = dict(filter(is_date_time, events.items()))
        date_events = dict(filter(is_not_date_time, events.items()))


        if count == 1:
            combined_date = list(date_events.values())
            combined_time = time_events
        else:
            combined_date.extend(date_events.values())

            for time, event in time_events.items():
                if time in combined_time:
                    combined_time[time] += f", and {event}"
                else:
                    combined_time[time] = event

            sorted_times = dict(
                    sorted(combined_time.items(),
                        key=lambda item: datetime.datetime.fromisoformat(item[0]))
            )


    date_events_str = ""
    length = len(combined_date)
    if length > 0:
        date_events_str = f"Events today include "
        count =0
        for event_name in combined_date:
            event_name = event_name.replace("\'","")

            count += 1
            date_events_str += f"{event_name}"
            if length > count:
                date_events_str += " and "

    time_events_str = ""
    for event_time, event_name in sorted_times.items():
        event_name = event_name.replace("\'"," ")
        time_str = get_time_str(extract_time(event_time), True)

        if time_events_str == "":
            time_events_str = f"Your next appointment is {event_name} at {time_str}"
        else:
            time_events_str += f", followed by {event_name} at {time_str}"
            break
except Exception as e:
    # print(e)
    time_events_str = "Cannot get calendar appointments"
    pass


announcement = f"""
Good {day_stage}.
It is {date_str}.
It is {current_temp}.
Currently {conditions} \
with wind speed of {wind_speed} meters per second \
from the {wind_direction}.
{rain_prediction}.
{temp_forecast}.
{date_events_str}.
{time_events_str}.
Sunset will be at {sunset} for {hours_of_day_str} of daylight.
"""

announcement.replace('minus', 'negative').replace('\n', ' ')

print(announcement)

