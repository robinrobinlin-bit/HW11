import os
import pandas as pd
from services.cwa_service import fetch_weather_forecast, extract_forecast_temperature
from services.database import init_db, save_forecasts

def fetch_weather_data():
    """Compatibility wrapper function."""
    return fetch_weather_forecast()

def extract_temperature(data):
    """Compatibility wrapper function."""
    return extract_forecast_temperature(data)

def observe_raw_data(data):
    """Compatibility wrapper function."""
    import json
    print("\n" + "="*50)
    print(" OBSERVING RAW DATA (Truncated) ")
    print("="*50)
    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "...\n[Truncated]\n" + "="*50 + "\n")

def observe_extracted_data(extracted):
    """Compatibility wrapper function."""
    import json
    print("\n" + "="*50)
    print(" OBSERVING EXTRACTED TEMPERATURE DATA ")
    print("="*50)
    print(json.dumps(extracted[:10], indent=2, ensure_ascii=False))
    print("="*50 + "\n")

if __name__ == "__main__":
    raw_data = fetch_weather_data()
    observe_raw_data(raw_data)
    extracted = extract_temperature(raw_data)
    observe_extracted_data(extracted)
    
    # Save CSV into data/ folder
    df = pd.DataFrame(extracted)
    os.makedirs("data", exist_ok=True)
    df.to_csv(os.path.join("data", "weather_data.csv"), index=False, encoding="utf-8-sig")
    print("[INFO] Saved extracted data to data/weather_data.csv")
    
    init_db()
    save_forecasts(extracted)
