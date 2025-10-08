#!/usr/bin/env python3
from __future__ import print_function
import time
import json

from utils import (
    Calendar,
    Weather,
    Season,
    day_stage,
    time_and_date,
    check_public_holiday,
    daily_events,
    string_replacements,
)

time.sleep(10)  # Wait for API to be ready

with open("config.json", "r") as file:
    config = json.load(file)

# Initialize Weather and Calendar with configuration
weather = Weather(location=config["weather_location"], timezone=config["timezone"])
calendar = Calendar(
    calendar_accounts=config["CALENDAR_ACCT_CREDENTIALS"],
    timezone=config["timezone"],
)
season = Season()

# Output
announcement = f"""
Good {day_stage()}.
It is {time_and_date()}.
{season.season_progress}. {check_public_holiday()}.
{weather.sunrise}.
It is {weather.current_temperature}.
Currently {weather.conditions} with {weather.wind_speed} from the {weather.wind_direction}.
{weather.rain_forecast}.
{weather.temperature_forecast}.
{calendar.all_day_events}.
{calendar.timed_events}.
Sunset will be at {weather.sunset} for {weather.hours_of_day} of daylight.
{daily_events()}.
"""

print(string_replacements(announcement))
