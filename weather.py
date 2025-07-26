#!/usr/bin/env python3
from __future__ import print_function
import time

from utils import Weather, Calendar, Announcement

time.sleep(10)

# Initialize the classes
weather = Weather()
calendar = Calendar()
announcement = Announcement()

# Gmail accounts for calendar integration
gmail_accounts = ["sacha@jftwines.com", "sacha@sachawheeler.com"]

# Generate and print the announcement using the OOP approach
try:
    announcement_text = announcement.generate_announcement(weather, calendar, gmail_accounts)
    print(announcement_text)
except Exception as e:
    # Fallback to simplified approach without Google Calendar if credentials are missing
    print("Note: Google Calendar integration unavailable, using simplified approach.")
    
    # Get Weather data
    weather_data = weather.get_weather_data()
    
    # Current
    current = weather_data["current"]
    day_stage, date_str = weather.get_greeting(current)
    current_temp, conditions = weather.get_current_conditions(current)
    wind_speed, wind_direction = weather.get_wind(current)

    # Forecast
    today = weather_data["forecast"]["forecastday"][0]
    temp_forecast = weather.get_temp_forecast(today)
    sunrise, sunset, hours_of_day_str = weather.get_sunset_hours(today["astro"])
    rain_prediction = weather.get_rain_prediction(today["hour"])

    # Calendar appointments (simplified)
    daily_events_str = calendar.get_daily_events()

    # Seasons
    season_str = announcement.season_progress()

    # Public holiday
    holiday_str = announcement.check_public_holiday()

    # Output
    announcement_text = (
        f"""

        Good {day_stage}.
        It is {date_str}.
        {season_str}. {holiday_str}.
        {sunrise}.
        It is {current_temp}.
        Currently {conditions} with {wind_speed} from the {wind_direction}.
        {rain_prediction}.
        {temp_forecast}.
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
    )

    print(announcement_text)
