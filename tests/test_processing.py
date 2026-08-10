import pandas as pd
import pytest
import os

# Import the modules to be tested
from src.data_processing import preprocess_tgv
from src.features import merge_datasets, features_selection


def test_remove_accents():
    """
    Scenario 1: Test the text normalization function.
    Ensure French accents are properly removed.
    """
    assert preprocess_tgv.remove_accents("Chambéry") == "Chambery"
    assert preprocess_tgv.remove_accents("Gare de l'Est") == "Gare de l'Est"
    assert preprocess_tgv.remove_accents("Évian-les-Bains") == "Evian-les-Bains"
    assert pd.isna(preprocess_tgv.remove_accents(None))


def test_preprocess_tgv_logic(monkeypatch, tmp_path):
    """
    Scenario 2: Test raw data cleaning and filtering.
    Verifies that the target routes are filtered, spaces are stripped,
    leakage columns are dropped, and NaNs are filled with 0.
    """
    # 1. Setup temporary file paths for the test
    fake_raw_path = tmp_path / "raw.csv"
    fake_clean_path = tmp_path / "clean.csv"
    
    # Mock the configuration variables in the module
    monkeypatch.setattr(preprocess_tgv, "RAW_DATA_PATH", str(fake_raw_path))
    monkeypatch.setattr(preprocess_tgv, "CLEAN_DATA_PATH", str(fake_clean_path))
    
    # 2. Create dummy raw data (includes one invalid route and NaNs)
    raw_df = pd.DataFrame({
        'Gare depart': [' PARIS EST ', 'HA NOI', 'BELLEGARDE (AIN)'],
        'Gare arrivee': ['STRASBOURG', 'HO CHI MINH', 'PARIS LYON'],
        'Durée moyenne du trajet': [120.5, 200.0, None], # Testing NaN filling
        'Commentaire annulations': ['Bad weather', 'None', 'None'] # Testing column drop
    })
    
    # Save using the exact format expected by the python engine in your script
    raw_df.to_csv(fake_raw_path, sep=';', encoding='utf-8-sig', decimal=',', index=False)
    
    # 3. Execute the function
    preprocess_tgv.process_data()
    
    # 4. Assert the results
    assert os.path.exists(fake_clean_path), "The cleaned file was not generated."
    
    result_df = pd.read_csv(fake_clean_path)
    
    # Ensure only 2 valid routes remain
    assert len(result_df) == 2
    assert 'HA NOI' not in result_df['departure_station'].values
    
    # Ensure spaces were stripped
    assert 'PARIS EST' in result_df['departure_station'].values
    
    # Ensure comment columns are dropped
    assert 'cancellation_comments' not in result_df.columns
    
    # Ensure NaN numeric values are filled with 0
    bellegarde_row = result_df[result_df['departure_station'] == 'BELLEGARDE (AIN)'].iloc[0]
    assert bellegarde_row['avg_journey_duration'] == 0.0


def test_merge_datasets_logic(monkeypatch, tmp_path):
    """
    Scenario 3: Test the joining of train data with weather data.
    Verifies that departure and arrival weather columns are created correctly.
    """
    fake_clean = tmp_path / "clean.csv"
    fake_weather = tmp_path / "weather.csv"
    fake_merged = tmp_path / "merged.csv"
    
    monkeypatch.setattr(merge_datasets, "CLEAN_DATA_TGV", str(fake_clean))
    monkeypatch.setattr(merge_datasets, "RAW_DATA_WEATHER", str(fake_weather))
    monkeypatch.setattr(merge_datasets, "merged_data", str(fake_merged))
    
    # Dummy train data
    pd.DataFrame({
        'date': ['2018-01', '2018-01'],
        'departure_station': ['PARIS EST', 'DIJON VILLE'],
        'arrival_station': ['STRASBOURG', 'PARIS LYON']
    }).to_csv(fake_clean, index=False)
    
    # Dummy weather data
    pd.DataFrame({
        'date': ['2018-01', '2018-01', '2018-01'],
        'station': ['PARIS EST', 'STRASBOURG', 'DIJON VILLE'],
        'temp_mean': [5.0, 2.0, 4.0],
        'precip_sum': [10.0, 5.0, 0.0],
        'wind_max': [15.0, 10.0, 20.0]
    }).to_csv(fake_weather, index=False)
    
    # Execute the merge
    merge_datasets.merge_train_weather()
    
    # Assertions
    result_df = pd.read_csv(fake_merged)
    assert len(result_df) == 2
    assert 'departure_temp_mean' in result_df.columns
    assert 'arrival_temp_mean' in result_df.columns
    
    # Verify PARIS EST to STRASBOURG weather mapped correctly
    paris_est_row = result_df[result_df['departure_station'] == 'PARIS EST'].iloc[0]
    assert paris_est_row['departure_temp_mean'] == 5.0
    assert paris_est_row['arrival_temp_mean'] == 2.0


def test_features_selection_logic(monkeypatch, tmp_path):
    """
    Scenario 4: Test feature engineering.
    Verifies temporal features, extreme weather flags, and data leakage removal.
    """
    fake_merged = tmp_path / "merged.csv"
    fake_train = tmp_path / "train.csv"
    
    monkeypatch.setattr(features_selection, "FULL_RAW_DATA", str(fake_merged))
    monkeypatch.setattr(features_selection, "DATA_TRAIN", str(fake_train))
    
    # Dummy merged data
    pd.DataFrame({
        'date': ['2018-01-01', '2018-06-01'],
        'departure_station': ['PARIS EST', 'PARIS EST'],
        'arrival_station': ['STRASBOURG', 'STRASBOURG'],
        'departure_temp_mean': [5.0, 25.0],
        'arrival_temp_mean': [2.0, 28.0],
        'departure_wind_max': [45.0, 10.0], # 45 > 40 -> extreme wind
        'departure_precip_sum': [90.0, 0.0], # 90 > 80 -> heavy rain
        'arrival_wind_max': [20.0, 15.0],
        'arrival_precip_sum': [10.0, 0.0],
        'avg_delay_all_trains_arrival': [10.5, 5.0], 
        'nb_late_trains_departure': [5, 2] # This is a Data Leakage column
    }).to_csv(fake_merged, index=False)
    
    # Execute feature selection
    features_selection.process_features()
    
    # Assertions
    result_df = pd.read_csv(fake_train)
    
    # 1. Verify Data Leakage elimination
    assert 'nb_late_trains_departure' not in result_df.columns
    
    # 2. Verify Temporal features (Winter=4, Summer=2)
    assert 'month' in result_df.columns
    assert result_df.loc[result_df['month'] == 1, 'season'].iloc[0] == 4 
    assert result_df.loc[result_df['month'] == 6, 'season'].iloc[0] == 2
    
    # 3. Verify Weather Flags thresholds
    assert result_df.loc[result_df['month'] == 1, 'is_extreme_wind_dep'].iloc[0] == 1
    assert result_df.loc[result_df['month'] == 6, 'is_heavy_rain_dep'].iloc[0] == 0
    
    # 4. Verify Lags initialization (should fill NaNs with 0 as defined in code)
    assert 'delay_lag_1' in result_df.columns
    assert 'delay_lag_12' in result_df.columns