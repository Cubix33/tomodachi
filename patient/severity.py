import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
df = pd.read_csv("data.csv")

df.drop(columns=['Base_Severity', 'Department_Name'], inplace=True)

symptom_encoder = LabelEncoder()
df['Symptoms'] = symptom_encoder.fit_transform(df['Symptoms'])

dept_encoder = LabelEncoder()
df['Department'] = dept_encoder.fit_transform(df['Department'])

df.to_csv("processed_data.csv", index=False)

print("Processed data saved as processed_data.csv")
print(df.head())

X_severity = df[['Age', 'Gender', 'Previous_Visits', 'Symptoms','Prev_Severity']]
y_severity = df['Severity_Score']

X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X_severity, y_severity, test_size=0.2, random_state=42)

severity_model = XGBRegressor(n_estimators=1000, learning_rate=0.1, max_depth=5, random_state=42)
severity_model.fit(X_train_s, y_train_s)

y_pred_s = severity_model.predict(X_test_s)
print("\n🔹 Severity Prediction Metrics:")
print("MAE:", mean_absolute_error(y_test_s, y_pred_s))
print("R2 Score:", r2_score(y_test_s, y_pred_s))
with open("severity_model.pkl", "wb") as f:
    pickle.dump(severity_model, f)
print("Severity model saved as severity_model.pkl")
df['Predicted_Severity'] = severity_model.predict(X_severity)

X_time = df[['Predicted_Severity', 'Department','Age', 'Gender', 'Previous_Visits', 'Symptoms']]
y_time = df['Consultation_Time']

X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(X_time, y_time, test_size=0.2, random_state=42)

time_model = XGBRegressor(n_estimators=200, learning_rate=0.1, max_depth=3, random_state=42)
time_model.fit(X_train_t, y_train_t)

y_pred_t = time_model.predict(X_test_t)
print("\n🔹 Consultation Time Prediction Metrics:")
print("MAE:", mean_absolute_error(y_test_t, y_pred_t))
print("R2 Score:", r2_score(y_test_t, y_pred_t))
with open("time_model.pkl", "wb") as f:
    pickle.dump(time_model, f)
print("Consultation time model saved as time_model.pkl")