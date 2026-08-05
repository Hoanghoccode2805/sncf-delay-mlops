import pandas as pd
from config.config import FULL_RAW_DATA, DATA_TRAIN
import os

def process_features():
    print(f"Loading merged data from: {FULL_RAW_DATA}")
    df = pd.read_csv(FULL_RAW_DATA)

    # 1. FEATURE SELECTION (Delete Data Leakage)
    print("Eliminating variables that cause Data Leakage")
    leakage_columns = [
        'nb_late_trains_departure', 'avg_delay_late_trains_departure', 'avg_delay_all_trains_departure',
        'nb_late_trains_arrival', 'avg_delay_late_trains_arrival', 
        'nb_trains_late_over_15min', 'avg_delay_trains_late_over_15min', 
        'nb_trains_late_over_30min', 'nb_trains_late_over_60min',
        'pct_delay_external_causes', 'pct_delay_infrastructure', 'pct_delay_traffic_management', 
        'pct_delay_rolling_stock', 'pct_delay_station_management', 
        'pct_delay_passenger_factors',
        'service'  # Ignore them because they're all National.
    ]
    df = df.drop(columns=[col for col in leakage_columns if col in df.columns], errors='ignore')


    # 2. TEMPORAL FEATURES 
    print("Creating temporal features (Season, Month, Year)")
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    # Season classification: 1 (Spring), 2 (Summer), 3 (Autumn), 4 (Winter)
    df['season'] = df['month'].apply(lambda x: 4 if x in [12, 1, 2] else (1 if x in [3, 4, 5] else (2 if x in [6, 7, 8] else 3)))


    # 3. WEATHER FEATURES (Weather warning)
    print("Creating weather features (temperature fluctuations, storm warnings)")
    df['temp_diff_route'] = abs(df['arrival_temp_mean'] - df['departure_temp_mean'])
    df['is_extreme_wind_dep'] = (df['departure_wind_max'] > 40).astype(int)
    df['is_heavy_rain_dep'] = (df['departure_precip_sum'] > 80).astype(int)
    df['is_extreme_wind_arr'] = (df['arrival_wind_max'] > 40).astype(int)
    df['is_heavy_rain_arr'] = (df['arrival_precip_sum'] > 80).astype(int)


    # 4. LAGGED FEATURES (System inertia – Historical data)
    print("Creating lagged features")
    df = df.sort_values(by=['departure_station', 'arrival_station', 'date'])
    
    # Calculate lag 1 (previous month) and lag 12 (same period last year).
    df['delay_lag_1'] = df.groupby(['departure_station', 'arrival_station'])['avg_delay_all_trains_arrival'].shift(1)
    df['delay_lag_12'] = df.groupby(['departure_station', 'arrival_station'])['avg_delay_all_trains_arrival'].shift(12)

    # Fill in the average values ​​for months with missing data.
    df['delay_lag_1'] = df.groupby(['departure_station', 'arrival_station'])['delay_lag_1'].transform(lambda x: x.fillna(x.mean()))
    df['delay_lag_12'] = df.groupby(['departure_station', 'arrival_station'])['delay_lag_12'].transform(lambda x: x.fillna(x.mean()))
    
    # If there are still NaN, fill in 0.
    df['delay_lag_1'] = df['delay_lag_1'].fillna(0)
    df['delay_lag_12'] = df['delay_lag_12'].fillna(0)

    # Convert the 'date' column back to the standard YYYY-MM format.
    df['date'] = df['date'].dt.strftime('%Y-%m')

    # 5. SAVE DATA
    print("Exporting training data")
    os.makedirs(os.path.dirname(DATA_TRAIN), exist_ok=True)
    df.to_csv(DATA_TRAIN, index=False)
    
    print("\n--- COMPLETING FEATURE ENGINEERING ---")
    print(f"The data is ready! There are {df.shape[0]} rows and {df.shape[1]} columns (features).")
    print(f"Saved at: {DATA_TRAIN}")

if __name__ == "__main__":
    process_features()