#!/usr/bin/env python3
from __future__ import print_function
import time

from utils import (
    authenticate_google_calendar, get_today_upcoming_events,
    is_date_time, is_not_date_time,
    get_calendar_events, get_time_str,
    get_weather_data, get_greeting, get_current_conditions,
    get_wind, get_temp_forecast, get_sunset_hours,
    get_rain_prediction,
    check_public_holiday, season_progress
)

season_str                              = season_progress()

print(season_str)

