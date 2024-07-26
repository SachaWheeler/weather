from __future__ import print_function
import datetime
import os
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define the scope for the Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Path to the service account key file
SERVICE_ACCOUNT_FILE = 'weather-and-calendar.json'

def authenticate_google_calendar():
    """Authenticates with the Google Calendar API using a service account."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)
    return service

def get_today_upcoming_events(service):
    # Define the time zone for London, England
    london_tz = pytz.timezone('Europe/London')

    # Get the current time in London, England
    now = datetime.datetime.now(london_tz)
    now_iso = now.isoformat()

    # Calculate the end of the day in London, England
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    end_of_day_iso = end_of_day.isoformat()
    print(end_of_day)

    print('Getting today\'s upcoming events')
    events_result = service.events().list(calendarId='primary', timeMin=now_iso,
                                          timeMax=end_of_day_iso, singleEvents=True,
                                          orderBy='startTime').execute()
    print(events_result)
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def main():
    service = authenticate_google_calendar()
    get_today_upcoming_events(service)

if __name__ == '__main__':
    main()

