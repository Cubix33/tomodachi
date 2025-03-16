import pandas as pd
import numpy as np
import joblib
from statsmodels.tsa.statespace.sarimax import SARIMAX

df = pd.read_csv(r"H:\APT-project\predbed\equipment_data.csv")
df = df.apply(pd.to_numeric, errors='coerce')

lag_days = 3
for col in ["Total_Discharges_Today", "ICU_Admissions_Today", "Surgeries_Today", "Bed_Occupancy_Rate"]:
    for lag in range(1, lag_days + 1):
        df[f"{col}_lag{lag}"] = df[col].shift(lag)

df.dropna(inplace=True)

features = [
    'Total_Discharges_Today', 'ICU_Admissions_Today', 'Surgeries_Today', 'Bed_Occupancy_Rate'
] + [f"{col}_lag{lag}" for col in [
    "Total_Discharges_Today", "ICU_Admissions_Today", "Surgeries_Today", "Bed_Occupancy_Rate"
] for lag in range(1, lag_days + 1)]

targets = ["Patient_Monitors_Required", "Defibrillators_Required", "Infusion_Pumps_Required"]
def calculate_equipment_requirements(row):
    seasonal_factor = np.random.uniform(0.8, 1.2)
    icu_admissions = row["ICU_Admissions_Today"]
    surgeries_today = row["Surgeries_Today"]
    total_admissions = row["Total_Discharges_Today"]
    return pd.Series({
        "Patient_Monitors_Required": max(5, int(icu_admissions * 1.2 + surgeries_today * 0.5 + seasonal_factor)),
        "Defibrillators_Required": max(2, int(1.2 * surgeries_today + 0.7 * icu_admissions + 0.4 * total_admissions + seasonal_factor)),
        "Infusion_Pumps_Required": max(8, int(icu_admissions * 1.5 + total_admissions * 0.3 + seasonal_factor))
    })

df[targets] = df.apply(calculate_equipment_requirements, axis=1)

model_paths = {
    "Patient_Monitors_Required": r"predbed/arima_Patient_Monitors_Required.pkl",
    "Defibrillators_Required": r"H:\APT-project\predbed\arima_Defibrillators_Required.pkl",
    "Infusion_Pumps_Required": r"H:\APT-project\predbed\arima_Infusion_Pumps_Required.pkl"
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
