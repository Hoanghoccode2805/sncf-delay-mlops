import pandas as pd
from config.config import CLEAN_DATA_TGV, RAW_DATA_WEATHER, FULL_RAW_DATA
import os

merged_data = FULL_RAW_DATA

def merge_train_weather():
    print("Loading data ...")
    df_tgv = pd.read_csv(CLEAN_DATA_TGV)
    df_weather = pd.read_csv(RAW_DATA_WEATHER)
    
    # 1. Merge weather data for the DEPARTURE station
    print("Merging weather data for departure stations...")
    df_merged = pd.merge (
        df_tgv,
        df_weather,
        how = 'left',
        left_on= ['date', 'departure_station'],
        right_on= ['date', 'station']
    )

    # Rename the newly merged weather columns to specify they belong to the departure station
    df_merged = df_merged.rename(columns={
        'temp_mean': 'departure_temp_mean',
        'precip_sum': 'departure_precip_sum',
        'wind_max': 'departure_wind_max'
    }).drop(columns=['station'])  # Drop the redundant 'station' column from the weather dataset

    # 2. Merge weather data for the ARRIVAL station
    print("Merging weather data for arrival stations...")
    df_merged = pd.merge(
        df_merged,
        df_weather,
        how='left',
        left_on=['date', 'arrival_station'],
        right_on=['date', 'station']
    )
    
    # Rename the newly merged weather columns to specify they belong to the arrival station
    df_merged = df_merged.rename(columns={
        'temp_mean': 'arrival_temp_mean',
        'precip_sum': 'arrival_precip_sum',
        'wind_max': 'arrival_wind_max'
    }).drop(columns=['station'])

    # 3. Handle missing values 
    weather_columns = [
        'departure_temp_mean', 'departure_precip_sum', 'departure_wind_max', 
        'arrival_temp_mean', 'arrival_precip_sum', 'arrival_wind_max'
    ]
    # Temporarily fill NaN values with 0 (this can be adjusted later during feature engineering)
    df_merged[weather_columns] = df_merged[weather_columns].fillna(0)

    # 4. Save the Final Master Dataset
    os.makedirs(os.path.dirname(merged_data), exist_ok=True)
    df_merged.to_csv(merged_data, index=False)
    
    print("\n--- FINAL DATASET SAMPLE ---")
    # Display a few key columns to verify the merge was successful
    cols_to_show = ['date', 'departure_station', 'departure_temp_mean', 'arrival_station', 'arrival_temp_mean']
    print(df_merged[cols_to_show].head())
    print(f"\nSuccess! The master dataset contains {df_merged.shape[0]} rows and {df_merged.shape[1]} columns.")
    print(f"Saved to: {merged_data}")

if __name__ == "__main__":
    merge_train_weather()