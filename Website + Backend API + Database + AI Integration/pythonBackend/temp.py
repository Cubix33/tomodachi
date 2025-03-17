import csv
from datetime import datetime, timedelta
from database import connectPostgres  # Your DB connection!

# CSV file path
CSV_FILE = r"C:\Users\prtyksh\Documents\ai4humanity\pythonBackend\aiStuff\csvs\equipment_data.csv"

# Start and end dates
start_date = datetime(2025, 3, 1)
end_date = datetime(2025, 3, 16)

# Open DB connection
with connectPostgres() as conn:
    with conn.cursor() as curr:

        # Iterate through the dates
        current_date = start_date
        while current_date <= end_date:

            # Format date for CSV
            date_str = current_date.strftime("%d:%m:%Y")
            is_weekend = current_date.weekday() >= 5  # Saturday=5, Sunday=6

            # Execute SQL query for the current date
            curr.execute("""
                SELECT
                    (SELECT COUNT(*) FROM admissions WHERE admissiondate = %s) AS Total_Admissions_Today,

                    (SELECT COUNT(*) FROM admissions WHERE dischargedate = %s) AS Total_Discharges_Today,

                    (SELECT COUNT(*) FROM icuAddms 
                     WHERE startDate <= %s 
                     AND (endDate IS NULL OR endDate >= %s)) AS ICU_Admissions_Today,

                    (SELECT COUNT(*) FROM surgeries WHERE date = %s) AS Surgeries_Today,

                    (SELECT COUNT(*) FROM admissions 
                     WHERE admissiondate <= %s 
                     AND (dischargedate IS NULL OR dischargedate >= %s))::float / 700 AS Bed_Occupancy_Rate,

                    (SELECT patientmonitorsrequired FROM equipments WHERE date = %s) AS Patient_Monitors_Required,

                    (SELECT defibrequired FROM equipments WHERE date = %s) AS Defibrillators_Required,

                    (SELECT infusionpumpsrequired FROM equipments WHERE date = %s) AS Infusion_Pumps_Required;
            """, (
                current_date,  # admissions admissiondate
                current_date,  # admissions dischargedate
                current_date,  # icuAddms startDate
                current_date,  # icuAddms endDate
                current_date,  # surgeries date
                current_date,  # admissions admissiondate <=
                current_date,  # admissions dischargedate >=
                current_date,  # equipment for tomorrow
                current_date,  # equipment for tomorrow
                current_date   # equipment for tomorrow
            ))

            result = curr.fetchone()

            if result is None:
                print(f">>> No data found for {date_str}, skipping.")
                current_date += timedelta(days=1)
                continue

            # Convert values, handle NULLs (None)
            row = [round(val, 2) if isinstance(val, float) else (int(val) if val is not None else 0) for val in result]

            # Prepend date and is_weekend to the row
            row.insert(0, is_weekend)
            row.insert(0, date_str)

            # Write to CSV
            with open(CSV_FILE, "a", newline='') as f:
                writerCSV = csv.writer(f)
                writerCSV.writerow(row)

            print(f">>> Wrote to CSV for {date_str}: {row}")

            # Move to the next day
            current_date += timedelta(days=1)

print(">>> Completed filling equipment_data.csv.")
