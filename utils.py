from __future__ import print_function
from datetime import datetime, timedelta
from dateutil import parser
import os
import sys
import re
import requests
import pytz
import json
import time

# pip install --upgrade google-api-python-client

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
now = datetime.now(london_tz)
today = now.strftime('%Y-%m-%d')

LAST_RUN_FILE = "./last_run_date.txt"


def is_first_run_today():
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, 'r') as file:
            last_run_date = file.read().strip()

        # Check if today's date is different from the last run date
        if today != last_run_date:
            # Update the last run date
            with open(LAST_RUN_FILE, 'w') as file:
                file.write(today)
            return True
        else:
            return False
    else:
        # If the file doesn't exist, it's the first run ever
        with open(LAST_RUN_FILE, 'w') as file:
            file.write(today)
        return True

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
        return "arse"

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
                    # if there are two simultaneous events
                    combined_time[time] += f", and {event}"
                else:
                    combined_time[time] = event

            sorted_times = dict(
                    sorted(combined_time.items(),
                        # key=lambda item: datetime.datetime.fromisoformat(item[0]))
                        key=lambda item: parser.isoparse(item[0]))
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
    if time_events_str == "" and now.hour <= 12:
        time_events_str = "No appointments"

    return date_events_str, time_events_str

def get_time_str(time, twentyfour_hour=False):
    time = datetime.strptime(time, "%H:%M")
    BST = 0  # 1  # make zero again when BST ends
    if twentyfour_hour:
        full_hour = (int(time.strftime('%I')) + BST)
    else:
        full_hour = (int(time.strftime('%I')) + BST) % 12

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


def is_file_outdated(file_path, max_age_minutes=20):
    if not os.path.exists(file_path):
        return True  # File doesn't exist, so it's outdated

    # Get the file's last modification time
    file_mtime = os.path.getmtime(file_path)

    # Get the current time and compare it with the file's mtime
    current_time = time.time()
    max_age_seconds = max_age_minutes * 60
    return current_time - file_mtime > max_age_seconds


def get_weather_data():
    API_DOMAIN = "http://api.weatherapi.com/v1/forecast.json"
    API_URL = f"{API_DOMAIN}?key={API_KEY}&q=London&days=1&aqi=no&alerts=no"

    json_file_path = 'fetched_data.json'
    if is_file_outdated(json_file_path):
        response = requests.get(API_URL)
        json_data = json.loads(response.text)
        with open(json_file_path, 'w') as f:
            json.dump(json_data, f)
    else:
        with open(json_file_path, 'r') as f:
            json_data = json.load(f)

    return json_data

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
    wind_speed = int(float(current['wind_kph']) * 1000 / (60 * 60))
    wind_speed_str = num2words(wind_speed, lang="en")
    wind_direction = degToCompass(current['wind_degree'])
    return f" wind speed of {wind_speed_str} meter{'s' if wind_speed > 1 else ''} per second", wind_direction

def get_temp_forecast(forecast):
    high = num2words(f"{forecast['day']['maxtemp_c']:0.0f}", lang="en")
    low = int(forecast['day']['mintemp_c'])
    low_str = num2words(low, lang="en")
    temp_forecast = f"A high of {high} and a low of {low_str} degree{'s' if low > 1 else ''} Celcius"
    return temp_forecast

def get_sunset_hours(astro):
    sunset = get_time_str(astro['sunset'].split(" ")[0])
    sunset_time = datetime.strptime(astro['sunset'], "%I:%M %p")
    sunrise_time = datetime.strptime(astro['sunrise'], "%I:%M %p")

    sunrise = ""
    sunrise_today = sunrise_time.replace(year=now.year, month=now.month, day=now.day, tzinfo=london_tz)
    if sunrise_today.time() > now.time():  # sunrise has yet to happen - use time as year is not set
        time_difference = sunrise_today - now

        hours = time_difference.seconds // 3600
        minutes = (time_difference.seconds // 60) % 60

        sunrise = "Sunrise wil be in"
        if hours > 0:
            sunrise += f" {num2words(hours)} hour{'s' if hours > 1 else ''}"
        if hours > 0 and minutes > 0:
            sunrise += " and"
        if minutes > 0:
            sunrise += f" {num2words(minutes)} minute{'s' if minutes > 1 else ''}"

    secs_of_day = sunset_time - sunrise_time
    hours_of_day, mins_of_day, _ = str(secs_of_day).split(":")
    hours_of_day_str = num2words(hours_of_day, lang="en") + " hours"
    if int(mins_of_day) > 0:
        hours_of_day_str += f" and {num2words(mins_of_day, lang='en')} minutes"
    return sunrise, sunset, hours_of_day_str

def get_rain_prediction(hourly):
    current_pop = None
    rain_change = None
    rain_desc = None
    rain_prediction = ""
    for h in hourly:
        # figure out when the rain might start or stop

        hour = datetime.fromtimestamp(h['time_epoch']).strftime('%H')
        if hour < now.strftime('%H'):
            continue

        desc = h['condition']['text']
        pop = h['will_it_rain']
        if current_pop is None:
            current_pop = pop
        if rain_change is None:
            if (current_pop == 0 and pop == 1) or (current_pop == 1 and pop == 0):
                # check if there's a rain change coming
                rain_change = hour
                rain_desc = desc

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

def get_season():
    """
    if not is_first_run_today():
        return ""
    """
    season_str = ""
    year = now.year
    season_dates = {
        "Winter": datetime(year, 3, 20, tzinfo=london_tz),
        "Spring": datetime(year, 6, 21, tzinfo=london_tz),
        "Summer": datetime(year, 9, 23, tzinfo=london_tz),
        "Autmnn": datetime(year, 12, 21, tzinfo=london_tz),
        "Winter": datetime(year + 1, 3, 20, tzinfo=london_tz),
    }

    # Check if the next season is in the current or next year
    for season, end_date in season_dates.items():
        if end_date > now:
            days_until_next_season = (end_date - now).days
            break
    else:
        # If no more seasons are left this year, calculate days until the first season of next year
        season = "Spring"
        next_year = now.year + 1
        spring_start_next_year = get_season_dates(next_year)["Spring"]
        days_until_next_season = (spring_start_next_year - now).days

    total_days = 91

    days_passed = total_days - days_until_next_season
    proportion_passed = days_passed / total_days if total_days > 0 else 0

    # Define fractions of the form n/d where n < d, and d ∈ {2, 3, 4, 5}
    fractions = [(n, d) for d in range(2, 9) for n in range(1, d)]

    # Calculate which fraction is closest to the proportion of days passed
    closest_fraction = min(fractions, key=lambda frac: abs((frac[0] / frac[1]) - proportion_passed))

    # Extract numerator and denominator of the closest fraction
    closest_numerator, closest_denominator = closest_fraction
    numerator = num2words(closest_numerator)
    denominator = "half" if closest_denominator == 2 else num2words(closest_denominator, lang="en", to="ordinal")

    # Calculate days left in the season
    days_left = total_days - days_passed
    progress = "into" if closest_numerator / closest_denominator < 0.5 else "through"

    # Handle if the season has ended
    if days_left <= 0:
        return f"{season} is over. Total duration: {total_days} days"

    return (f"We are {num2words(days_passed)} day{'s' if days_passed != 1 else '' }, "
            f"or {numerator} {denominator}{'s' if closest_numerator > 1 else '' } "
            f"of the way {progress} {season}, "
            f"with {num2words(days_left)} day{'s' if days_left != 1 else '' } left")


def check_public_holiday():
    with open("bank-holidays.json", 'r') as file:
        data = json.load(file)

    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)

    days = {today: "Today",
            tomorrow: "Tomorrow"
            }

    # Assuming we check only 'england-and-wales', modify for other regions if needed
    holidays = data.get('england-and-wales', {}).get('events', [])

    found_holiday = False
    for holiday in holidays:
        holiday_date = datetime.strptime(holiday['date'], "%Y-%m-%d").date()
        if today <= holiday_date <= next_week:
            # print(f"Upcoming Public Holiday: {holiday['title']} on {holiday['date']}")
            found_holiday = True
            break

    if found_holiday:
        if holiday_date in days:
            day = days[holiday_date]
        else:
            day = holiday_date.strftime('%A')

        return f"{day} is {holiday['title']}"
    else:
        return ""








