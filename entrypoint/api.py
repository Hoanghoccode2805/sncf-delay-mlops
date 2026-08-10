from fastapi import FastAPI, HTTPException
from entrypoint.schemas import SNCFDelayInput
from src.models.predict import SNCFDelayPredictor
from src.utils.logger import get_logger

logger = get_logger(__name__)

# --- API Documentation & Meta Data ---
API_DESCRIPTION = """
Welcome to the **SNCF Delay Prediction API**! 🚄

This API predicts the average delay (in minutes) for high-speed trains (TGV) based on historical data, weather conditions, and route characteristics.

### Supported Target Routes
Please note that this machine learning model was exclusively trained on and optimized for the following **5 specific routes**. 
You must input one of these exact departure and arrival combinations:

1. **CHAMBERY CHALLES LES EAUX** ➡️ **PARIS LYON**
2. **BELLEGARDE (AIN)** ➡️ **PARIS LYON**
3. **PARIS EST** ➡️ **STRASBOURG**
4. **PARIS LYON** ➡️ **MULHOUSE VILLE**
5. **DIJON VILLE** ➡️ **PARIS LYON**

*Warning: Entering any other station combinations outside of this list will result in invalid features and inaccurate predictions.*
"""

app = FastAPI(
    title="SNCF Delay Prediction API",
    description=API_DESCRIPTION,
    version="1.0.0"
)

# --- Initialize Model ---
RUN_ID = "e2ebbfbff1cc46d382156d40ba9e1493"
try:
    predictor = SNCFDelayPredictor(run_id=RUN_ID)
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    predictor = None

# --- Endpoints ---

@app.get("/", tags=["Health Check"])
def health_check():
    """
    Root endpoint to verify if the API is up and running.
    """
    return {"status": "success", "message": "SNCF MLOps API is running perfectly!"}


@app.post("/predict", tags=["Prediction"])
def predict_delay(data: SNCFDelayInput):
    """
    Takes route details, weather data, and historical lag features to predict the train delay.
    """
    if predictor is None:
        raise HTTPException(
            status_code=500, 
            detail="Model is not initialized. Please check server logs."
        )
    
    try:
        input_dict = data.model_dump()
        predicted_delay = predictor.predict(input_dict)
        
        return {
            "departure_station": input_dict["departure_station"],
            "arrival_station": input_dict["arrival_station"],
            "predicted_delay_minutes": predicted_delay,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))