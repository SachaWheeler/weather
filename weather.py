#!/usr/bin/env python3
from __future__ import print_function
import time
import pytz
from datetime import datetime

from utils import (
    Calendar,
    Weather,
    get_greeting,
    Season,
    check_public_holiday,
    get_daily_events,
)

time.sleep(10)

# Get current time and date
day_stage, date_str = get_greeting()

# Set timezone to London
london_tz = pytz.timezone("Europe/London")
gmail_accounts = ["sacha@jftwines.com", "sacha@sachawheeler.com"]

# Initialize Calendar object with required Gmail accounts
calendar = Calendar(accounts=gmail_accounts, timezone=london_tz)
date_events_str, time_events_str = calendar.get_calendar_events()

# Get Weather
weather = Weather(location="London")

# Current conditions
current_temp, conditions = weather.get_current_conditions()
wind_speed, wind_direction = weather.get_wind()

# Forecast
temp_forecast = weather.get_temp_forecast()
sunrise, sunset, hours_of_day_str = weather.get_sunset_hours()
rain_prediction = weather.get_rain_prediction()

# Other events
daily_events_str = get_daily_events()

# Season progress
season = Season()
season_str = season.season_progress()

# Public holidays
holiday_str = check_public_holiday()

# Output
announcement = (
    f"""

    Good {day_stage}.
    It is {date_str}.
    {season_str}. {holiday_str}.
    {sunrise}.
    It is {current_temp}.
    Currently {conditions} with {wind_speed} from the {wind_direction}.
    {rain_prediction}.
    {temp_forecast}.
    {date_events_str}.
    {time_events_str}.
    Sunset will be at {sunset} for {hours_of_day_str} of daylight.
    {daily_events_str}.

""".replace("minus", "negative")
    .replace(
        "    ",
        "",  # left padding
    )
    .replace(
        "\n.",
        "",  # blank lines with '.'s
    )
    .replace(
        " .",
        "",  # double '.'s
    )
    .replace(
        "'",
        "",  # remove things that might break the shell script "'"
    )
    .lstrip()
    .rstrip()
)  # lines at start and end

print(announcement)
