
from database import connectPostgres
from predictSeverityAndTime import getSeverityAndTime
from math import ceil
from scheduling import scheduleAppointments
from easygmail import Client, EmailBuilder

def sendEmail(emailClient, apptid, department):
    client = Client("", "")

    msg = EmailBuilder(
        receiver=emailClient, subject="Your Appointment Has Been Scheduled", body=f"Dear Patient, Your Appointment {apptid}, in department {department} has been scheduled, Please login to check more details. - APT"
    ).build()

    return client.send(msg)

with connectPostgres() as conn:
    with conn.cursor() as curr:
        
        print(">>> Postgres Connection Successful ")

        curr.execute('''
            SELECT
                    
                p.age,
                p.gender,
                p.medicalhistory,
                COALESCE(a.symptoms, '') AS symptoms,
                COALESCE(a.department, 'TBA') AS department,
                (
                    SELECT COUNT(*)
                    FROM appts ap
                    WHERE ap.patientid = p.id
                    AND lower(ap.timeperiod) < CURRENT_DATE
                ) AS previous_visits,
                a.id
            FROM patientsappt p
            INNER JOIN appts a
                ON a.patientid = p.id
            WHERE a.date = CURRENT_DATE + INTERVAL '2 days' AND a.severity = NULL;''')
        
        records = curr.fetchall()

        print(f">>> Fetched {len(records)}")

        for appt in records:
            severity, time = getSeverityAndTime(appt[0], 'Male' if appt[1] == 'M' else 'Female', appt[5], appt[3], appt[2], appt[4] )
            
            curr.execute("UPDATE appts SET severity = %s, time = %s WHERE id = %s", (ceil(severity), ceil(time), appt[-1]))
            conn.commit()
            print(f">>> Processed Appt ID: {appt[-1]} w/ Severity:{severity}, Time: {time}")
        
        print(">>> Finished Adding Severity and Predicted Time For All Appointments.")


        # Now Moving On To Scheduling Them
        curr.execute("SELECT a.id, a.patientid, a.severity, a.time, a.department, p.email FROM appts a JOIN patientsappt p ON a.patientid = p.patientid WHERE a.date = CURRENT_DATE + INTERVAL '2 days';")
        records = curr.fetchall()

        print(f">>> Fetched {len(records)}")
        toSend = []
        for appt in records:
            toSend.append(
                {
                    'id': appt[0],
                    'patient_id': appt[1],
                    'severity': appt[2],
                    'consultation_time': appt[3],
                    'department': appt[4],
                    'email': appt[5]
                }
            )
        for record in scheduleAppointments(toSend):
            start_time, end_time = record['Scheduled Time']
            curr.execute("UPDATE appts SET doctorid = %s, timeperiod = tsrange(%s, %s, '[)') WHERE id = %s", (record["Doctor ID"], start_time, end_time, record['id']))
            conn.commit()

            sendEmail( record['email'], 9, record['department'])
            
            print(f">>> Scheduled Appt {record['id']}")