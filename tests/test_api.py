import pytest
from fastapi.testclient import TestClient
import httpx
from entrypoint.api import app

# Initialize the TestClient with our FastAPI app
client = TestClient(app)

def test_heath_check():
    """
    Scenario 1: Test if the server is awake and responding to basic requests.
    """
    response = client.get("/")

    # Assert HTTP status code is 200 (OK)
    assert response.status_code == 200 

    # Assert the JSON response matches our exact expectation
    expected_response = {"status": "success", "message": "SNCF MLOps API is running perfectly!"}
    assert response.json() == expected_response

def test_predict_success():
    """
    Scenario 2: Send a perfectly formatted JSON payload to the /predict endpoint.
    The model should return a 200 OK status and a float value for the delay.
    """
    valid_payload = {
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
    response = client.post("/predict", json = valid_payload)

    # Check that the API successfully processed the data
    assert response.status_code == 200 

    # Extract the JSON body
    data = response.json()

    # Verify the structure and data types of the response
    assert data["status"] == "success"
    assert data["departure_station"] == "BELLEGARDE (AIN)"
    assert "predicted_delay_minutes" in data
    assert isinstance(data["predicted_delay_minutes"], float)

def test_predict_validation_error():
    """
    Scenario 3: Send 'Garbage Data' to test the Pydantic firewall.
    We will inject an invalid station, negative duration, and invalid month.
    The API MUST block this and return a 422 Unprocessable Entity code.
    """

    invalid_payload = {
        "departure_station": "HO CHI MINH CITY", # INVALID: Not in the 5 target routes
        "arrival_station": "PARIS LYON",
        "avg_journey_duration": -50.0, # INVALID: Cannot be negative
        "nb_planned_trains": 259.0,
        "nb_cancelled_trains": 3.0,
        "departure_temp_mean": 5.59,
        "departure_precip_sum": 283.5,
        "departure_wind_max": 19.52,
        "arrival_temp_mean": 7.15,
        "arrival_precip_sum": 130.3,
        "arrival_wind_max": 46.35,
        "year": 2018,
        "month": 15, # INVALID: Month must be <= 12
        "season": 4,
        "temp_diff_route": 1.56,
        "is_extreme_wind_dep": 0,
        "is_heavy_rain_dep": 1,
        "is_extreme_wind_arr": 1,
        "is_heavy_rain_arr": 1,
        "delay_lag_1": 5.4653,
        "delay_lag_12": 5.2291
    }

    response = client.post("/predict", json = invalid_payload)

    # Check that the firewall successfully blocked the request
    response.status_code == 422
    
    # Verify that multiple validation errors were caught
    errors = response.json()["detail"]
    assert len(errors) >= 1

