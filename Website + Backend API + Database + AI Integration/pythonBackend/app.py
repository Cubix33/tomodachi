from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
import bcrypt
from database import connectPostgres
from datetime import datetime as dt
from datetime import date, timedelta

def getTime(dateStr):
    startStr, endStr = dateStr.strip("[]()").split(",")
    startStr = startStr.strip()
    endStr = endStr.strip()
    startDate, endDate = dt.strptime(startStr,"%Y-%m-%d %H:%M:%S" ), dt.strptime(endStr,"%Y-%m-%d %H:%M:%S" )

    return startDate.strftime("%d %B %Y"), startDate.strftime("%I:%M %p"), endDate.strftime("%I:%M %p")

# Some Initializors
app = Flask(__name__)
CORS(app)
SECRET_KEY = 'FyodorDostoyevsky'

# Hashing Passwds With bcrypt
def hashPasswd(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Checking Hashed Passwds
def checkPasswd(password, hashedPassword):
    return bcrypt.checkpw(password.encode('utf-8'), hashedPassword.encode('utf-8'))

# Generate JSON Web Tokens
def createJWT(id):
    payload = {
        'id': id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
     

# Decode JWTs
def decodeAndVerifyJWT(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  
    except jwt.InvalidTokenError:
        return None  

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email == '' or password == '':
        return jsonify({'error': 'Email and Password Are Required'}), 400
    
    with connectPostgres() as conn:
        with conn.cursor() as curr:
            curr.execute(f"SELECT id, passwordhash FROM patientsappt WHERE email = '{email}' ")
            passwordHash = curr.fetchone()
            if passwordHash != None:
                if checkPasswd(password, passwordHash[1]):

                    return jsonify({"jwt": createJWT(passwordHash[0]) }), 200
                else:
                    return jsonify({'message': "Invalid Passwd or Email"}), 500
            else:
                return jsonify({'message':"Invalid Password Or Email"}), 500


@app.route("/signup", methods=['POST'])
def signup():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    gender = data.get('gender')
    age = data.get('age')
    medicalHistory = data.get("medicalHistory")

    if email == '' or password == '' or gender == '' or name == '' or age == '':
        return jsonify({'message': 0}), 400
    
    with connectPostgres() as conn:
        with conn.cursor() as curr:
            curr.execute(f"SELECT EXISTS (SELECT 1 FROM patientsappt WHERE email = '{email}' )")
            if curr.fetchone()[0] == True:
                return jsonify({'message':"Email Already Exists"}), 500
            else:

                curr.execute(f"INSERT INTO patientsappt (name, age, gender, passwordhash, email, medicalhistory) VALUES (%s, %s, %s, %s, %s, %s)", (name, age, gender, hashPasswd(password), email, medicalHistory))
                conn.commit()
                return jsonify({'message':7}), 200


@app.route('/getPatientDetails', methods=['GET'])
def getPatientDetails():
    authorizationHead = request.headers.get('Authorization')

    if not authorizationHead or not authorizationHead.startswith("Bearer "):
        return jsonify({"error": "Something's Wrong with Your Auth"})

    token = authorizationHead.split(' ')[1]
    payload = decodeAndVerifyJWT(token)

    if payload == None:
        return jsonify({"error": "User not Authorized to perform this action"}), 401

    print(payload)
    id = payload['id']

    toReturn = {}
    with connectPostgres() as conn:
        with conn.cursor() as curr:
            curr.execute("SELECT  name, age, gender FROM patientsappt WHERE id = %s", (id,))
            data = curr.fetchone()
            
            toReturn['id'] = id
            toReturn['name'] = data[0]
            toReturn['age'] = data[1]
            toReturn['gender'] = "Male" if data[2] == 'M' else 'Female' if data[2] == 'F' else 'Non-Binary'

            curr.execute("SELECT appts.id, appts.timeperiod, appts.symptoms, COALESCE(doctors.name, 'TBA') AS doctorName, appts.department FROM appts LEFT JOIN doctors ON appts.doctorid = doctors.id WHERE patientid = %s", (id, ))
            appointments = curr.fetchall()

            if not appointments:
                toReturn['appointments'] = {}
            else:
                toAppend = []
                for appointment in appointments:

                    if (appointment[1] != None):
                        date, startTime, endTime = getTime(str(appointment[1]))
                    else:
                        date = startTime = endTime =  "TBA"
                    temp = {
                        'id': appointment[0],
                        'symptoms': appointment[2],
                        'doctorName': appointment[3],
                        'department': appointment[4],
                        'date': date,
                        'startTime': startTime,
                        'endTime': endTime
                    }
                    toAppend.append(temp)
                toReturn['appointments'] = toAppend
    
    return jsonify(toReturn)

    # Do what you wanna do.


# @app.route('/getAvailableTimings', methods=['POST'])
# def getAvailableTimings():
#     authorizationHead = request.headers.get('Authorization')

#     if not authorizationHead or not authorizationHead.startswith("Bearer "):
#         return jsonify({"error": "Something's Wrong with Your Auth"})

#     token = authorizationHead.split(' ')[1]
#     payload = decodeAndVerifyJWT(token)

#     if payload == None:
#         return jsonify({"error": "User not Authorized to perform this action"}), 401

#     data = request.get_json()

#     department = data.get('department')

#     #  Integrate W/ AI to get Available Time Slots
#     toSend = ['45 Mins', []]
#     tsranges = ["[2025-03-16 08:00:00, 2025-03-16 09:00:00)",
#                 '[2025-03-13 14:00:00, 2025-03-13 15:00:00)',
#                 '[2025-03-12 09:00:00, 2025-03-12 10:00:00)',
#                 "[2025-03-15 16:00:00, 2025-03-15 17:00:00)",
#                 "[2025-03-14 11:00:00, 2025-03-14 12:00:00)",
#                 ]
#     for tsrange in tsranges:
#         date, startTime, endTime = getTime(tsrange)
#         toSend[1].append({
#             'tsrange': tsrange,
#             'startTime': startTime,
#             'endTime': endTime
#         })

#     return jsonify(toSend)

@app.route('/bookAppointment', methods=['POST'])
def bookAppointment():
    authorizationHead = request.headers.get('Authorization')

    if not authorizationHead or not authorizationHead.startswith("Bearer "):
        return jsonify({"error": "Something's Wrong with Your Auth"})

    token = authorizationHead.split(' ')[1]
    payload = decodeAndVerifyJWT(token)

    if payload == None:
        return jsonify({"error": "User not Authorized to perform this action"}), 401

    id = payload['id']
    data = request.get_json()
    department = data.get('department')
    symtomps = data.get('symptoms')

    if symtomps == 'None':
        symtomps = None

    with connectPostgres() as conn:
        with conn.cursor() as curr:
            try:
                curr.execute("INSERT INTO appts (patientid, department, symptoms, date) VALUES (%s, %s, %s, %s)", (id, department, symtomps, date.today()+timedelta(days=2)))
                conn.commit()
                return jsonify({"message":7}), 200
            except:
                return jsonify({"message": "Error"}), 500

    # Do what you wanna do.

@app.route('/deleteAppointment', methods=['POST'])
def deleteAppointment():
    authorizationHead = request.headers.get('Authorization')

    if not authorizationHead or not authorizationHead.startswith("Bearer "):
        return jsonify({"error": "Something's Wrong with Your Auth"})

    token = authorizationHead.split(' ')[1]
    payload = decodeAndVerifyJWT(token)

    if payload == None:
        return jsonify({"error": "User not Authorized to perform this action"}), 401

    id = payload['id']
    data = request.get_json()
    apptid = data.get("apptid")

    with connectPostgres() as conn:
        with conn.cursor() as curr:
            curr.execute("SELECT EXISTS ( SELECT 1 FROM appts WHERE id = %s AND patientid = %s) AS ownership", (apptid, id))
            owns = curr.fetchone()
            if owns != None:
                if owns[0] == True:
                    curr.execute("DELETE FROM appts WHERE id = %s", (apptid,))
                    conn.commit()
                    return jsonify({"message":7}), 200
                else:
                    return jsonify({"message":"Appt Not Of Patient"}), 200
            else:
                return jsonify({"message":"No Apptid"}), 200

@app.route('/adminLogin', methods=['POST'])
def adminLogin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == '' or password == '':
        return jsonify({'error': 'username and Password Are Required'}), 400
    if username == 'root' and password == 'root@kali':
        payload = {
        'username': username,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        }
        return jsonify({"jwt": jwt.encode(payload, SECRET_KEY, algorithm='HS256')}), 200
    else:
        return jsonify({'error': 'Try hard, lol'}), 400

@app.route('/getAllAppointmentsToday', methods=['GET'])
def getAllAppointmentsToday():
    authorizationHead = request.headers.get('Authorization')

    if not authorizationHead or not authorizationHead.startswith("Bearer "):
        return jsonify({"error": "Something's Wrong with Your Auth"})

    token = authorizationHead.split(' ')[1]
    payload = decodeAndVerifyJWT(token)

    if payload == None:
        return jsonify({"error": "User not Authorized to perform this action"}), 401

    if "username" not in payload:
        return jsonify({"error": "User not Authorized to perform this action"}), 401

    with connectPostgres() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT a.*, p.name AS patientName, d.name AS doctorName FROM appts a JOIN patientsAppt p ON a.patientId = p.id  JOIN doctors d ON a.doctorid = d.id  WHERE date = CURRENT_DATE")
            result = cursor.fetchall()
            toSendBack = []
            if result:
                for appt in result:
                    if (appt[3] != None):
                        date, startTime, endTime = getTime(str(appt[3]))
                    else:
                        date = startTime = endTime =  "TBA"
                    toSendBack.append({
                        "id": appt[0],
                        "patientId": appt[1],
                        "doctorId": appt[2],
                        'date': date,
                        'startTime': startTime,
                        'endTime': endTime,
                        'symptoms': appt[4],
                        'department': appt[5],
                        'predictedTime': appt[7],
                        'severity': appt[8],
                        'patientName': appt[9],
                        'doctorName': appt[10]

                    })
            return jsonify(toSendBack)

@app.route('/getBedStatus', methods=['GET'])
def getBedStatus():
    authorizationHead = request.headers.get('Authorization')

    if not authorizationHead or not authorizationHead.startswith("Bearer "):
        return jsonify({"error": "Something's Wrong with Your Auth"})

    token = authorizationHead.split(' ')[1]
    payload = decodeAndVerifyJWT(token)

    if payload == None:
        return jsonify({"error": "User not Authorized to perform this action"}), 401

    if "username" not in payload:
        return jsonify({"error": "User not Authorized to perform this action"}), 401

    with connectPostgres() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT 
                (SELECT predicted FROM bedhistorialData WHERE date = CURRENT_DATE) AS predictedBeds,
                
                (SELECT COUNT(*) 
                FROM admissions 
                WHERE admissionDate <= CURRENT_DATE AND 
                    (dischargeDate IS NULL OR dischargeDate >= CURRENT_DATE)) AS occupiedBeds,
                
                700 - (SELECT COUNT(*) 
                    FROM admissions 
                    WHERE admissionDate <= CURRENT_DATE AND 
                            (dischargeDate IS NULL OR dischargeDate >= CURRENT_DATE)) AS freeBeds,
                
                (SELECT COUNT(*) 
                FROM surgeries 
                WHERE date = CURRENT_DATE) AS surgeriesToday,
                
                (SELECT COUNT(*) 
                FROM icuAddms 
                WHERE startDate <= CURRENT_DATE AND 
                    (endDate IS NULL OR endDate >= CURRENT_DATE)) AS icuAddmsToday;

            """)
            result = cursor.fetchone()
  
            return jsonify({
                "predictedBeds": result[0],
                "occupiedBeds": result[1],
                "freeBeds": result[2],
                "surgeriesToday": result[3],
                "icuAddmsToday":result[4]
            })

@app.route('/getStaffStatus', methods=['GET'])
def getStaffStatus():
    authorizationHead = request.headers.get('Authorization')

    if not authorizationHead or not authorizationHead.startswith("Bearer "):
        return jsonify({"error": "Something's Wrong with Your Auth"})

    token = authorizationHead.split(' ')[1]
    payload = decodeAndVerifyJWT(token)

    if payload == None:
        return jsonify({"error": "User not Authorized to perform this action"}), 401

    if "username" not in payload:
        return jsonify({"error": "User not Authorized to perform this action"}), 401

    with connectPostgres() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT doctorspresent, nursespresent,technicianspresent,doctorsaipredict ,nursesaipredict ,techniciansaipredict FROM staff WHERE date = CURRENT_DATE")
            result = cursor.fetchone()
            print(result)
            return jsonify({
                "doctorsPrediction": result[0],
                "nursesPrediction": result[1],
                "technicianPrediction": result[2],
                "doctorsAttendance": result[3],
                "nursesAttendance":result[4],
                "technicianAttendance":result[5]
            })  
        
@app.route('/getEquipment', methods=['GET'])
def getEquipmentStatus():
    authorizationHead = request.headers.get('Authorization')

    if not authorizationHead or not authorizationHead.startswith("Bearer "):
        return jsonify({"error": "Something's Wrong with Your Auth"})

    token = authorizationHead.split(' ')[1]
    payload = decodeAndVerifyJWT(token)

    if payload == None:
        return jsonify({"error": "User not Authorized to perform this action"}), 401

    if "username" not in payload:
        return jsonify({"error": "User not Authorized to perform this action"}), 401

    with connectPostgres() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT patientmonitorsaipredict, defibaipredict, infusionpumpsaipredict, patientmonitors, defibs, infusionpumps FROM equipments WHERE date = CURRENT_DATE;")

            result = cursor.fetchone()
            print(result)
            return jsonify({
                "patientmonitorsaipredict": result[0],
                "defibaipredict": result[1],
                "infusionpumpsaipredict": result[2],
                "patientmonitors": result[3],
                "defibs": result[4],
                "infusionpumps": result[5]
            }) 


# @app.route('/protected', methods=['GET'])
# def protected():
#     authorizationHead = request.headers.get('Authorization')

#     if not authorizationHead or not authorizationHead.startswith("Bearer "):
#         return jsonify({"error": "Something's Wrong with Your Auth"})

#     token = authorizationHead.split(' ')[1]
#     payload = decodeAndVerifyJWT(token)

#     if payload == None:
#         return jsonify({"error": "User not Authorized to perform this action"}), 401

#     print(payload)
#     # Do what you wanna do.


if __name__ == '__main__':
    app.run(debug=True)