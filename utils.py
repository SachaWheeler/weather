from __future__ import print_function
from datetime import datetime, timedelta, date
from dateutil import parser
import os
import re
import requests
import pytz
import json
import time

from google.oauth2 import service_account
from googleapiclient.discovery import build
from num2words import num2words
from licence import API_KEY as WEATHER_API_KEY

DEFAULT_TIMEZONE = pytz.timezone("Europe/London")
with open("config.json", "r") as file:
    config = json.load(file)
now = datetime.now(pytz.timezone(config["timezone"])) if "timezone" in config else datetime.now(DEFAULT_TIMEZONE)

LAST_RUN_FILE = "./last_run_date.txt"


class Calendar:
    def __init__(
        self,
        calendar_accounts=None,
        cache_file="calendar_cache.json",
        cache_expiry_minutes=30,
        timezone=None,
    ):
        self.calendar_accounts = calendar_accounts.keys()
        self.CALENDAR_ACCT_CREDENTIALS = calendar_accounts
        self.timezone = pytz.timezone(timezone) if timezone else DEFAULT_TIMEZONE
        self.now = datetime.now(self.timezone)
        self.current_date = self.now.strftime("%Y-%m-%d")
        self.sorted_event_times = {}
        self.cache_file = cache_file
        self.cache_expiry_minutes = cache_expiry_minutes

    # Define the scope for the Google Calendar API
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    def is_cache_outdated(self):
        """Check if the cache file exists and is still valid."""
        if not os.path.exists(self.cache_file):
            return True  # Cache does not exist

        # Get the last modification time of the cache file
        file_mtime = os.path.getmtime(self.cache_file)
        last_modified = datetime.fromtimestamp(file_mtime, self.timezone)
        expiry_time = last_modified + timedelta(minutes=self.cache_expiry_minutes)

        return (
            self.now > expiry_time
        )  # Cache is outdated if the current time is past the expiry time

    def load_cached_data(self):
        """Load data from the cache file."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as file:
                return json.load(file)
        return {}

    def save_to_cache(self, data):
        """Save data to the cache file."""
        with open(self.cache_file, "w") as file:
            json.dump(data, file)

    def is_first_run_today(self):
        if os.path.exists(LAST_RUN_FILE):
            with open(LAST_RUN_FILE, "r") as file:
                last_run_date = file.read().strip()

            # Check if today's date is different from the last run date
            if self.current_date != last_run_date:
                # Update the last run date
                with open(LAST_RUN_FILE, "w") as file:
                    file.write(self.current_date)
                return True
            else:
                return False
        else:
            # If the file doesn't exist, it's the first run ever
            with open(LAST_RUN_FILE, "w") as file:
                file.write(self.current_date)
            return True

    def authenticate_google_calendar(self, account=None):
        """Authenticates with the Google Calendar API using a service account."""
        if account is None:
            return None
        else:
            SERVICE_ACCOUNT_FILE = self.CALENDAR_ACCT_CREDENTIALS[account]

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=self.SCOPES
        )

        service = build("calendar", "v3", credentials=credentials)
        return service, account

    def get_today_upcoming_events(self, service, account=None):
        now_iso = self.now.isoformat()

        # Calculate the end of the day in London, England
        end_of_day = self.now.replace(hour=23, minute=59, second=59, microsecond=999999)
        end_of_day_iso = end_of_day.isoformat()

        events_result = (
            service.events()
            .list(
                calendarId=account,
                timeMin=now_iso,
                timeMax=end_of_day_iso,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return None
        upcoming_events = {}
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            upcoming_events[start] = event["summary"]
        return upcoming_events

    def is_date_time(self, pair):
        key, value = pair
        return "T" in key

    def is_not_date_time(self, pair):
        return not self.is_date_time(pair)

    def get_calendar_events(self):
        if not self.is_cache_outdated():
            # Load data from the cache
            cached_data = self.load_cached_data()
            return cached_data.get("date_events_str", ""), cached_data.get(
                "time_events_str", ""
            )

        if self.calendar_accounts is None:
            return "No accounts provided"

        count = 0
        all_day_events = []
        timed_events = {}

        for acct in self.calendar_accounts:
            count += 1
            service, account = self.authenticate_google_calendar(acct)
            events = self.get_today_upcoming_events(service, account)

            time_events = (
                dict(filter(self.is_date_time, events.items())) if events else {}
            )
            date_events = (
                dict(filter(self.is_not_date_time, events.items())) if events else {}
            )

            if count == 1:
                all_day_events = list(date_events.values()) if date_events else []
                timed_events = time_events
            else:
                all_day_events.extend(date_events.values())

                for time, event in time_events.items():
                    if time in timed_events:
                        timed_events[time] += f", and {event}"
                    else:
                        timed_events[time] = event

                self.sorted_event_times = dict(
                    sorted(
                        timed_events.items(),
                        key=lambda item: parser.isoparse(item[0]),
                    )
                )

        all_day_events_str = ""
        if self.now.hour <= 9:
            length = len(all_day_events)
            if length > 0:
                all_day_events_str = "Events today include "
                count = 0
                for event_name in all_day_events:
                    count += 1
                    all_day_events_str += f"{event_name}"
                    if length > count:
                        all_day_events_str += ", and "

        timed_events_str = ""
        for event_time, event_name in self.sorted_event_times.items():
            time_str = get_time_str(self.extract_time(event_time), True)

            if timed_events_str == "":
                timed_events_str = (
                    f"Your next appointment is {event_name} at {time_str}"
                )
            else:
                timed_events_str += f", followed by {event_name} at {time_str}"
                break
        if timed_events_str == "" and self.now.hour <= 12:
            timed_events_str = "No appointments"

        # Save the events to cache
        cached_data = {
            "date_events_str": all_day_events_str,
            "time_events_str": timed_events_str,
        }
        self.save_to_cache(cached_data)

        return all_day_events_str, timed_events_str

    def extract_time(self, start):
        match = re.search(r"T(\d{2}:\d{2}):\d{2}", start)
        if match:
            return match.group(1)
        return start


# Weather class encapsulating all weather-related functionality
class Weather:
    def __init__(
        self,
        location="London",
        cache_file="weather_cache.json",
        cache_expiry_minutes=30,
        timezone=None,
    ):
        self.location = location
        self.api_key = WEATHER_API_KEY
        self.weather_api_url = "http://api.weatherapi.com/v1/forecast.json"
        self.cache_file = cache_file
        self.cache_expiry_minutes = cache_expiry_minutes
        self.timezone = pytz.timezone(timezone) if timezone else DEFAULT_TIMEZONE
        self.weather_data = self.get_weather_data()

    def is_cache_outdated(self):
        """Check if the cache file exists and is still valid."""
        if not os.path.exists(self.cache_file):
            return True  # Cache does not exist

        # Get the last modification time of the cache file
        file_mtime = os.path.getmtime(self.cache_file)
        last_modified = datetime.fromtimestamp(file_mtime, self.timezone)
        expiry_time = last_modified + timedelta(minutes=self.cache_expiry_minutes)

        return (
            datetime.now(self.timezone) > expiry_time
        )  # Cache is outdated if the current time is past the expiry time

    def load_cached_data(self):
        """Load data from the cache file."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as file:
                return json.load(file)
        return {}

    def save_to_cache(self, data):
        """Save data to the cache file."""
        with open(self.cache_file, "w") as file:
            json.dump(data, file)

    def is_file_outdated(self, file_path, max_age_minutes=20):
        if not os.path.exists(file_path):
            return True  # File doesn't exist, so it's outdated

        # Get the file's last modification time
        file_mtime = os.path.getmtime(file_path)

        # Get the current time and compare it with the file's mtime
        current_time = time.time()
        max_age_seconds = max_age_minutes * 60
        return current_time - file_mtime > max_age_seconds

    def get_weather_data(self):
        """Fetch weather data from the API or load from cache if available."""
        if not self.is_cache_outdated():
            # Load data from the cache
            return self.load_cached_data()

        # If cache is outdated, fetch new data from the API
        api_url = f"{self.weather_api_url}?key={self.api_key}&q={self.location}&days=1&aqi=no&alerts=no"

        response = requests.get(api_url)
        weather_data = json.loads(response.text)

        # Save the fetched data to the cache
        self.save_to_cache(weather_data)

        return weather_data

    def get_current_conditions(self, current=None):
        if current is None:
            current = self.weather_data["current"]

        temp_c = int(current["temp_c"])
        current_temp = (
            f"{num2words(temp_c, lang='en')} degree{'' if temp_c == 1 else 's'}"
        )
        if int(current["temp_c"]) != int(current["feelslike_c"]):
            current_temp += (
                f" but feels like {num2words(int(current['feelslike_c']), lang='en')}"
            )

        conditions = current["condition"]["text"]

        return current_temp, conditions

    def deg_to_compass(self, num):
        val = int((num / 22.5) + 0.5)
        arr = [
            "North",
            "North North East",
            "North East",
            "East North East",
            "East",
            "East South East",
            "South East",
            "South South East",
            "South",
            "South South West",
            "South West",
            "West South West",
            "West",
            "West North West",
            "North West",
            "North North West",
        ]
        return arr[(val % 16)]

    def get_wind(self, current=None):
        if current is None:
            current = self.weather_data["current"]

        wind_speed = int(float(current["wind_kph"]) * 1000 / (60 * 60))
        wind_speed_str = num2words(wind_speed, lang="en")
        wind_direction = self.deg_to_compass(current["wind_degree"])
        return (
            f" wind speed of {wind_speed_str} meter{'s' if wind_speed > 1 else ''} per second",
            wind_direction,
        )

    def get_temperature_forecast(self, forecast_data=None):
        if forecast_data is None:
            forecast_data = self.weather_data["forecast"]["forecastday"][0]

        high = num2words(f"{forecast_data['day']['maxtemp_c']:0.0f}", lang="en")
        low = int(forecast_data["day"]["mintemp_c"])
        low_str = num2words(low, lang="en")
        temperature_forecast = f"A high of {high} and a low of {low_str} degree{'s' if low > 1 else ''} Celcius"
        return temperature_forecast

    def get_sunset_hours(self, astro_data=None):
        if astro_data is None:
            astro_data = self.weather_data["forecast"]["forecastday"][0]["astro"]

        sunset = get_time_str(astro_data["sunset"].split(" ")[0])
        sunset_time = datetime.strptime(astro_data["sunset"], "%I:%M %p")
        sunrise_time = datetime.strptime(astro_data["sunrise"], "%I:%M %p")

        sunrise = ""
        sunrise_today = sunrise_time.replace(
            year=now.year, month=now.month, day=now.day, tzinfo=self.timezone
        )
        if (
            sunrise_today.time() > now.time()
        ):  # sunrise has yet to happen - use time as year is not set
            time_difference = sunrise_today - now

            hours = time_difference.seconds // 3600
            minutes = (time_difference.seconds // 60) % 60

            sunrise = "Sunrise will be in"
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

    def get_rain_prediction(self, forecast=None):
        if forecast is None:
            forecast = self.weather_data["forecast"]["forecastday"][0]
        hourly = forecast["hour"]

        current_pop = None
        rain_change = None
        rain_desc = None
        rain_prediction = ""
        for h in hourly:
            # figure out when the rain might start or stop

            hour = datetime.fromtimestamp(h["time_epoch"]).strftime("%H")
            if hour < now.strftime("%H"):
                continue

            desc = h["condition"]["text"]
            pop = h["will_it_rain"]
            if current_pop is None:
                current_pop = pop
            if rain_change is None:
                if (current_pop == 0 and pop == 1) or (current_pop == 1 and pop == 0):
                    # check if there's a rain change coming
                    rain_change = hour
                    rain_desc = desc

            if int(hour) == 23:  # only look at today
                break

        if rain_change is not None:
            preface = f"{rain_desc} expected at {num2words(rain_change, lang='en')}"
            if int(hour) > 13:
                suffix = "hundred hours"
            else:
                suffix = "o clock"
            rain_prediction = f"{preface} {suffix}"
        return rain_prediction


class Season:
    def __init__(self):
        self.current_date = now.date()

    def get_season_dates(self, year):
        """Return the start dates of seasons for the given year."""
        return {
            "Spring": date(year, 3, 20),
            "Summer": date(year, 6, 21),
            "Autumn": date(year, 9, 23),
            "Winter": date(year, 12, 21),
        }

    def get_current_and_next_season(self):
        year = self.current_date.year
        seasons = self.get_season_dates(year)
        season_names = ["Spring", "Summer", "Autumn", "Winter"]

        # Determine current season and next season
        for i, season in enumerate(season_names):
            if self.current_date < seasons[season]:
                current_season = season_names[i - 1] if i > 0 else "Winter"
                current_start = (
                    seasons[current_season]
                    if i > 0
                    else self.season_dates(year - 1)["Winter"]
                )
                next_season = season
                next_start = seasons[next_season]
                break
        else:
            current_season = "Winter"
            current_start = seasons["Winter"]
            next_season = "Spring"
            next_start = self.season_dates(year + 1)["Spring"]

        return current_season, current_start, next_season, next_start

    def get_season_progress(self):
        current_season, current_start, next_season, next_start = (
            self.get_current_and_next_season()
        )

        days_passed = (self.current_date - current_start).days + 1
        days_until_next = (next_start - self.current_date).days

        total_days = days_passed + days_until_next
        proportion_passed = days_passed / total_days if total_days > 0 else 0

        # Define fractions of the form n/d where n < d, and d ∈ {2, 3, 4, 5}
        fractions = [(n, d) for d in range(2, 11) for n in range(1, d)]

        # Calculate which fraction is closest to the proportion of days passed
        closest_fraction = min(
            fractions, key=lambda frac: abs((frac[0] / frac[1]) - proportion_passed)
        )

        # Extract numerator and denominator of the closest fraction
        closest_numerator, closest_denominator = closest_fraction
        numerator = num2words(closest_numerator)
        denominator = (
            "half"
            if closest_denominator == 2
            else num2words(closest_denominator, lang="en", to="ordinal")
        )

        # Calculate days left in the season
        days_left = total_days - days_passed
        progress = (
            "into" if closest_numerator / closest_denominator < 0.5 else "through"
        )

        # Handle if the season has ended
        if days_left <= 0:
            return f"{current_season} is over. Total duration: {total_days} days"

        return (
            f"We are {num2words(days_passed)} day{'s' if days_passed != 1 else ''}, "
            f"or {numerator} {denominator}{'s' if closest_numerator > 1 else ''} "
            f"of the way {progress} {current_season}, "
            f"with {num2words(days_left)} day{'s' if days_left != 1 else ''} left"
        )


def check_public_holiday():
    # https://www.gov.uk/bank-holidays.json
    with open("bank-holidays.json", "r") as file:
        data = json.load(file)

    today = now.date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)

    days = {today: "Today", tomorrow: "Tomorrow"}

    # Assuming we check only 'england-and-wales', modify for other regions if needed
    holidays = data.get("england-and-wales", {}).get("events", [])

    found_holiday = False
    for holiday in holidays:
        holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d").date()
        if today <= holiday_date <= next_week:
            # print(f"Upcoming Public Holiday: {holiday['title']} on {holiday['date']}")
            found_holiday = True
            break

    if found_holiday:
        if holiday_date in days:
            day = days[holiday_date]
        else:
            day = holiday_date.strftime("%A")

        return f"{day} is {holiday['title']}"
    else:
        return ""


def get_daily_events(file_path="calendar.txt"):
    current_day = now.strftime("%A")  # e.g., Monday, Tuesday
    current_hour = now.hour  # e.g., 11, 14

    matching_entries = []

    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):  # Skip empty lines or comments
                    continue

                try:
                    day, hour, label = line.split(",", 2)
                    if day.strip() == current_day and int(hour.strip()) == current_hour:
                        matching_entries.append(label.strip())
                except ValueError:
                    print(f"Invalid line format: {line}")

    except FileNotFoundError:
        print(f"Calendar file not found at {file_path}")

    return ". ".join(matching_entries)


def get_time_str(time, twentyfour_hour=False):
    time = datetime.strptime(time, "%H:%M")
    BST = 0  # 1  # make zero again when BST ends
    if twentyfour_hour:
        full_hour = int(time.strftime("%I")) + BST
    else:
        full_hour = (int(time.strftime("%I")) + BST) % 12

    hour = num2words(full_hour, lang="en")
    minute = int(time.strftime("%M"))
    if minute == 0:
        minute = "oh clock"
    elif minute < 10:
        minute = " oh " + num2words(minute, lang="en")
    else:
        minute = num2words(minute, lang="en")
    string = f"{hour} {minute}"
    return string


def get_greeting():
    current_hour = int(now.strftime("%H"))
    if current_hour < 12:
        day_stage = "morning"
    elif current_hour < 18:
        day_stage = "afternoon"
    else:
        day_stage = "evening"

    hour = num2words(now.strftime("%I"), lang="en")
    day = now.strftime("%A")
    date = num2words(now.strftime("%-d"), lang="en", to="ordinal")
    month = now.strftime("%B")
    date_str = f"{hour} o clock on {day} the {date} of {month}"
    return day_stage, date_str
