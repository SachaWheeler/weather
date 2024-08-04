#!/usr/bin/env python
from __future__ import print_function
import requests
import json
import time
import pprint
import datetime
from num2words import num2words
import re
import os.path
import pytz

from licence import API_KEY
from google_auth import authenticate_google_calendar, get_today_upcoming_events


# get Calendar appointments
try:
    service = authenticate_google_calendar()
    # appointments = get_today_upcoming_events(service)

    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        print(calendar_list)
        for calendar_list_entry in calendar_list['items']:
            print(calendar_list_entry['summary'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    print()

    events_str = ""
    """
    for event_time, event_name in appointments.items():
        time_str = get_time_str(extract_time(event_time), True)

        if events_str == "":
            events_str = f"Your next appointment is {event_name} at {time_str}"
        else:
            events_str += f", followed by {event_name} at {time_str}"
            break
    """
except Exception as e:
    print(e)
    pass


