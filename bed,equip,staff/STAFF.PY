import pandas as pd
import numpy as np
import joblib
from statsmodels.tsa.statespace.sarimax import SARIMAX

df = pd.read_csv(r"predbed\staff_data.csv")

df = df.apply(pd.to_numeric, errors='coerce')
if 'Is_Weekend' in df.columns:
    df['Is_Weekend'] = df['Is_Weekend'].astype(int)

lag_days = 3
for col in ["Total_Admissions_Today", "Total_Discharges_Today", "ICU_Patients_Today", "Total_Beds_Occupied_Today"]:
    for lag in range(1, lag_days + 1):
        df[f"{col}_lag{lag}"] = df[col].shift(lag)

# Drop rows with NaN due to lagging
df.dropna(inplace=True)

features = [
    'Total_Admissions_Today', 'Total_Discharges_Today',
    'ICU_Patients_Today', 'Total_Beds_Occupied_Today', 'Is_Weekend'
] + [f"{col}_lag{lag}" for col in [
    "Total_Admissions_Today", "Total_Discharges_Today", "ICU_Patients_Today", "Total_Beds_Occupied_Today"
] for lag in range(1, lag_days + 1)]

targets = ["Doctors_Required_Tomorrow", "Nurses_Required_Tomorrow", "Technicians_Required_Tomorrow"]



model_paths = {
    "Doctor_Required": r"H:\APT-project\predbed\arima_Doctors_Required_Tomorrow.pkl",
    "Nurse_Required": r"H:\APT-project\predbed\arima_Nurses_Required_Tomorrow.pkl",
    "Technicians_Required": r"H:\APT-project\predbed\arima_Technicians_Required_Tomorrow.pkl"
}

models = {target: joblib.load(path) for target, path in model_paths.items()}

def predict_equipment_requirements(models, latest_data):
    predictions = {}
    exog_df = latest_data[features]
    
    for target, model in models.items():
        try:
            forecast = model.get_forecast(steps=1, exog=exog_df)
            predictions[target] = forecast.predicted_mean.iloc[0]
        except Exception as e:
            print(f"Prediction error for {target}: {e}")
            predictions[target] = None
    
    return predictions

latest_data = df.iloc[[-1]]

predictions = predict_equipment_requirements(models, latest_data)

print("\nNext Day Equipment Predictions:")
for equip, value in predictions.items():
    if value is not None:
        print(f"{equip}: {value:.2f}")
    else:
        print(f"{equip}: Prediction failed.")


#UPDATE YOUR DATASET HERE AT END OF DAY WITH ACTUAL DATA
def update_model_with_actual(models, new_data):
    for target, model in models.items():
        try:
            new_actual_value = new_data[target].values[0]
            new_exog = new_data[features].values
            model = model.extend([new_actual_value], exog=new_exog)
            model_path = f"arima_{target.replace(' ', '_')}.pkl"
            joblib.dump(model, model_path)
            print(f"Updated model for {target} with actual value: {new_actual_value:.2f}")
        except Exception as e:
            print(f"Error updating model for {target}: {e}")

# latest_data = df.iloc[[-1]].copy()
# update_model_with_actual(models, latest_data)
# print(latest_data)
