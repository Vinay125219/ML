import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
import joblib
import os
import json
from datetime import datetime

# Set up MLflow
mlflow.set_tracking_uri("file:../mlruns")
mlflow.set_experiment("housing_price_prediction")

def retrain_housing_model(new_data_path=None):
    """
    Retrain the housing price prediction model with new data
    """
    try:
        # Load data - use new data if provided, otherwise use existing
        if new_data_path and os.path.exists(new_data_path):
            print(f"🔄 Loading new data from {new_data_path}")
            df = pd.read_csv(new_data_path)
        else:
            print("🔄 Loading existing data")
            df = pd.read_csv("../data/housing.csv")
        
        X = df.drop("MedHouseVal", axis=1)
        y = df["MedHouseVal"]

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Create models directory if not exists (in project root)
        os.makedirs("../models", exist_ok=True)

        # Store model performance for comparison
        model_performance = {}

        def train_and_log_model(model, model_name):
            with mlflow.start_run(run_name=f"retrain_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
                model.fit(X_train, y_train)
                preds = model.predict(X_test)

                mse = mean_squared_error(y_test, preds)
                r2 = r2_score(y_test, preds)

                mlflow.log_param("model_name", model_name)
                mlflow.log_param("retrain_timestamp", datetime.now().isoformat())
                mlflow.log_metric("mse", mse)
                mlflow.log_metric("r2_score", r2)

                signature = infer_signature(X_test, preds)
                input_example = X_test.head(2)

                mlflow.sklearn.log_model(
                    sk_model=model,
                    artifact_path="model",
                    input_example=input_example,
                    signature=signature
                )

                # Save locally
                joblib.dump(model, f"../models/{model_name}.pkl")

                print(f"✅ {model_name} | MSE: {mse:.3f} | R2 Score: {r2:.3f} | Saved to ../models/{model_name}.pkl")
                
                # Store performance for comparison
                model_performance[model_name] = {
                    'mse': mse,
                    'r2': r2,
                    'run_id': run.info.run_id
                }

        # Train models
        train_and_log_model(LinearRegression(), "LinearRegression")
        train_and_log_model(DecisionTreeRegressor(max_depth=5), "DecisionTree")

        # Register the best model based on performance
        print("\n📊 Model Performance Comparison:")
        print("=" * 40)
        for model_name, metrics in model_performance.items():
            print(f"{model_name}: MSE={metrics['mse']:.3f}, R2={metrics['r2']:.3f}")

        # Find the best model (lower MSE, higher R2)
        best_model_name = min(model_performance.keys(), key=lambda x: model_performance[x]['mse'])
        best_metrics = model_performance[best_model_name]

        print(f"\n🏆 Best Model: {best_model_name}")
        print(f"   MSE: {best_metrics['mse']:.3f}")
        print(f"   R2 Score: {best_metrics['r2']:.3f}")

        # Register the best model
        try:
            registered_model = mlflow.register_model(
                model_uri=f"runs:/{best_metrics['run_id']}/model",
                name="HousingPricePredictor"
            )
            print(f"✅ Successfully registered 'HousingPricePredictor' model (version {registered_model.version})")
        except Exception as e:
            print(f"⚠️  HousingPricePredictor already registered or error: {e}")

        # Save retraining results
        retrain_results = {
            "retrain_timestamp": datetime.now().isoformat(),
            "best_model": best_model_name,
            "performance": best_metrics,
            "all_models": model_performance,
            "data_source": new_data_path if new_data_path else "existing_data"
        }
        
        with open("../retrain_results.json", "w") as f:
            json.dump(retrain_results, f, indent=2)
        
        print("✅ Retraining completed successfully!")
        return retrain_results

    except Exception as e:
        print(f"❌ Error during retraining: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    retrain_housing_model()
