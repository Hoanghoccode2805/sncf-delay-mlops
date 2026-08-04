import pandas as pd
import unicodedata
import os
from config.config import RAW_DATA_TGV, CLEAN_DATA_TGV

# -----------------------------------------------------------------------------
# Configuration Paths
# -----------------------------------------------------------------------------
RAW_DATA_PATH = RAW_DATA_TGV
CLEAN_DATA_PATH = CLEAN_DATA_TGV
# -----------------------------------------------------------------------------
# Target Routes Configuration
# -----------------------------------------------------------------------------
# List of tuples defining the specific (departure_station, arrival_station) routes to keep
TARGET_ROUTES = [
    ("CHAMBERY CHALLES LES EAUX", "PARIS LYON"),
    ("BELLEGARDE (AIN)", "PARIS LYON"),
    ("PARIS EST", "STRASBOURG"),
    ("PARIS LYON", "MULHOUSE VILLE"),
    ("DIJON VILLE", "PARIS LYON")
]

# -----------------------------------------------------------------------------
# Column Mapping: French to English (snake_case)
# -----------------------------------------------------------------------------
COLUMN_MAPPING = {
    'Date': 'date',
    'Service': 'service',
    'Gare de départ': 'departure_station',
    'Gare d\'arrivée': 'arrival_station',
    'Durée moyenne du trajet': 'avg_journey_duration',
    'Nombre de circulations prévues': 'nb_planned_trains',
    'Nombre de trains annulés': 'nb_cancelled_trains',
    'Commentaire annulations': 'cancellation_comments',
    'Nombre de trains en retard au départ': 'nb_late_trains_departure',
    'Retard moyen des trains en retard au départ': 'avg_delay_late_trains_departure',
    'Retard moyen de tous les trains au départ': 'avg_delay_all_trains_departure',
    'Commentaire retards au départ': 'departure_delay_comments',
    'Nombre de trains en retard à l\'arrivée': 'nb_late_trains_arrival',
    'Retard moyen des trains en retard à l\'arrivée': 'avg_delay_late_trains_arrival',
    'Retard moyen de tous les trains à l\'arrivée': 'avg_delay_all_trains_arrival',
    'Commentaire retards à l\'arrivée': 'arrival_delay_comments',
    'Nombre trains en retard > 15min': 'nb_trains_late_over_15min',
    'Retard moyen trains en retard > 15 (si liaison concurrencée par vol)': 'avg_delay_trains_late_over_15min',
    'Nombre trains en retard > 30min': 'nb_trains_late_over_30min',
    'Nombre trains en retard > 60min': 'nb_trains_late_over_60min',
    'Prct retard pour causes externes': 'pct_delay_external_causes',
    'Prct retard pour cause infrastructure': 'pct_delay_infrastructure',
    'Prct retard pour cause gestion trafic': 'pct_delay_traffic_management',
    'Prct retard pour cause matériel roulant': 'pct_delay_rolling_stock',
    'Prct retard pour cause gestion en gare et réutilisation de matériel': 'pct_delay_station_management',
    'Prct retard pour cause prise en compte voyageurs (affluence; gestions PSH; correspondances)': 'pct_delay_passenger_factors'
}

COLUMNS_TO_DROP = [
    'cancellation_comments',
    'departure_delay_comments',
    'arrival_delay_comments'
]

def remove_accents(text: str) -> str:
    """
    Removes French accents and diacritics from a string.
    """
    if pd.isna(text) or not isinstance(text, str):
        return text
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

def process_data():
    print(f"Reading raw data from: {RAW_DATA_PATH}")
    
    # 1. Load raw data using latin1 encoding and python engine to handle bad lines
    df = pd.read_csv(
        RAW_DATA_PATH, 
        sep=';', 
        decimal=',',
        encoding='latin1', 
        engine='python', 
        on_bad_lines='skip'
    )
    
    # 2. Strip whitespaces from departure and arrival stations to ensure exact matching
    df['Gare de départ'] = df['Gare de départ'].astype(str).str.strip()
    df['Gare d\'arrivée'] = df['Gare d\'arrivée'].astype(str).str.strip()
    
    # 3. Filter data for the exact 5 routes required
    # Create a boolean mask initialized to False
    mask = pd.Series([False] * len(df))
    
    for dep_station, arr_station in TARGET_ROUTES:
        route_mask = (df['Gare de départ'] == dep_station) & (df['Gare d\'arrivée'] == arr_station)
        mask = mask | route_mask
        
    df_filtered = df[mask].copy()
    
    # 4. Remove accents from all string columns
    string_cols = df_filtered.select_dtypes(include=['object', 'string']).columns
    for col in string_cols:
        df_filtered[col] = df_filtered[col].apply(remove_accents)
        
    # 5. Rename columns to English standard (snake_case)
    df_filtered = df_filtered.rename(columns=COLUMN_MAPPING)

    # 6. Remove unnecessary comments columns
    df_filtered = df_filtered.drop(columns=COLUMNS_TO_DROP, errors='ignore')

    # 7. Handling Missing Values ​​(NaN) for numeric columns
    # Enter 0 for NaN values ​​(e.g., If there are no delays > 15 minutes, enter 0 instead of NaN)
    numeric_cols = df_filtered.select_dtypes(include=['float64', 'int64']).columns
    df_filtered[numeric_cols] = df_filtered[numeric_cols].fillna(0)

    # 8. Save the cleaned and filtered dataset
    os.makedirs(os.path.dirname(CLEAN_DATA_PATH), exist_ok=True)
    df_filtered.to_csv(CLEAN_DATA_PATH, index=False, encoding='utf-8', sep=',')
    
    print(f"Data processing complete! Kept {len(df_filtered)} rows representing the 5 target routes.")
    print(f"Unnecessary columns dropped: {COLUMNS_TO_DROP}")
    print(f"Cleaned file saved to: {CLEAN_DATA_PATH}")

if __name__ == "__main__":
    process_data()