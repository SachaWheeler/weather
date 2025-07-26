## Weather - A Personal Assistant Script

This script acts as a personal assistant, providing important daily information at regular intervals.
It uses a text-to-speech engine (connected to a Hi-fi) to speak it to me

---

## Features

At the top of every hour between 07:00 and 14:00, the script provides a detailed summary of:

- **Day, Date & Time**: A greeting with the current time and date.
- **Current Weather Conditions**:
  - Temperature (actual and feels-like)
  - Weather conditions (e.g., Partly Cloudy, Rainy)
  - Wind speed and direction
  - Rain predictions (when it will start or stop, if applicable)
- **Forecast**:
  - Daily high and low temperatures
  - Sunrise time (if it hasn’t occurred yet)
  - Sunset time
  - Total hours and minutes of daylight
- **Seasonal Progress**:
  - How far we are into the current season
  - Days left in the season
- **Public Holidays**:
  - Any holidays in the next 7 days
- **Upcoming Events**:
  - Friends' birthdays
  - Scheduled meetings from connected Google Calendars
  - Next two meetings today (if any) with their times
  - Other daily calendar events
- **Colleagues' Availability**:
  - Identifies if any colleagues are on holiday today (from a shared calendar)

---

## Motivation

I tend to get lost in my work in the morning, so this script serves as a gentle, informative assistant to keep me on track.

---

## Architecture and Design

The script's functionality is designed to be modular and reusable. It is structured around three main objects:

### 1. **Calendar Object**
Handles all calendar-related functionality, including:
- Authentication with Google Calendar API
- Retrieving today's events
- Formatting event details for output

### 2. **Weather Object**
Encapsulates weather-related functionality:
- Fetches current weather data and forecasts using the Weather API
- Processes temperature, wind, and rain predictions
- Calculates sunrise, sunset, and daylight hours

### 3. **Season Object**
Manages season-related calculations:
- Determines the current and next seasons
- Tracks progress into the current season
- Calculates days left until the next season

---

## Example Output

Here’s an example of what the script outputs to the text-to-speech engine:

> Good morning.
> It is eight o'clock on Friday the twenty-fifth of July.
> We are thirty-five days, or three eighths of the way into Summer, with sixty days left.
> It is seventeen degrees but feels like sixteen.
> Currently Partly Cloudy with a wind speed of one meter per second from the North North West.
> A high of twenty-six and a low of sixteen degrees Celsius.
> Events today include Lizzie's birthday.
> Your next appointment is Dev stand-up at eight-thirty, followed by Team lunch at one o'clock.
> Sunset will be at eight fifty-nine for fifteen hours and forty-five minutes of daylight.

---

## Requirements

To run this project, you’ll need:

- Python 3.7+
- **Google Calendar API credentials**:
  - Service account credentials for accessing Google Calendar data
- **Weather API key**:
  - Sign up for an API key at [WeatherAPI](https://www.weatherapi.com/)
- **Public Holidays JSON**:
  - Download the list of public holidays from [GOV.UK Bank Holidays](https://www.gov.uk/bank-holidays.json)
- **Text-to-Speech Engine**:
  - A TTS engine is used to audibly deliver the summary (e.g., `say` command on macOS)

---

## Usage

To run the script, simply execute:
```bash
python weather.py
```

---

## License

This project is for personal use and is not under any specific license currently.

