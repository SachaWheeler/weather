#!/usr/bin/env python3
"""
Basic test cases for the OOP weather classes.
"""
import json
import unittest
from unittest.mock import patch, mock_open
from datetime import datetime
import pytz

from utils import Weather, Calendar, Announcement


class TestWeatherClass(unittest.TestCase):
    """Test cases for the Weather class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.weather = Weather()
        
        # Sample weather data
        self.sample_weather_data = {
            "current": {
                "temp_c": 16.1,
                "feelslike_c": 16.1,
                "condition": {"text": "Sunny"},
                "wind_kph": 7.9,
                "wind_degree": 266
            },
            "forecast": {
                "forecastday": [{
                    "day": {
                        "maxtemp_c": 22.8,
                        "mintemp_c": 14.2
                    },
                    "astro": {
                        "sunrise": "05:18 AM",
                        "sunset": "08:56 PM"
                    },
                    "hour": [
                        {"time_epoch": 1722060000, "will_it_rain": 0, "condition": {"text": "Sunny"}},
                        {"time_epoch": 1722063600, "will_it_rain": 0, "condition": {"text": "Sunny"}},
                    ]
                }]
            }
        }
    
    def test_current_conditions(self):
        """Test get_current_conditions method."""
        current = self.sample_weather_data["current"]
        temp, conditions = self.weather.get_current_conditions(current)
        
        self.assertIn("sixteen degrees", temp)
        self.assertEqual("Sunny", conditions)
    
    def test_wind_data(self):
        """Test get_wind method."""
        current = self.sample_weather_data["current"]
        wind_speed, wind_direction = self.weather.get_wind(current)
        
        self.assertIn("wind speed of", wind_speed)
        self.assertIn("meter", wind_speed)
        self.assertEqual("West", wind_direction)
    
    def test_temp_forecast(self):
        """Test get_temp_forecast method."""
        forecast = self.sample_weather_data["forecast"]["forecastday"][0]
        temp_forecast = self.weather.get_temp_forecast(forecast)
        
        self.assertIn("A high of", temp_forecast)
        self.assertIn("and a low of", temp_forecast)
        self.assertIn("degrees Celcius", temp_forecast)
    
    def test_deg_to_compass(self):
        """Test _deg_to_compass private method."""
        self.assertEqual("North", self.weather._deg_to_compass(0))
        self.assertEqual("East", self.weather._deg_to_compass(90))
        self.assertEqual("South", self.weather._deg_to_compass(180))
        self.assertEqual("West", self.weather._deg_to_compass(270))


class TestCalendarClass(unittest.TestCase):
    """Test cases for the Calendar class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calendar = Calendar()
    
    @patch("builtins.open", new_callable=mock_open, read_data="Monday,8,Weekly stand-up\nTuesday,10,Manager meeting")
    def test_get_daily_events(self, mock_file):
        """Test get_daily_events method."""
        # Mock current time to be Monday at 8 AM
        with patch.object(self.calendar, 'now') as mock_now:
            mock_now.strftime.side_effect = lambda fmt: {
                "%A": "Monday",
            }.get(fmt, "08")
            mock_now.hour = 8
            
            events = self.calendar.get_daily_events("test_calendar.txt")
            self.assertEqual("Weekly stand-up", events)
    
    def test_is_date_time(self):
        """Test _is_date_time private method."""
        self.assertTrue(self.calendar._is_date_time(("2024-07-26T08:00:00", "Meeting")))
        self.assertFalse(self.calendar._is_date_time(("2024-07-26", "All day event")))
    
    def test_extract_time(self):
        """Test _extract_time private method."""
        time_str = self.calendar._extract_time("2024-07-26T08:30:00")
        self.assertEqual("08:30", time_str)


class TestAnnouncementClass(unittest.TestCase):
    """Test cases for the Announcement class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.announcement = Announcement()
    
    def test_season_dates(self):
        """Test _season_dates private method."""
        dates = self.announcement._season_dates(2024)
        
        self.assertIn("Spring", dates)
        self.assertIn("Summer", dates)
        self.assertIn("Autumn", dates)
        self.assertIn("Winter", dates)
    
    @patch("builtins.open", new_callable=mock_open, read_data='{"england-and-wales": {"events": []}}')
    def test_check_public_holiday_none(self, mock_file):
        """Test check_public_holiday when no holidays."""
        result = self.announcement.check_public_holiday()
        self.assertEqual("", result)
    
    def test_season_progress(self):
        """Test season_progress method."""
        progress = self.announcement.season_progress()
        
        self.assertIn("We are", progress)
        self.assertIn("days", progress)
        self.assertIn("way", progress)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.weather = Weather()
        self.calendar = Calendar()
        self.announcement = Announcement()
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_weather_data_loading(self, mock_json_load, mock_file):
        """Test that weather data can be loaded from file."""
        sample_data = {"current": {"temp_c": 20}, "forecast": {"forecastday": []}}
        mock_json_load.return_value = sample_data
        
        with patch.object(self.weather, '_is_file_outdated', return_value=False):
            data = self.weather.get_weather_data()
            self.assertEqual(sample_data, data)


if __name__ == '__main__':
    print("Running OOP weather system tests...")
    unittest.main(verbosity=2)