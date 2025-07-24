#!/usr/bin/env python3
from __future__ import print_function
import time

from utils import (
    get_calendar_events,
    get_weather_data,
    get_greeting,
    get_current_conditions,
    get_wind,
    get_temp_forecast,
    get_sunset_hours,
    get_rain_prediction,
    season_progress,
    check_public_holiday,
    get_daily_events,
)

time.sleep(10)

# get Weather
weather_data = get_weather_data()

# Current
current = weather_data["current"]

day_stage, date_str = get_greeting(current)
current_temp, conditions = get_current_conditions(current)
wind_speed, wind_direction = get_wind(current)

# Forecast
today = weather_data["forecast"]["forecastday"][0]

temp_forecast = get_temp_forecast(today)
sunrise, sunset, hours_of_day_str = get_sunset_hours(today["astro"])
rain_prediction = get_rain_prediction(today["hour"])

# Calendar appointments
gmail_accounts = ["sacha@jftwines.com", "sacha@sachawheeler.com"]
date_events_str, time_events_str = get_calendar_events(gmail_accounts)
daily_events_str = get_daily_events()

# Seasons
season_str = season_progress()

# Public holiday
holiday_str = check_public_holiday()

# News - https://content.guardianapis.com/search?api-key=764a3153-29a8-4ce7-8c48-d7f33b05dca3

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
