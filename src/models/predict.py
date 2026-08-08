import os
import pandas as pd
import mlflow
import mlflow.sklearn

os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

class SCNFDelayPredictor:
    def __init__(self, run_id: str, model_name : str = "model_Random_Forest" ):
        mlflow.set_tracking_uri("sqlite:///mlflow.db")

        # Standard MLflow path: runs:/<run_id>/<model_folder_name>
        self.model_uri = f"runs:/{run_id}/{model_name}"

        print(f"Load model from {self.model_uri}")
        self.model = mlflow.sklearn.load_model(self.model_uri)
        print("Model loaded successfully")

        # Get the list of features (columns) required by the model from MLflow metadata
        self.expected_columns = list(self.model.feature_names_in_)

    def predict(self, input_data: dict) -> float:
        # 1. Convert dict to DataFrame 
        df = pd.DataFrame([input_data])

        # 2. Handling One-Hot Encoding (OHE) for categorical columns (stations)
        categories_cols = df.select_dtypes(include = ['object', 'string']).columns
        if len(categories_cols) > 0:
            df = pd.get_dummies(df, columns= categories_cols, drop_first= False)

        # 3. Synchronize columns with the training set 
        # Add missing columns with zeros, remove extra columns
        for col in self.expected_columns:
            if col not in df.columns:
                df[col] = 0

        df = df[self.expected_columns]

        # 4. Predict
        prediction = self.model.predict(df)

        # 5. Return result (Rounded to 2 decimal places, unit: minutes) 
        return round(float(prediction[0]), 2)

if __name__ == "__main__": 
    TEST_RUN_ID = "e2ebbfbff1cc46d382156d40ba9e1493"
    try:
        predictor = SCNFDelayPredictor(run_id=TEST_RUN_ID)
        sample_input = {
            "departure_station": "BELLEGARDE (AIN)",
            "arrival_station": "PARIS LYON",
            "avg_journey_duration": 162.0,
            "nb_planned_trains": 259.0,
            "nb_cancelled_trains": 3.0,
            "departure_temp_mean": 5.59,
            "departure_precip_sum": 283.5,
            "departure_wind_max": 19.52,
            "arrival_temp_mean": 7.15,
            "arrival_precip_sum": 130.3,
            "arrival_wind_max": 46.35,
            "year": 2018,
            "month": 1,
            "season": 4,
            "temp_diff_route": 1.56,
            "is_extreme_wind_dep": 0,
            "is_heavy_rain_dep": 1,
            "is_extreme_wind_arr": 1,
            "is_heavy_rain_arr": 1,
            "delay_lag_1": 5.4653,
            "delay_lag_12": 5.2291
        }

        result = predictor.predict(sample_input)
        print(f"Delay forecast for the train: {result} minutes")

    except Exception as e:
        print(f"Error: {e}")