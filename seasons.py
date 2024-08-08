from datetime import datetime, timedelta

# Define the dates for the start of each season in the current year
def get_season_dates(year):
    return {
        "Spring": datetime(year, 3, 20),
        "Summer": datetime(year, 6, 21),
        "Fall": datetime(year, 9, 23),
        "Winter": datetime(year, 12, 21)
    }

# Get the current date
today = datetime.now()

# Get the season dates for the current year
season_dates = get_season_dates(today.year)

# Check if the next season is in the current or next year
for season, start_date in season_dates.items():
    if start_date > today:
        next_season = season
        days_until_next_season = (start_date - today).days
        break
else:
    # If no more seasons are left this year, calculate days until the first season of next year
    next_season = "Spring"
    next_year = today.year + 1
    spring_start_next_year = get_season_dates(next_year)["Spring"]
    days_until_next_season = (spring_start_next_year - today).days

# Print the result
print(f"The next season is {next_season}, which starts in {days_until_next_season} days.")

