import pandas as pd
from datetime import datetime, timedelta

# Load doctor data
doctor_df = pd.read_csv(r"H:\New folder (4)\tomodachi\doctor_data\DOCTOR_FULL_DATA.csv")

# Convert time columns to datetime format
def convert_time(df, cols):
    for col in cols:
        df[col] = pd.to_datetime(df[col], format="%H:%M:%S").dt.time
    return df

doctor_df = convert_time(doctor_df, ["firstshiftstart", "firstshiftend", "secondshiftstart", "secondshiftend"])

# Dictionary to store booked slots
booked_slots = {}

# Function to find available slots
def get_available_slots(doctor_id, shift_start, shift_end, cons_time, max_slots=4):
    available_slots = []
    start_time = datetime.combine(datetime.today(), shift_start)
    end_time = datetime.combine(datetime.today(), shift_end)
    
    while start_time + timedelta(minutes=cons_time) <= end_time:
        slot = (start_time.time(), (start_time + timedelta(minutes=cons_time)).time())
        if slot not in booked_slots.get(doctor_id, []):
            available_slots.append(slot)
        if len(available_slots) == max_slots:
            break
        start_time += timedelta(minutes=60)  # Move to next hour
    
    return available_slots

# Function to assign slots based on severity and consultation time
def assign_appointments(patients_df):
    patients_df = patients_df.sort_values(by="severity", ascending=False)  # Higher severity first
    
    for _, patient in patients_df.iterrows():
        department = patient["department"]
        severity = patient["severity"]
        cons_time = patient["cons_time"]
        
        # Get available doctors in the department
        available_doctors = doctor_df[doctor_df["department"] == department]
        assigned = False
        
        for _, doctor in available_doctors.iterrows():
            doctor_id = doctor["doctorid"]
            
            # Check both shifts
            for shift_start, shift_end in [(doctor["firstshiftstart"], doctor["firstshiftend"]),
                                           (doctor["secondshiftstart"], doctor["secondshiftend"])]:
                if pd.isna(shift_start) or pd.isna(shift_end):
                    continue
                
                available_slots = get_available_slots(doctor_id, shift_start, shift_end, cons_time)
                if available_slots:
                    print(f"Patient {patient['id']} (Severity {severity}) Suggested Slots: {available_slots}")
                    booked_slots.setdefault(doctor_id, []).extend(available_slots[:1])  # Book first selected slot
                    assigned = True
                    break
            if assigned:
                break

# Example patient data (Replace with actual patient dataset)
patients_data = pd.DataFrame({
    "id": [1, 2, 3],
    "department": ["Cardiology", "Neurology", "Cardiology"],
    "severity": [10, 8, 7],
    "cons_time": [26, 30, 20]
})

# Assign appointments
assign_appointments(patients_data)
