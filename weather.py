#!/usr/bin/env python3
from __future__ import print_function
import time
import pytz

from utils import (
    Calendar,
    Weather,
    Season,
    get_greeting,
    check_public_holiday,
    get_daily_events,
)

time.sleep(10)

# Get current time and date
greeting_stage, formatted_date = get_greeting()

# Set timezone to London
london_tz = pytz.timezone("Europe/London")
gmail_accounts = ["sacha@jftwines.com", "sacha@sachawheeler.com"]

# Initialize Calendar with required Gmail accounts
calendar = Calendar(calendar_accounts=gmail_accounts, timezone=london_tz)
all_day_events_str, timed_events_str = calendar.get_calendar_events()

# Get Weather
weather = Weather(location="London")

# Current conditions
current_temperature, conditions = weather.get_current_conditions()
wind_speed_str, wind_direction = weather.get_wind()

# Forecast
temp_forecast = weather.get_temperature_forecast()
sunrise, sunset, hours_of_day_str = weather.get_sunset_hours()
rain_forecast_str = weather.get_rain_prediction()

# Season progress
season = Season()
season_progress_str = season.get_season_progress()

# Other events
hourly_events_str = get_daily_events()

# Public holidays
public_holiday_str = check_public_holiday()

# Output
announcement = (
    f"""

    Good {greeting_stage}.
    It is {formatted_date}.
    {season_progress_str}. {public_holiday_str}.
    {sunrise}.
    It is {current_temperature}.
    Currently {conditions} with {wind_speed_str} from the {wind_direction}.
    {rain_forecast_str}.
    {temp_forecast}.
    {all_day_events_str}.
    {timed_events_str}.
    Sunset will be at {sunset} for {hours_of_day_str} of daylight.
    {hourly_events_str}.

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
