import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import model_from_json
import pickle
from sklearn.preprocessing import MinMaxScaler
import os

df = pd.read_csv("bed_data.csv")

if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"])
    df["Is_Weekend"] = df["Date"].dt.dayofweek.isin([5, 6]).astype(int)
    df.set_index("Date", inplace=True)

features = [
    "Total_Admissions_Today", "Total_Discharges_Today", "Avg_LOS",
    "Avg_Age_Admissions_Today", "Total_Beds_Occupied_Today", "Is_Weekend"
]
target = "Total_Beds_Required_Tomorrow"

scaler = MinMaxScaler()
df_scaled = df.copy()
df_scaled[features[:-1] + [target]] = scaler.fit_transform(df[features[:-1] + [target]])
df_scaled[features + [target]] = df_scaled[features + [target]].astype(np.float32)

seq_length = 10

def create_sequences(data, seq_length=10):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data.iloc[i:i+seq_length][features].values)
        y.append(data.iloc[i+seq_length][target])
    return np.array(X), np.array(y)

model_path = r"H:\APT-project\predbed\lstm_bed_prediction.pkl"
if os.path.exists(model_path):
    with open(model_path, "rb") as f:
        model_json, weights = pickle.load(f)
    model = model_from_json(model_json)
    model.set_weights(weights)
    model.compile(loss='mse', optimizer='adam')
    print("Loaded existing model.")
else:
    raise FileNotFoundError("Saved model not found!")

latest_data = df_scaled.iloc[-seq_length:][features].values.reshape(1, seq_length, len(features))
predicted_scaled = model.predict(latest_data)

predicted_full = np.zeros((1, len(features)))
predicted_full[:, -1] = predicted_scaled.flatten()
predicted_beds = scaler.inverse_transform(predicted_full)[:, -1][0]

print(f"Predicted Beds for Tomorrow: {predicted_beds:.2f}")
#UPDATE YOUR DATASET HERE AT END OF DAY WITH ACTUAL DATA

def update_model_with_actual(actual_beds):
    global df_scaled
    new_data = df.iloc[-1:].copy()
    new_data[target] = actual_beds

    new_data_scaled = new_data.copy()
    new_data_scaled[features[:-1] + [target]] = scaler.transform(new_data[features[:-1] + [target]])
    df_scaled = pd.concat([df_scaled, new_data_scaled])

    X_train, y_train = create_sequences(df_scaled, seq_length)
    model.fit(X_train, y_train, epochs=10, batch_size=16, verbose=1)

    model_json = model.to_json()
    weights = model.get_weights()
    with open(model_path, "wb") as f:
        pickle.dump((model_json, weights), f)
    print("Model updated with new data.")

actual_beds = float(input("Enter actual beds required for today: "))
print(f"Predicted: {predicted_beds:.2f}, Actual: {actual_beds:.2f}")
update_model_with_actual(actual_beds)
