# Compatibility wrapper pointing to services/database.py
from services.database import (
    get_connection,
    init_db,
    save_forecasts,
    query_all_regions,
    query_central_forecasts,
    query_region_forecasts,
    DB_FILE
)
