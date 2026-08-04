from pathlib import Path
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

RAW_DATA_TGV = os.path.join(PROJECT_ROOT, "data", "regularite-mensuelle-tgv-aqst.csv")
CLEAN_DATA_TGV = os.path.join(PROJECT_ROOT, "data", "sncf_filtered_routes.csv")
RAW_DATA_WEATHER = os.path.join(PROJECT_ROOT, "data", "weather_7_stations.csv")