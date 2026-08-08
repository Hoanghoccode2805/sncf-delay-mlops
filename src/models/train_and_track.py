import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.compose import TransformedTargetRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, root_mean_squared_error
import yaml
from pathlib import Path
from config.config import DATA_TRAIN
import mlflow
import mlflow.sklearn

# Load params of model from file yaml
def load_params(params_name="params.yaml"):
    base_dir = Path(__file__).resolve().parents[2]
    params_path = base_dir / "config" / params_name
    
    with open(params_path, "r") as f:
        return yaml.safe_load(f)

def load_data():
    return pd.read_csv(DATA_TRAIN)

def train_and_tune_model(model_name, model, param_grid, X_train, y_train):
    print(f"Currently training and searching for optimal parameters for: {model_name} ...")

    grid_search = GridSearchCV(
        estimator = model,
        param_grid= param_grid, # Bộ tham số 
        cv = 3, # Số lần đánh giá using Cross-Validation
        scoring= 'neg_mean_squared_error',
        n_jobs= -1
    )

    grid_search.fit(X_train,y_train)
    print(f"[SUCCESS] Best parameters for {model_name}: {grid_search.best_params_}")
    
    # Returns the best trained model.
    return grid_search.best_estimator_, grid_search.best_params_

def evaluate_model(model_name, model, X_test, y_test):
    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    print(f"\n[EVALUATION] Results of {model_name} on the test set:")
    print(f"- MSE: {mse:.4f}")
    print(f"- MAE: {mae:.4f}")
    print(f"- RMSE: {rmse:.4f}")
    print("-" * 40)

    return {"MSE": mse, "RMSE": rmse, "MAE": mae}

def main():
    # 0. Initialize MLflow Experiment
    mlflow.set_experiment("SNCF_Delay_Prediction_Master")

    # 1. Load params and data
    params = load_params()
    df = load_data()

    # HANDLE STRING/CATEGORICAL DATA (Crucial step)
    # Drop 'date' column as it cannot be processed by the model
    df = df.drop(columns=['date'], errors='ignore')
    
    # One-Hot Encoding for categorical variables (Stations)
    categorical_cols = df.select_dtypes(include=['object', 'string']).columns
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    # 2. Prepare X,y
    X = df.drop(columns= ["avg_delay_all_trains_arrival"], errors='ignore')
    y = df["avg_delay_all_trains_arrival"]

    # 3. Split x,y based on params.yaml
    train_end_year = params['train']['train_end_year']
    test_start_year = params['train']['test_start_year']

    X_train = X[df["year"] <= train_end_year]
    y_train = y[df["year"] <= train_end_year]
    X_test = X[df["year"] >= test_start_year]
    y_test = y[df["year"] >= test_start_year]

    # 4. Model configuration
    MODELS = {
        "Ridge_Regression": TransformedTargetRegressor(
            regressor=Ridge(), 
            func=np.log1p,       # Automatically transform y -> log(y + 1) during training
            inverse_func=np.expm1 # Automatically invert e^(y') - 1 when returning the result
        ),
        
        "Random_Forest": RandomForestRegressor(random_state=params['train']['random_state']),

        "XGBoost": XGBRegressor(random_state=params['train']['random_state'], objective='reg:squarederror')
    }

    model_performances = {}

    # 5. Train -> Evaluate Loop -> MLflow Tracking Loop
    for model_name, base_model in MODELS.items():
        param_grid = params['models'][model_name]

        # Start MLflow tracking run for each model
        with mlflow.start_run(run_name=model_name):
            
            # Step 1: Train and Tune
            best_model, best_params = train_and_tune_model(model_name, base_model, param_grid, X_train, y_train)
            
            # Step 2: Evaluate
            metrics = evaluate_model(model_name, best_model, X_test, y_test)
            model_performances[model_name] = metrics 

            # Step 3: MLFLOW TRACKING
            mlflow.log_params(best_params) # Log the best hyperparameters
            mlflow.log_metrics(metrics)    # Log the evaluation metrics
            mlflow.sklearn.log_model(
                best_model, 
                f"model_{model_name}", 
                serialization_format="cloudpickle"
            )

    # 6. Summarize and compare to determine the best model (based on the lowest RMSE)
    print("\n[SUMMARY] MODEL LEADERBOARD (Based on lowest RMSE):")
    best_rmse = float('inf')
    best_model_name = ""

    for name, metrics in model_performances.items():
        print(f"{name.ljust(20)} | RMSE: {metrics['RMSE']:.4f} | MAE: {metrics['MAE']:.4f}")
        if metrics['RMSE'] < best_rmse:
            best_rmse = metrics['RMSE']
            best_model_name = name
            
    print(f"\n=> The winning model is: {best_model_name} with RMSE = {best_rmse:.4f}")

if __name__ == "__main__":
    main()