from __future__ import print_function
import datetime
import os
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define the scope for the Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
ACCT_CREDENTIALS = {
    "sacha@jftwines.com": "bibo-calendar.json",
    "sacha@sachawheeler.com": "sacha-calendar.json",
}

def authenticate_google_calendar(account=None):
    """Authenticates with the Google Calendar API using a service account."""
    # print(account)
    if account is None:
        return None
    else:
        SERVICE_ACCOUNT_FILE = ACCT_CREDENTIALS[account]

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)
    return service, account

def get_today_upcoming_events(service, account=None):
    # print(f"geting events for {account}")
    # Define the time zone for London, England
    london_tz = pytz.timezone('Europe/London')

    # Get the current time in London, England
    now = datetime.datetime.now(london_tz)
    now_iso = now.isoformat()

    # Calculate the end of the day in London, England
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    end_of_day_iso = end_of_day.isoformat()

    # print('Getting today\'s upcoming events')
    events_result = service.events().list(
            calendarId=account,
            timeMin=now_iso,
            timeMax=end_of_day_iso, singleEvents=True,
            orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return None
    upcoming_events = {}
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        # print(start, event['summary'])
        upcoming_events[start] = event['summary']
    return upcoming_events

def main():
    combined = None
    for acct in ['sacha@jftwines.com', 'sacha@sachawheeler.com']:
        service, account = authenticate_google_calendar(acct)
        events = get_today_upcoming_events(service, account)
        if combined is None:
            combined = events
        else:
            combined = {**combined, **events}
            sorted_combined_dict = dict(
                    sorted(combined.items(),
                        key=lambda item: datetime.datetime.fromisoformat(item[0])
                )
            )
            combined = sorted_combined_dict
    print(combined)

if __name__ == '__main__':
    main()

