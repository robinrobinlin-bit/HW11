import os
import sqlite3
import pandas as pd

# Path to data/data.db relative to this file's directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "data.db")

def get_connection():
    """
    Returns a sqlite3 connection object. Creates data directory if missing.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_FILE)

def init_db():
    """
    Initializes the SQLite database and creates the TemperatureForecasts table.
    Uses a UNIQUE constraint on (regionName, dataDate) to handle updates gracefully.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TemperatureForecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regionName TEXT NOT NULL,
                dataDate TEXT NOT NULL,
                mint REAL,
                maxt REAL,
                UNIQUE(regionName, dataDate)
            )
        """)
        
        conn.commit()
        print(f"[INFO] Database initialized successfully at: {DB_FILE}")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
    finally:
        if conn:
            conn.close()

def save_forecasts(forecasts):
    """
    Saves a list of parsed forecast dictionaries into the database.
    Uses INSERT OR REPLACE to update existing forecasts for the same region and date.
    """
    if not forecasts:
        print("[WARNING] No forecasts to save.")
        return
        
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        for f in forecasts:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO TemperatureForecasts (regionName, dataDate, mint, maxt)
                    VALUES (?, ?, ?, ?)
                """, (f["regionName"], f["dataDate"], f["mint"], f["maxt"]))
                inserted_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to insert forecast: {f}. Error: {e}")
                
        conn.commit()
        print(f"[INFO] Successfully saved/updated {inserted_count} temperature forecasts in SQLite.")
    except Exception as e:
        print(f"[ERROR] Database operation failed during save: {e}")
    finally:
        if conn:
            conn.close()

def query_all_regions():
    """
    Queries and returns all distinct region names from the database.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT regionName FROM TemperatureForecasts ORDER BY regionName")
        regions = [row[0] for row in cursor.fetchall()]
        return regions
    except Exception as e:
        print(f"[ERROR] Failed to query regions: {e}")
        return []
    finally:
        if conn:
            conn.close()

def query_central_forecasts():
    """
    Queries and returns all weather forecast records for the Central Taiwan Sea Area (中部地區).
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT regionName FROM TemperatureForecasts WHERE regionName LIKE '%中部%'")
        rows = cursor.fetchall()
        
        if not rows:
            return pd.DataFrame()
            
        central_region_name = rows[0][0]
        
        query = """
            SELECT id, regionName, dataDate, mint, maxt 
            FROM TemperatureForecasts 
            WHERE regionName = ? 
            ORDER BY dataDate
        """
        df = pd.read_sql_query(query, conn, params=(central_region_name,))
        return df
    except Exception as e:
        print(f"[ERROR] Failed to query Central region forecasts: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def query_region_forecasts(region_name):
    """
    Queries and returns all weather forecast records for a specific region.
    """
    conn = None
    try:
        conn = get_connection()
        query = """
            SELECT id, regionName, dataDate, mint, maxt 
            FROM TemperatureForecasts 
            WHERE regionName = ? 
            ORDER BY dataDate
        """
        df = pd.read_sql_query(query, conn, params=(region_name,))
        return df
    except Exception as e:
        print(f"[ERROR] Failed to query forecasts for region {region_name}: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
