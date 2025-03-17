import csv
from datetime import date, datetime
from database import connectPostgres
from bed import getPredictedBeds
from staff import getStaffPredictions
from equipment import getEquipmentPredictions
today= date.today()
from math import ceil
import os

def checkIfDataAlreadyNotPresent(file, today):
    with open(file, "rb") as f:
        f.seek(-2, os.SEEK_END)  
        
        while f.read(1) != b"\n":
            f.seek(-2, os.SEEK_CUR) 
        
        last = f.readline().decode().strip()  
        
    last_date = last.split(",")[0]
    
    return last_date != today  

def updateBedDataCSVandgetPredictedValueForTomorrow():
    if checkIfDataAlreadyNotPresent(r"C:\Users\prtyksh\Documents\ai4humanity\pythonBackend\aiStuff\csvs\bed_data.csv", datetime.now().strftime("%d:%m:%Y")):
        with connectPostgres() as conn:
            with conn.cursor() as curr:
                
                curr.execute("""
                SELECT
                             (SELECT COUNT(*) FROM admissions WHERE admissiondate = CURRENT_DATE ) AS totalAddms,

                             (SELECT COUNT(*) FROM admissions WHERE dischargedate = CURRENT_DATE ) AS totalDischarges,

                             (SELECT AVG(dischargedate - admissiondate) FROM admissions WHERE dischargeDate = CURRENT_DATE ) AS avgLOS,

                             (SELECT AVG(age) FROM admissions WHERE admissiondate = CURRENT_DATE ) AS avgAge,

                             (SELECT COUNT(*) FROM admissions WHERE  admissiondate <= CURRENT_DATE  AND (dischargedate IS NULL OR dischargedate >= CURRENT_DATE )) as totalBedsOccupuied,
                            
                             (SELECT required FROM bedhistorialdata WHERE date = CURRENT_DATE) AS requiredBeds;

                """)

                row =  [int(value)  for value in list(curr.fetchone())]
                row.insert(0, datetime.now().strftime("%d:%m:%Y"))
                row.insert(1, True if datetime.now().weekday() >= 5 else False)

                with open(r"C:\Users\prtyksh\Documents\ai4humanity\pythonBackend\aiStuff\csvs\bed_data.csv", "a", newline='') as f:
                    writerCSV = csv.writer(f)
                    writerCSV.writerow(row)

                print(">>> Wrote in CSV, Today's Data.")

                predictedBeds = int(getPredictedBeds())
                curr.execute("UPDATE bedhistorialdata set predicted = %s WHERE date = CURRENT_DATE + 1", (predictedBeds, ))
                conn.commit()

                print(">>> Inserted Predicted Value Of Beds For Tomorrow")
    else:
        print("Already Present!")

def updateStaffDataCSVandgetPredictions():
    if checkIfDataAlreadyNotPresent(r"C:\Users\prtyksh\Documents\ai4humanity\pythonBackend\aiStuff\csvs\staff_data.csv", datetime.now().strftime("%d:%m:%Y")):
        with connectPostgres() as conn:
            with conn.cursor() as curr:
                
                curr.execute("""
                    SELECT
                (SELECT COUNT(*) FROM admissions WHERE admissiondate =  CURRENT_DATE ) AS Total_Admissions_Today,
                (SELECT COUNT(*) FROM admissions WHERE dischargedate =  CURRENT_DATE ) AS Total_Discharges_Today,
                (SELECT COUNT(*) FROM icuAddms WHERE startDate <=  CURRENT_DATE  AND (endDate IS NULL OR endDate >=  CURRENT_DATE )) AS ICU_Patients_Today,
                (SELECT COUNT(*) FROM surgeries WHERE date =  CURRENT_DATE ) AS Surgeries_Today,
                (SELECT COUNT(*) FROM admissions WHERE admissiondate <=  CURRENT_DATE  AND (dischargedate IS NULL OR dischargedate >=  CURRENT_DATE )) AS Total_Beds_Occupied_Today,
                (SELECT doctorsrequired FROM staff WHERE date =  CURRENT_DATE ) AS Doctors_Required_Tomorrow,
                (SELECT nursesrequired FROM staff WHERE date =  CURRENT_DATE ) AS Nurses_Required_Tomorrow,
                (SELECT techniciansrequired FROM staff WHERE date =  CURRENT_DATE ) AS Technicians_Required_Tomorrow""")

                row =  [int(value)  for value in list(curr.fetchone())]
                row.insert(0, datetime.now().strftime("%d:%m:%Y"))
                row.insert(1, True if datetime.now().weekday() >= 5 else False)


                with open(r"C:\Users\prtyksh\Documents\ai4humanity\pythonBackend\aiStuff\csvs\staff_data.csv", "a", newline='') as f:
                    writerCSV = csv.writer(f)
                    writerCSV.writerow(row)

                print(">>> Wrote Into Staff.CSV, today's details")
                
                result = getStaffPredictions()
                for key in result:
                    result[key] = ceil(result[key])

                print(result)

                curr.execute("UPDATE staff set doctorsaipredict = %s, nursesaipredict = %s, techniciansaipredict = %s WHERE date = CURRENT_DATE + 1", (result['Doctor_Required'], result['Nurse_Required'], result['Technicians_Required'] ) )
                conn.commit()

                print(">>> Predicted Staff Details For Tomorrow")
    else:
        print("Already Present!")

def updateEquipmentsCSVandgetPredictions():
    # Assuming Total Beds To Be 700
    if checkIfDataAlreadyNotPresent(r"C:\Users\prtyksh\Documents\ai4humanity\pythonBackend\aiStuff\csvs\equipment_data.csv", datetime.now().strftime("%d:%m:%Y") ):
        with connectPostgres() as conn:
            with conn.cursor() as curr:
                
                curr.execute("""SELECT

                            (SELECT COUNT(*) FROM admissions WHERE admissiondate = CURRENT_DATE) AS Total_Admissions_Today,

                            (SELECT COUNT(*) FROM admissions WHERE dischargedate = CURRENT_DATE) AS Total_Discharges_Today,

                            (SELECT COUNT(*) FROM icuAddms WHERE startDate <= CURRENT_DATE AND (endDate IS NULL OR endDate >= CURRENT_DATE)) AS ICU_Admissions_Today,
                            (SELECT COUNT(*) FROM surgeries WHERE date = CURRENT_DATE) AS Surgeries_Today,


                            (SELECT COUNT(*) FROM admissions WHERE admissiondate <= CURRENT_DATE AND (dischargedate IS NULL OR dischargedate >= CURRENT_DATE))::float / 700 AS Bed_Occupancy_Rate,


                            (SELECT patientmonitorsrequired FROM equipments WHERE date = CURRENT_DATE ) AS Patient_Monitors_Required,

                            (SELECT defibrequired  FROM equipments WHERE date = CURRENT_DATE ) AS Defibrillators_Required,

                            (SELECT infusionpumpsrequired FROM equipments WHERE date = CURRENT_DATE ) AS Infusion_Pumps_Required;

                """)

                row =  [int(value)  for value in list(curr.fetchone())]
                row.insert(0, datetime.now().strftime("%d:%m:%Y"))
                row.insert(1, True if datetime.now().weekday() >= 5 else False)

                with open("C:\Users\prtyksh\Documents\ai4humanity\pythonBackend\aiStuff\csvs\equipment_data.csv", "a", newline='') as f:
                    writerCSV = csv.writer(f)
                    writerCSV.writerow(row)
                
                result = getEquipmentPredictions()
                for key in result:
                    result[key] = ceil(result[key])

                curr.execute("UPDATE equipments SET patientmonitorsaipredict = %s, defibaipredict = %s, infusionpumpsaipredict = %s WHERE date = CURRENT_DATE + 1;", (result['Patient_Monitors_Required'], result['Defibrillators_Required'], result['Infusion_Pumps_Required'] ))
                conn.commit()

                print(">>> Predicted Equipment Details For Tomorrow")
    else:
        print("Already Present!")

    
# updateBedDataCSVandgetPredictedValueForTomorrow()
# updateStaffDataCSVandgetPredictions()
# updateEquipmentsCSVandgetPredictions()