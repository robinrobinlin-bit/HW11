import unittest
import os
import sqlite3
import pandas as pd

class TestWeatherDashboard(unittest.TestCase):
    def setUp(self):
        self.db_file = "data.db"
        self.csv_file = "weather_data.csv"
        
    def test_database_exists(self):
        """Verify that SQLite database data.db exists."""
        self.assertTrue(os.path.exists(self.db_file), "Database file data.db does not exist.")
        
    def test_csv_exists(self):
        """Verify that weather_data.csv is generated."""
        self.assertTrue(os.path.exists(self.csv_file), "CSV output file weather_data.csv does not exist.")
        
    def test_database_schema(self):
        """Verify table schema of TemperatureForecasts matches prompt requirements."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(TemperatureForecasts)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        expected_cols = ['id', 'regionName', 'dataDate', 'mint', 'maxt']
        for col in expected_cols:
            self.assertIn(col, columns, f"Column '{col}' is missing in TemperatureForecasts table.")
            
    def test_fetch_modules(self):
        """Verify that API fetching modules are present and importable."""
        try:
            import fetch_weather
            self.assertTrue(hasattr(fetch_weather, 'fetch_weather_data'))
            self.assertTrue(hasattr(fetch_weather, 'extract_temperature'))
            
            import fetch_observations
            self.assertTrue(hasattr(fetch_observations, 'fetch_realtime_observations'))
            self.assertTrue(hasattr(fetch_observations, 'compute_extremes'))
        except ImportError as e:
            self.fail(f"Module import failed: {e}")

if __name__ == "__main__":
    print("[INFO] Running unit tests...")
    unittest.main()
