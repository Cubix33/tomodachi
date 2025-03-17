import pandas as pd
from datetime import datetime, timedelta
import random

def load_doctor_data(file_path):
    doctor_data = pd.read_csv(file_path)
    time_columns = ["firstshiftstart", "firstshiftend", "secondshiftstart", "secondshiftend"]
    for col in time_columns:
        doctor_data[col] = pd.to_datetime(doctor_data[col], format="%H:%M:%S").dt.time
    return doctor_data

def find_best_schedule(id, patient_id, severity, consultation_time, department, doctor_data, booked_slots):
    consultation_duration = timedelta(minutes=consultation_time)
    max_gap = timedelta(minutes=5)
    available_doctors = doctor_data[doctor_data['department'] == department].copy()
    available_doctors = available_doctors.sort_values(by=['firstshiftstart'])
    for _, doctor in available_doctors.iterrows():
        doctor_id = doctor['doctorid']
        if doctor_id not in booked_slots:
            booked_slots[doctor_id] = []
        for shift_start, shift_end in [(doctor['firstshiftstart'], doctor['firstshiftend']),
                                       (doctor['secondshiftstart'], doctor['secondshiftend'])]:
            if pd.isna(shift_start) or pd.isna(shift_end):  
                continue
            current_time = datetime.combine(datetime.today(), shift_start)
            shift_end_time = datetime.combine(datetime.today(), shift_end)
            if booked_slots[doctor_id]:
                last_end_time = booked_slots[doctor_id][-1][1]
                last_end_time_dt = datetime.combine(datetime.today(), last_end_time)
                current_time = max(current_time, last_end_time_dt + max_gap)
            while current_time + consultation_duration <= shift_end_time:
                slot_start = current_time.time()
                slot_end = (current_time + consultation_duration).time()
                if all(not (s[0] <= slot_start < s[1] or s[0] < slot_end <= s[1]) for s in booked_slots[doctor_id]):
                    booked_slots[doctor_id].append((slot_start, slot_end))
                    return {
                        "id": id,
                        "Patient ID": patient_id,
                        "Doctor ID": doctor_id,
                        "severity": severity,
                        "Department": department,
                        "Scheduled Time": (datetime.combine(datetime.today()+ timedelta(days=2), slot_start), datetime.combine(datetime.today()+ timedelta(days=2), slot_end))
                    }
                current_time += timedelta(minutes=1)
    return {"Patient ID": patient_id, "Status": "No available slots"}




def scheduleAppointments(patients):
    doctor_data = load_doctor_data(r"C:\Users\prtyksh\Documents\ai4humanity\pythonBackend\aiStuff\csvs\DOCTOR_FULL_DATA.csv")
    booked_slots = {}
    schedules = []
    for patient in sorted(patients, key=lambda x: -x['severity']):
        schedules.append(find_best_schedule(patient['id'],patient["patient_id"], patient["severity"], 
                                            patient["consultation_time"], patient["department"], 
                                            doctor_data, booked_slots))

    return pd.DataFrame(schedules).to_dict(orient='records')
    