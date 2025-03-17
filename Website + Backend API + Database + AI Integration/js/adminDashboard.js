const endPoint = 'http://localhost:5000'
jwt = localStorage.getItem('jwt');

function loadTodaysAppts() {
    fetch(`${endPoint}/getAllAppointmentsToday`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + jwt
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)

            if (data.length != 0) {
                appendAppts = document.getElementById("appendAppts")
                data.forEach(element => {
                    box = document.createElement("div")
                    box.classList.add("box")
                    box.classList.add("has-text-left")
                    box.innerHTML = `
                            <h3 class="is-3 title">Appt ID: ${element.id}</h3>
                            <h5 class="is-size-5 subtitle my-0 mt-1">Patient ID: ${element.patientName}</h5>
                            <h5 class="is-size-5 subtitle my-0 ">Patient Name: ${element.patientId}</h5>
                            <h5 class="is-size-5 subtitle my-0 mt-1">Doctor: ${element.doctorName}</h5>
                            <h5 class="is-size-5 subtitle my-0 ">Doctor ID: ${element.doctorId}</h5>
                            <h5 class="is-size-5 subtitle my-0 mt-1">Department: ${element.department}</h5>
                            <h5 class="is-size-5 subtitle my-0">Day: ${element.date}</h5>
                            <h5 class="is-size-5 subtitle my-0 mt-1">Time: ${element.startTime} to ${element.endTime}</h5>
                            <h5 class="is-size-5 subtitle my-0">Symptoms: ${element.symptoms}</h5>
                            <h5 class="is-size-5 subtitle my-0 mt-1 ">Severity: ${element.severity}</h5>
                            <h5 class="is-size-5 subtitle my-0">Predicted Time: ${element.predictedTime}</h5>
                
                            `
                    appendAppts.appendChild(box)
                });
            }
            

        })
        .catch(error => {
            console.log('Error', error)
        })
}

function realTimeBedData() {
    fetch(`${endPoint}/getBedStatus`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + jwt
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)

            document.getElementById("predictedBeds").innerText = data.predictedBeds
            document.getElementById("occupiedBeds").innerText = data.occupiedBeds
            document.getElementById("freeBeds").innerText = data.freeBeds
            document.getElementById("surgeriesToday").innerText = data.surgeriesToday
            document.getElementById("icuAddmsToday").innerText = data.icuAddmsToday


        })
        .catch(error => {
            console.log('Error', error)
        })
}

function realtimeStaffAvailablity() {
    fetch(`${endPoint}/getStaffStatus`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + jwt
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)

            document.getElementById("doctorsPrediction").innerText = data.doctorsPrediction;
            document.getElementById("nursesPrediction").innerText = data.nursesPrediction;
            document.getElementById("technicianPrediction").innerText = data.technicianPrediction;;
            document.getElementById("doctorAttendance").innerText = data.doctorsAttendance;
            document.getElementById("nursesAttendance").innerText = data.nursesAttendance;
            document.getElementById("technicianAttendance").innerText = data.technicianAttendance
                ;

        })
        .catch(error => {
            console.log('Error', error)
        })
}

function realtimeEquipment() {
    fetch(`${endPoint}/getEquipment`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + jwt
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)

            document.getElementById("patientmonitorsaipredict").innerText = data.patientmonitorsaipredict;
            document.getElementById("defibaipredict").innerText = data.defibaipredict;
            document.getElementById("infusionpumpsaipredict").innerText = data.infusionpumpsaipredict;
            document.getElementById("patientmonitorsused").innerText = data.patientmonitors;
            document.getElementById("defibused").innerText = data.defibs;
            document.getElementById("infusionpumpsused").innerText = data.infusionpumps;



        })
        .catch(error => {
            console.log('Error', error)
        })
}
window.onload = function loadEverything() {

    loadTodaysAppts();
    realTimeBedData();
    realtimeStaffAvailablity();
    realtimeEquipment();
}