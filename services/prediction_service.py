import random
import datetime
import pandas as pd
from services.database import query_region_forecasts

class PredictionService:
    """
    Service class to handle AI temperature forecasting and prediction.
    """
    
    @staticmethod
    def predict_temperature(region_name):
        """
        Generates AI model predictions for a given region for the next 7 days.
        Simulates an AI model output by adding regression trend and noise to baseline data.
        """
        # Load baseline forecasts from SQLite
        df_base = query_region_forecasts(region_name)
        if df_base.empty:
            return pd.DataFrame()
            
        predictions = []
        # Simulate AI model prediction with small variations
        random.seed(42)  # Keep predictions stable for evaluation
        
        for idx, row in df_base.iterrows():
            date_str = row["dataDate"]
            mint_base = row["mint"]
            maxt_base = row["maxt"]
            
            # Simulate prediction errors (noise)
            mint_pred = round(mint_base + random.normalvariate(0, 0.8), 1)
            maxt_pred = round(maxt_base + random.normalvariate(0, 1.2), 1)
            
            predictions.append({
                "regionName": region_name,
                "dataDate": date_str,
                "predicted_mint": mint_pred,
                "predicted_maxt": maxt_pred,
                "error_mint": round(mint_pred - mint_base, 1),
                "error_maxt": round(maxt_pred - maxt_base, 1)
            })
            
        return pd.DataFrame(predictions)
        
    @staticmethod
    def calculate_evaluation_metrics(region_name):
        """
        Calculates MAE (Mean Absolute Error) and RMSE (Root Mean Squared Error)
        comparing actual CWA forecasts and the AI prediction model outputs.
        """
        df_base = query_region_forecasts(region_name)
        df_pred = PredictionService.predict_temperature(region_name)
        
        if df_base.empty or df_pred.empty:
            return {"mint_mae": 0.0, "mint_rmse": 0.0, "maxt_mae": 0.0, "maxt_rmse": 0.0}
            
        # Merge datasets
        df = pd.merge(df_base, df_pred, on=["regionName", "dataDate"])
        
        # Calculate Mean Absolute Error (MAE)
        mint_mae = round((df["predicted_mint"] - df["mint"]).abs().mean(), 2)
        maxt_mae = round((df["predicted_maxt"] - df["maxt"]).abs().mean(), 2)
        
        # Calculate Root Mean Squared Error (RMSE)
        mint_rmse = round(((df["predicted_mint"] - df["mint"])**2).mean()**0.5, 2)
        maxt_rmse = round(((df["predicted_maxt"] - df["maxt"])**2).mean()**0.5, 2)
        
        return {
            "mint_mae": mint_mae,
            "mint_rmse": mint_rmse,
            "maxt_mae": maxt_mae,
            "maxt_rmse": maxt_rmse
        }
