from sklearn.datasets import fetch_california_housing
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os

def load_and_save():
    # Load the data
    data = fetch_california_housing(as_frame=True)
    df = data.frame

    # --- Preprocessing ---
    # Check and drop missing values (usually none in this dataset)
    df.dropna(inplace=True)

    # Separate features and target
    X = df.drop("MedHouseVal", axis=1)
    y = df["MedHouseVal"]

    # Feature Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Reconstruct the processed dataframe
    df_processed = pd.DataFrame(X_scaled, columns=X.columns)
    df_processed["MedHouseVal"] = y.reset_index(drop=True)

    # Get the project root directory (parent of src directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Save preprocessed data
    output_path = os.path.join(data_dir, "housing.csv")
    df_processed.to_csv(output_path, index=False)
    print(f"Preprocessed data saved to {output_path}")


if __name__ == "__main__":
    load_and_save()
