#!/usr/bin/env python
from __future__ import print_function
import time

from utils import (
    authenticate_google_calendar, get_today_upcoming_events,
    is_date_time, is_not_date_time,
    get_calendar_events, get_time_str,
    get_weather_data, get_greeting, get_current_conditions,
    get_wind, get_temp_forecast, get_sunset_hours,
    get_rain_prediction, get_season
)

time.sleep(10)

# get Weather
weather_data = get_weather_data()

# Current
current = weather_data['current']

day_stage, date_str                         = get_greeting(current)
current_temp, conditions                    = get_current_conditions(current)
wind_speed, wind_direction                  = get_wind(current)

# Forecast
today = weather_data['forecast']['forecastday'][0]

temp_forecast                               = get_temp_forecast(today)
sunrise, sunset, hours_of_day_str           = get_sunset_hours(today['astro'])
rain_prediction                             = get_rain_prediction(today['hour'])

# Calendar appointments
gmail_accounts = ['sacha@jftwines.com', 'sacha@sachawheeler.com']
date_events_str, time_events_str            = get_calendar_events(gmail_accounts)

# Seasons
season_str                                  = get_season()

# Output
announcement = f"""

    Good {day_stage}.
    It is {date_str}.
    {season_str}.
    {sunrise}.
    It is {current_temp}.
    Currently {conditions} with {wind_speed} from the {wind_direction}.
    {rain_prediction}.
    {temp_forecast}.
    {date_events_str}.
    {time_events_str}.
    Sunset will be at {sunset} for {hours_of_day_str} of daylight.

""".replace('minus', 'negative'
).replace('    ', ''        # left padding
).replace('\n.', ''         # blank lines with '.'s
).replace('\'', ''          # remove things that might break the shell script "'"
).lstrip().rstrip()         # lines at start and end

print(announcement)

