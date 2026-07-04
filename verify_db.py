import sys
from weather_db import query_all_regions, query_central_forecasts

def verify():
    """
    Queries and verifies the database contents by printing:
    1. All distinct region names.
    2. Weekly forecast for the Central Taiwan Sea Area (中部地區).
    """
    print("="*60)
    print(" VERIFYING DATABASE CONTENTS ")
    print("="*60)
    
    # 1. List all region names
    regions = query_all_regions()
    print(f"\n[1] All Region Names in Database ({len(regions)} total):")
    if not regions:
        print("  (No regions found in database. Make sure fetch_weather.py ran successfully.)")
    for r in regions:
        print(f"  - {r}")
        
    # 2. List forecasts for Central region
    print("\n" + "-"*60)
    print("[2] Weather Forecast for Central Region (中部地區):")
    print("-"*60)
    df = query_central_forecasts()
    if df.empty:
        print("No central region forecast found in database.")
    else:
        # Display the pandas dataframe nicely
        print(df.to_string(index=False))
    print("="*60 + "\n")

if __name__ == "__main__":
    verify()
