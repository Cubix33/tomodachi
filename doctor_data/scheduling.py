import pandas as pd
from datetime import datetime, timedelta

def format_time(time_obj):
    """Format time object to a readable string with AM/PM."""
    return time_obj.strftime("%I:%M %p").lstrip("0")  # Remove leading zeros

def load_doctor_data(file_path):
    doctor_data = pd.read_csv(file_path)

    # Convert shift timings to datetime.time format
    time_columns = ["firstshiftstart", "firstshiftend", "secondshiftstart", "secondshiftend"]
    for col in time_columns:
        doctor_data[col] = pd.to_datetime(doctor_data[col], format="%H:%M:%S").dt.time

    return doctor_data

def find_available_slots(doctor_data, patient_severity, consultation_time, department):
    """Finds available slots for a patient based on severity and consultation time."""
    
    # Filter doctors based on department
    available_doctors = doctor_data[doctor_data['department'] == department]
    
    suggested_slots = []
    
    for _, doctor in available_doctors.iterrows():
        doctor_id = doctor['doctorid']
        slots = []
        
        # Generate slots for first shift
        start_time = datetime.combine(datetime.today(), doctor['firstshiftstart'])
        end_time = datetime.combine(datetime.today(), doctor['firstshiftend'])
        
        while start_time + timedelta(minutes=consultation_time) <= end_time:
            slots.append((start_time.time(), (start_time + timedelta(minutes=consultation_time)).time()))
            start_time += timedelta(minutes=60)  # Move to the next hour
        
        # If doctor has a second shift
        if pd.notna(doctor['secondshiftstart']) and pd.notna(doctor['secondshiftend']):
            start_time = datetime.combine(datetime.today(), doctor['secondshiftstart'])
            end_time = datetime.combine(datetime.today(), doctor['secondshiftend'])
            
            while start_time + timedelta(minutes=consultation_time) <= end_time:
                slots.append((start_time.time(), (start_time + timedelta(minutes=consultation_time)).time()))
                start_time += timedelta(minutes=60)  # Move to the next hour
        
        # Select top 4 slots based on severity
        slots = sorted(slots)[:4]
        if slots:
            suggested_slots.append((doctor_id, slots))
    
    return suggested_slots

# Load doctor data
file_path = r"H:\New folder (4)\tomodachi\doctor_data\DOCTOR_FULL_DATA.csv"
doctor_data = load_doctor_data(file_path)

# Example patient data
patients = [
    {'patient_id': 1, 'severity': 10, 'consultation_time': 26, 'department': 'Cardiology'},
    {'patient_id': 2, 'severity': 7, 'consultation_time': 20, 'department': 'Neurology'}
]

# Generate appointment slots with better formatting
for patient in patients:
    slots = find_available_slots(doctor_data, patient['severity'], patient['consultation_time'], patient['department'])
    print(f"\nPatient {patient['patient_id']} (Severity {patient['severity']}, Department: {patient['department']})")
    print("Suggested Appointment Slots:")
    
    for doctor_id, slot_list in slots:
        print(f"\n  Doctor {doctor_id}:")
        for i, (start, end) in enumerate(slot_list, 1):
            print(f"    Slot {i}: {format_time(start)} to {format_time(end)}")
