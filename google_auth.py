from __future__ import print_function
import datetime
import os
import re
import requests
import pytz
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from num2words import num2words
from licence import API_KEY

# Define the scope for the Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
ACCT_CREDENTIALS = {
    "sacha@jftwines.com": "bibo-calendar.json",
    "sacha@sachawheeler.com": "sacha-calendar.json",
}

london_tz = pytz.timezone('Europe/London')
now = datetime.datetime.now(london_tz)

def authenticate_google_calendar(account=None):
    """Authenticates with the Google Calendar API using a service account."""
    # print(account)
    if account is None:
        return None
    else:
        SERVICE_ACCOUNT_FILE = ACCT_CREDENTIALS[account]

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)
    return service, account

def get_today_upcoming_events(service, account=None):
    # print(f"geting events for {account}")
    # Define the time zone for London, England
    london_tz = pytz.timezone('Europe/London')

    # Get the current time in London, England
    now = datetime.datetime.now(london_tz)
    now_iso = now.isoformat()

    # Calculate the end of the day in London, England
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    end_of_day_iso = end_of_day.isoformat()

    # print('Getting today\'s upcoming events')
    events_result = service.events().list(
            calendarId=account,
            timeMin=now_iso,
            timeMax=end_of_day_iso, singleEvents=True,
            orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return None
    upcoming_events = {}
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        # print(start, event['summary'])
        upcoming_events[start] = event['summary']
    return upcoming_events

def is_date_time(pair):
        key, value = pair
        return "T" in key

def is_not_date_time(pair):
        return not is_date_time(pair)

def get_calendar_events(accounts=None):
    if accounts is None:
        return None

    count = 0
    for acct in accounts:
        # print(acct)
        count += 1
        service, account = authenticate_google_calendar(acct)
        events = get_today_upcoming_events(service, account)

        time_events = dict(filter(is_date_time, events.items())) if events else {}
        date_events = dict(filter(is_not_date_time, events.items())) if events else {}

        if count == 1:
            combined_date = list(date_events.values()) if date_events else []
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
    if now.hour <= 9:
        length = len(combined_date)
        if length > 0:
            date_events_str = f"Events today include "
            count =0
            for event_name in combined_date:
                count += 1
                date_events_str += f"{event_name}"
                if length > count:
                    date_events_str += ", and "

    time_events_str = ""
    for event_time, event_name in sorted_times.items():
        time_str = get_time_str(extract_time(event_time), True)

        if time_events_str == "":
            time_events_str = f"Your next appointment is {event_name} at {time_str}"
        else:
            time_events_str += f", followed by {event_name} at {time_str}"
            break
    if time_events_str == "":
        time_events_str = "You have no further appointments today"

    return date_events_str, time_events_str

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

def extract_time(start):
    match = re.search(r'T(\d{2}:\d{2}):\d{2}', start)
    if match:
        return match.group(1)
    return start

def get_weather_data():
    API_DOMAIN = "http://api.weatherapi.com/v1/forecast.json"
    API_URL = f"{API_DOMAIN}?key={API_KEY}&q=London&days=1&aqi=no&alerts=no"

    response = requests.get(API_URL)
    data = json.loads(response.text)
    return data

def get_greeting(current):
    current_hour = int(now.strftime('%H'))
    if current_hour < 12:
        day_stage = "morning"
    elif current_hour < 18:
        day_stage = "afternoon"
    else:
        day_stage = "evening"

    hour = num2words(now.strftime('%I'), lang="en")
    day = now.strftime('%A')
    date = num2words(now.strftime('%-d'), lang="en", to="ordinal")
    month = now.strftime('%B')
    date_str = f"{hour} o clock on {day} the {date} of {month}"
    return day_stage, date_str

def get_current_conditions(current):
    current_temp = f"{num2words(int(current['temp_c']), lang='en')} degrees"
    if int(current['temp_c']) != int(current['feelslike_c']):
        current_temp += f" but feels like {num2words(int(current['feelslike_c']), lang='en')}"

    conditions = current['condition']['text']

    return current_temp, conditions

def degToCompass(num):
    val=int((num/22.5)+.5)
    arr=["North","North North East","North East","East North East",
            "East","East South East", "South East", "South South East",
            "South","South South West","South West","West South West",
            "West","West North West","North West","North North West"]
    return arr[(val % 16)]

def get_wind(current):
    #  https://www.weatherapi.com/api-explorer.aspx#forecast
    wind_speed = num2words(int(float(current['wind_kph']) * 1000 / (60 * 60)), lang="en")  # km/h ->
    wind_direction = degToCompass(current['wind_degree'])
    return wind_speed, wind_direction

def get_temp_forecast(forecast):
    today = forecast
    high = num2words(f"{today['day']['maxtemp_c']:0.0f}", lang="en")
    low = num2words(f"{today['day']['mintemp_c']:0.0f}", lang="en")
    temp_forecast = f"A high of {high} and a low of {low} degrees Celcius"
    return temp_forecast

def get_sunset_hours(astro):
    sunset = get_time_str(astro['sunset'].split(" ")[0])
    sunset_time = datetime.datetime.strptime(astro['sunset'], "%I:%M %p")
    sunrise_time = datetime.datetime.strptime(astro['sunrise'], "%I:%M %p")

    secs_of_day = sunset_time - sunrise_time
    hours_of_day, mins_of_day, _ = str(secs_of_day).split(":")
    hours_of_day_str = num2words(hours_of_day, lang="en") + " hours"
    if int(mins_of_day) > 0:
        hours_of_day_str += f" and {num2words(mins_of_day, lang='en')} minutes"
    return sunset, hours_of_day_str

def get_rain_prediction(hourly):
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
        return rain_prediction


