from pathlib import Path
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

RAW_DATA_TGV = os.path.join(PROJECT_ROOT, "data", "1_raw", "regularite-mensuelle-tgv-aqst.csv")
RAW_DATA_WEATHER = os.path.join(PROJECT_ROOT, "data","1_raw", "weather_7_stations.csv")
CLEAN_DATA_TGV = os.path.join(PROJECT_ROOT, "data", "2_interim", "sncf_filtered_routes.csv")
FULL_RAW_DATA = os.path.join(PROJECT_ROOT, "data", "3_processed", "final_merged_data.csv")
DATA_TRAIN = os.path.join(PROJECT_ROOT, "data", "3_processed", "data_train_model.csv")