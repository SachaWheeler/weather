## Weather - A Personal Assistant Script

It uses a text-to-speech engine (connected to my Hi-fi) to inform me of important daily details.

## Features

At the top of every hour between 07:00 and 14:00, it provides a summary of:
- the day, date & time
- current weather conditions & temperature
- rain predictions if any (when it will start if it hasn't yet or end if it has)
- sunrise time (if still to come), sunset time & total hours of daylight
- how far are we into the current season
- any public holidays or friends' birthdays in the next 7 days
- if any of my colleagues are on holiday today (from a shared calendar)
- my next 2 scheduled meetings today (if any) and when they are
- and my upcoming calendar events for the day.

## Motivation

I tend to get lost in my work in the morning, so this script serves as a gentle, informative assistant
to keep me on track.

## Requirements
- Python 3.7+
- Google Calendar & API key
- [OpenWeatherMap API key](https://openweathermap.org/api)
- [List of public holidays](https://www.gov.uk/bank-holidays.json)
- A text-to-speech engine ('say' on a networked Mac)

## Example Output

This would be sent to a text-to-speech engine:
> Good morning.
> It is eight o clock on Friday the twenty-fifth of July.
> We are thirty-five days, or three eighths of the way into Summer, with sixty days left.
> It is seventeen degrees.
> Currently Partly Cloudy with wind speed of one meter per second from the North North West.
> A high of twenty-six and a low of sixteen degrees Celcius.
> Events today include Lizzies birthday.
> Your next appointment is Dev stand-up at eight thirty, followed by Team lunch at one oh clock.
> Sunset will be at eight fifty-nine for fifteen hours and forty-five minutes of daylight.


## License
This project is for personal use and is not under any specific license currently.
