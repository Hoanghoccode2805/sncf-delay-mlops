from pydantic import BaseModel, Field
from typing import Literal
class SNCFDelayInput(BaseModel):
    departure_station: Literal[
        "CHAMBERY CHALLES LES EAUX", 
        "BELLEGARDE (AIN)", 
        "PARIS EST", 
        "PARIS LYON", 
        "DIJON VILLE"
    ] = Field(..., description="Must be one of the exact 5 valid departure stations.")

    arrival_station: Literal[
        "PARIS LYON", 
        "STRASBOURG", 
        "MULHOUSE VILLE"
    ] = Field(..., description="Must be one of the exact valid arrival stations.")

    avg_journey_duration: float = Field(
        ..., ge = 0,
        description="Average planned journey duration in minutes.",
        example=162.0
    )
    nb_planned_trains: float = Field(
        ..., ge = 0,
        description="Total number of trains planned for this route in the given month.",
        example=259.0
    )
    nb_cancelled_trains: float = Field(
        ..., ge = 0,
        description="Total number of cancelled trains for this route in the given month.",
        example=3.0
    )
    
    # --- Weather Features ---
    departure_temp_mean: float = Field(..., description="Mean temperature at the departure station (°C).", example=5.59)
    departure_precip_sum: float = Field(..., ge = 0, description="Total precipitation at the departure station (mm).", example=283.5)
    departure_wind_max: float = Field(..., ge = 0, description="Maximum wind speed at the departure station (km/h).", example=19.52)

    arrival_temp_mean: float = Field(..., description="Mean temperature at the arrival station (°C).", example=7.15)
    arrival_precip_sum: float = Field(..., ge = 0, description="Total precipitation at the arrival station (mm).", example=130.3)
    arrival_wind_max: float = Field(..., ge = 0, description="Maximum wind speed at the arrival station (km/h).", example=46.35)
    
    # --- Time Features ---
    year: int = Field(..., ge = 2017 ,description="Year of the journey (e.g., 2018).", example=2018)
    month: int = Field(..., ge = 1, le =12 ,description="Month of the journey (1 to 12).", example=1)
    season: int = Field(..., ge = 1, le = 4, description="Season code: 1 (Spring), 2 (Summer), 3 (Autumn), 4 (Winter).", example=4)
    
    # --- Engineered Features ---
    temp_diff_route: float = Field(..., description="Absolute temperature difference between departure and arrival.", example=1.56)

    is_extreme_wind_dep: int = Field(..., ge = 0, le=1, description="Boolean flag (0 or 1): Is there extreme wind at departure?", example=0)
    is_heavy_rain_dep: int = Field(..., ge = 0, le=1, description="Boolean flag (0 or 1): Is there heavy rain at departure?", example=1)
    is_extreme_wind_arr: int = Field(..., ge = 0, le=1, description="Boolean flag (0 or 1): Is there extreme wind at arrival?", example=1)
    is_heavy_rain_arr: int = Field(..., ge = 0, le=1, description="Boolean flag (0 or 1): Is there heavy rain at arrival?", example=1)
    
    # --- Lag Features (Historical Delay) ---
    delay_lag_1: float = Field(..., description="Average delay on this route 1 month ago (in minutes).", example=5.4653)
    delay_lag_12: float = Field(..., description="Average delay on this route 12 months ago (in minutes).", example=5.2291)