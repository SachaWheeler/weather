#!/usr/bin/env python3
from __future__ import print_function

from utils import (
    get_schedule
)

daily_events                                = get_schedule()

print(daily_events)
