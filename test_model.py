import joblib

# Load the saved pickle model file
model_data = joblib.load("hospital_readmission_model.pkl")

print("--- Pickle File Loaded Successfully ---")
print("Keys inside pickle:", model_data.keys())
print("Model object:", model_data["model"])
print("Feature count:", len(model_data["features"]))
print("Threshold:", model_data["threshold"])