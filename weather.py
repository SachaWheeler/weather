#!/usr/bin/env python
from __future__ import print_function
import time

from google_auth import (
    authenticate_google_calendar, get_today_upcoming_events,
    is_date_time, is_not_date_time,
    get_calendar_events, get_time_str,
    get_weather_data, get_greeting, get_current_conditions,
    get_wind, get_temp_forecast, get_sunset_hours,
    get_rain_prediction,
)

time.sleep(10)

# get Weather
weather_data = get_weather_data()

current = weather_data['current']
day_stage, date_str = get_greeting(current)
current_temp, conditions = get_current_conditions(current)
wind_speed, wind_direction = get_wind(current)

today = weather_data['forecast']['forecastday'][0]
temp_forecast = get_temp_forecast(today)
sunset, hours_of_day_str = get_sunset_hours(today['astro'])
rain_prediction = get_rain_prediction(today['hour'])


# get Calendar appointments
gmail_accounts = ['sacha@jftwines.com', 'sacha@sachawheeler.com']
date_events_str, time_events_str = get_calendar_events(gmail_accounts)

announcement = (
    f"Good {day_stage}. "
    f"It is {date_str}. "
    f"It is {current_temp}. "
    f"Currently {conditions} "
    f"with wind speed of {wind_speed} meters per second from the {wind_direction}. "
    f"{rain_prediction}. "
    f"{temp_forecast}. "
    f"{date_events_str}. "
    f"{time_events_str}. "
    f"Sunset will be at {sunset} for {hours_of_day_str} of daylight. "
    )

announcement = announcement.replace(
        'minus', 'negative'
    ).replace( '\n.', ''
    ).replace('\'', ''
    ).lstrip().rstrip()

print(announcement)

