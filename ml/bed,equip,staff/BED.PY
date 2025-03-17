import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from sklearn.preprocessing import MinMaxScaler
import pickle
import os
from datetime import datetime

scaler_path = r"H:\New folder (4)\tomodachi\ml\bed,equip,staff\scaler.pkl"
model_path = r"H:\New folder (4)\tomodachi\ml\bed,equip,staff\xyz.pkl"

features = [
    "Total_Admissions_Today",
    "Total_Discharges_Today",
    "Avg_LOS",
    "Avg_Age_Admissions_Today",
    "Total_Beds_Occupied_Today",
    "Is_Weekend"
]
target = "Total_Beds_Required_Tomorrow"

def load_model_and_scaler():
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
        
    with open(model_path, "rb") as f:
        model_json, weights = pickle.load(f)
    model = model_from_json(model_json)
    model.set_weights(weights)
    model.compile(loss="mse", optimizer="adam")
    
    print("✅ Loaded model and scaler.")
    return model, scaler

def predict_beds_required(new_data_dict, model=None, scaler=None):
    if model is None or scaler is None:
        model, scaler = load_model_and_scaler()
    
    new_data = pd.DataFrame([new_data_dict])
    new_data_with_dummy = pd.DataFrame([new_data_dict])
    new_data_with_dummy[target] = 0
    new_data_scaled = scaler.transform(new_data_with_dummy)
    new_data_scaled = new_data_scaled[:, :-1]
    new_data_reshaped = new_data_scaled.reshape(1, 1, len(features))
    predicted_scaled = model.predict(new_data_reshaped, verbose=0)
    input_and_prediction_scaled = np.append(new_data_scaled, predicted_scaled, axis=1)
    input_and_prediction = scaler.inverse_transform(input_and_prediction_scaled)
    predicted_beds = input_and_prediction[0, -1]
    
    return predicted_beds

def update_model_with_actual(actual_beds, today_data):
    df = pd.read_csv(r"H:\New folder (4)\tomodachi\ml\bed,equip,staff\bed_data.csv")
    
    date_column = None
    if "Date" in df.columns:
        date_column = "Date"
        df["Date"] = pd.to_datetime(df["Date"])
        df["Is_Weekend"] = df["Date"].dt.dayofweek.isin([5, 6]).astype(int)
    
    new_row = pd.DataFrame([today_data])
    new_row[target] = actual_beds
    
    if date_column:
        new_row[date_column] = datetime.now().date()
    
    if date_column:
        df_copy = df.copy()
        new_row_copy = new_row.copy()
    else:
        df_copy = df.copy()
        new_row_copy = new_row.copy()
    
    df_updated = pd.concat([df_copy, new_row_copy], ignore_index=True)
    df_updated.to_csv("bed_data.csv", index=False)
    
    scaler = MinMaxScaler()
    df_scaled = df_updated.copy()
    
    columns_to_scale = features.copy()
    if target not in columns_to_scale:
        columns_to_scale.append(target)
    
    df_scaled[columns_to_scale] = scaler.fit_transform(df_updated[columns_to_scale])
    
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    
    with open(model_path, "rb") as f:
        model_json, weights = pickle.load(f)
    model = model_from_json(model_json)
    model.set_weights(weights)
    model.compile(loss="mse", optimizer="adam")
    
    X_train = df_scaled[features].values.reshape(-1, 1, len(features))
    y_train = df_scaled[target].values
    
    model.fit(X_train, y_train, epochs=10, batch_size=16, verbose=1)
    
    model_json = model.to_json()
    weights = model.get_weights()
    with open(model_path, "wb") as f:
        pickle.dump((model_json, weights), f)
    
    print("✅ Model updated with new actual data.")
    return True

if __name__ == "__main__":
    model, scaler = load_model_and_scaler()
    
    today_data = {
        "Total_Admissions_Today": 45,
        "Total_Discharges_Today": 42,
        "Avg_LOS": 3.5,
        "Avg_Age_Admissions_Today": 30,
        "Total_Beds_Occupied_Today": 4000,
        "Is_Weekend": 1 if datetime.now().weekday() >= 5 else 0
    }
    
    predicted_beds = predict_beds_required(today_data, model, scaler)
    print(f"🛏️ Predicted Beds Required Tomorrow: {predicted_beds:.2f}")
    
    update_choice = input("Do you want to update the model with actual bed count? (y/n): ")
    if update_choice.lower() == 'y':
        actual_beds = float(input("Enter actual beds required for today: "))
        print(f"Predicted: {predicted_beds:.2f}, Actual: {actual_beds:.2f}")
        update_model_with_actual(actual_beds, today_data)
