#!/usr/bin/env python
from __future__ import print_function
import datetime
import os.path
import pickle
import requests
import pytz
import re

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google_calendar():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_today_upcoming_events(service):
    # Define the time zone for London, England
    london_tz = pytz.timezone('Europe/London')

    # Get the current time in London, England
    now = datetime.datetime.now(london_tz).isoformat()

    # Calculate the end of the day in London, England
    end_of_day = (datetime.datetime.now(london_tz) + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    print('Getting today\'s upcoming events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          timeMax=end_of_day, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        time_str = extract_time(start)
        event_name = event['summary']
        print(f'Time: {time_str}, Event: {event_name}')

def extract_time(start):
    """Extract the time from the datetime string."""
    # Using regular expression to find the time part
    match = re.search(r'T(\d{2}:\d{2}):\d{2}', start)
    if match:
        return match.group(1)
    return start

def main():
    service = authenticate_google_calendar()
    get_today_upcoming_events(service)

if __name__ == '__main__':
    main()

