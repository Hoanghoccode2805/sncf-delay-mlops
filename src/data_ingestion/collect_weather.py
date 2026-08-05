import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
from config.config import RAW_DATA_WEATHER

#1. Configure Cache and Retry (Use MLOps to prevent API crashes due to network congestion)
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

#2. List of stations and coordinates
stations = {
    'PARIS_LYON': (48.8443, 2.3730),
    'PARIS_EST': (48.8777, 2.3579),
    'CHAMBERY CHALLES LES EAUX': (45.5906, 5.8987),
    'BELLEGARDE (AIN)': (46.1047, 5.8252),
    'DIJON_VILLE': (47.3200, 5.0667),
    'STRASBOURG': (48.5731, 7.6392),
    'MULHOUSE VILLE': (47.7451, 7.3394),
}

def collect_weather_openmeteo():
    url = "https://archive-api.open-meteo.com/v1/archive"
    all_monthly_data = []

    for name, (lat, lon) in stations.items():
        print(f"Loading weather data for the station: {name}...")
        
        # Configure parameters to retrieve data by date (Daily)
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": "2018-01-01",
            "end_date": "2026-06-30",
            "daily": ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"],
            "timezone": "Europe/Paris"
        }

        try:
            # Call API
            responses = openmeteo.weather_api(url, params=params)
            response = responses[0]

            # Processing the returned data
            daily = response.Daily()
            daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
            daily_precipitation_sum = daily.Variables(1).ValuesAsNumpy()
            daily_wind_speed_10m_max = daily.Variables(2).ValuesAsNumpy()

            # Create a Date range and assign it to a DataFrame
            daily_data = {"date": pd.date_range(
                start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
                end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
                freq = pd.Timedelta(seconds = daily.Interval()),
                inclusive = "left"
            )}
            
            daily_data["temp_mean"] = daily_temperature_2m_mean
            daily_data["precip_sum"] = daily_precipitation_sum
            daily_data["wind_max"] = daily_wind_speed_10m_max
            
            df_daily = pd.DataFrame(data = daily_data)
            
            # Convert the date column to standard datetime format (remove the UTC timezone for easier grouping)
            df_daily['date'] = df_daily['date'].dt.tz_localize(None)
            
            # 3. Aggregate from Day to Month using Pandas
            # Create a year_month column in 'YYYY-MM' format
            df_daily['year_month'] = df_daily['date'].dt.to_period('M').astype(str)
            
            df_monthly = df_daily.groupby('year_month').agg(
                temp_mean=('temp_mean', 'mean'),        # Average monthly temperature
                precip_sum=('precip_sum', 'sum'),       # Total rainfall in the month
                wind_max=('wind_max', 'max')            # The strongest wind gusts of the month.
            ).reset_index()

            # More information of station
            df_monthly['station'] = name
            
            # Round the decimal numbers for a nicer look
            df_monthly = df_monthly.round(2)
            
            all_monthly_data.append(df_monthly)
            print(f"Success: The {len(df_monthly)} months have been compiled.")

        except Exception as e:
            print(f"Error processing gas {name}: {e}")

    # Combine all the data
    if all_monthly_data:
        df_final = pd.concat(all_monthly_data, ignore_index=True)
        
        # Rename the year_month column to date to make it easier to join with TGV data later
        df_final = df_final.rename(columns={'year_month': 'date'})
        
        print("\n--- SAMPLE RESULTS ---")
        print(df_final.head())
        print(f"Complete! Total {len(df_final)} records")
        
        # Lưu file CSV
        output_path = RAW_DATA_WEATHER
        df_final.to_csv(output_path, index=False)
        print(f"The file has been saved at: {output_path}")
    else:
        print("\n Data could not be retrieved.")

if __name__ == "__main__":
    collect_weather_openmeteo()