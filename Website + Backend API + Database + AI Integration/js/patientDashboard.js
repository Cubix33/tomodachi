const endPoint = 'http://localhost:5000'

jwt = localStorage.getItem('jwt');

function getDateWithOffset(offsetDays = 0) {
    const today = new Date();

    // Clone today's date and add offset in days
    const targetDate = new Date(today);
    targetDate.setDate(today.getDate() + offsetDays);

    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const months = ["January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"];

    const dayName = days[targetDate.getDay()];
    const day = targetDate.getDate();
    const monthName = months[targetDate.getMonth()];
    const year = targetDate.getFullYear();

    const ordinalSuffix = (n) => {
        if (n > 3 && n < 21) return 'th';
        switch (n % 10) {
            case 1: return "st";
            case 2: return "nd";
            case 3: return "rd";
            default: return "th";
        }
    };

    return `${dayName}, ${day}${ordinalSuffix(day)} ${monthName} ${year}`;
}







window.onload = function loadPatientDetails() {

    fetch(`${endPoint}/getPatientDetails`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + jwt
        },
    })
        .then(response => response.json())
        .then(data => {

            console.log(data)
            
            // filling data in the form
            document.getElementById('name').innerText = data.name
            document.getElementById('id').innerText = data.id
            document.getElementById('gender').innerText = data.gender
            document.getElementById('age').innerText = data.age

            if (data.appointments && data.appointments.length > 0) {

                appendAppts = document.getElementById("appendAppts")
                appendAppts.innerHTML = ''
                data.appointments.forEach(appointment => {
                    box = document.createElement("div")
                    box.classList.add("box")
                    box.classList.add("has-text-left")
                    box.innerHTML = `
                            <h3 class="is-3 title">Appt ID: ${appointment.id}</h3>
                            <h5 class="is-size-5 subtitle my-0 mt-1">Doctor: ${appointment.doctorName}</h5>
                            <h5 class="is-size-5 subtitle my-0">Department: ${appointment.department}</h5>
                            <h5 class="is-size-5 subtitle my-0">Day: ${appointment.date}</h5>
                            <h5 class="is-size-5 subtitle my-0">Time: ${appointment.startTime} to ${appointment.endTime}</h5>
                            <h5 class="is-size-5 subtitle my-0">Symptoms: ${appointment.symptoms}</h5>
                            <hr>
                            <div class="columns">
                                <div class="column">
                                    <button class="button is-danger is-fullwidth" data-apptid='${appointment.id}' onclick='cancelApptConfirm(this)'>Cancel</button>
                                </div>
                            </div>
                
                            `
                    appendAppts.appendChild(box)
                })
            }
            const progress = document.getElementById("loadingProgress");
            const container = document.getElementById("mainContainer");

            // Step 1: Fade out the progress bar
            progress.classList.add("fade-out");

            // Step 2: After fade-out is done, hide progress bar completely
            setTimeout(() => {
                progress.classList.add("is-hidden"); // Fully hide it (display: none)

                // Step 3: Reveal the container
                container.classList.remove("is-hidden");
                container.classList.add("fade-in");

            }, 500);

        })
        .catch(error => {
            console.log('Error', error)
        })
}



document.getElementById('scheduleApptBtn').addEventListener('click', (e) => {
    document.getElementById('scheduleApptDialog').classList.remove('is-hidden')
    setTimeout(() => {
        document.getElementById('scheduleApptDialog').classList.add("slide-in");
    }, 10);
})

// document.getElementById('getAvailableTimingsBtn').addEventListener('click', (e) => {
//     if (document.getElementById('department').value != 'N') {

//         fetch(`${endPoint}/getAvailableTimings`, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'Authorization': 'Bearer ' + jwt
//             },
//             body: JSON.stringify({ 'department': document.getElementById('department').value })
//         })
//             .then(response => response.json())
//             .then(data => {
//                 console.log(data)
//                 document.getElementById("estimateConsulTime").innerText = data[0]
//                 timingsContainer = document.getElementById("timingsContainer")
//                 data[1].forEach(timeSlot => {
//                     button = document.createElement("button")
//                     button.classList.add('button')
//                     button.classList.add('is-warning')
//                     button.classList.add('m-1')
//                     button.classList.add('timeSlotBtn')
//                     button.setAttribute('onclick', `confirmationDialogBook(this)`)
//                     button.setAttribute('data-tsrange', `${timeSlot.tsrange}`)
//                     button.innerText = `${timeSlot.startTime} - ${timeSlot.endTime}`

//                     timingsContainer.appendChild(button)
//                 })

//                 document.getElementById('consulationTimingDiv').classList.remove('is-hidden')
//                 void document.getElementById('consulationTimingDiv').offsetWidth
//                 document.getElementById('consulationTimingDiv').classList.add('slide-in')

//             })
//             .catch(error => {
//                 console.log('Error', error)
//             })

//     } else {
//         document.getElementById('department').parentElement.classList.remove("is-warning")
//         document.getElementById('department').parentElement.classList.add("is-danger")
//     }
// })



document.getElementById("getAvailableTimingsBtn").addEventListener("click", () => {

    if (document.getElementById('department').value != 'N') {
        document.getElementById('modalConfirmAppt').classList.add('is-active')

        document.getElementById('departmentConfirm').innerText = document.getElementById('department').value

        document.getElementById('symptomsConfirm').innerText = document.getElementById("symptoms").value

        document.getElementById('dateConfirm').innerText = getDateWithOffset(2)
    }
    else {
        document.getElementById('department').parentElement.classList.remove("is-warning")
        document.getElementById('department').parentElement.classList.add("is-danger")
    }
})

document.getElementById("bookApptConfirmBtn").addEventListener("click", (e) => {


    data = {
        'department': document.getElementById('department').value,
        'symptoms': document.getElementById("symptoms").value
    }


    fetch(`${endPoint}/bookAppointment`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + jwt
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if (data.message == 7) {
                document.getElementById("messageBodyConfirmAppointment").innerHTML = `
                <h1 class='title is-1'>Done</h1>
                <p class='subtitle'>Redirecting You...</p>
                `
                setTimeout(() => {
                    window.location = "/patientDashboard.html"
                }, 2000)

            }

        })
        .catch(error => {
            console.log('Error', error)
        })
})

function cancelApptConfirm(e) {
    document.getElementById("modalConfirmDelete").classList.add("is-active")
    document.getElementById("apptid").innerText = e.dataset.apptid
    document.getElementById("confirmDeleteBtn").setAttribute("data-apptid", e.dataset.apptid)
}

document.getElementById("confirmDeleteBtn").addEventListener("click", () => {

    fetch(`${endPoint}/deleteAppointment`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + jwt
        },
        body: JSON.stringify({ 'apptid': document.getElementById("confirmDeleteBtn").dataset.apptid })
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if (data.message == 7) {
                document.getElementById("deleteConfirmBody").innerHTML = `
                <h1 class='title is-1'>Done</h1>
                <p class='subtitle'>Refreshing...</p>
                `
                setTimeout(() => {
                    window.location = "/patientDashboard.html"
                }, 2000)
            } else {
                document.getElementById("deleteConfirmBody").innerHTML = `
                <h1 class='title is-1'>Done</h1>
                <p class='subtitle'>Refreshing...</p>
                `
            }

        })
        .catch(error => {
            console.log('Error', error)
            document.getElementById("deleteConfirmBody").innerHTML = `
                <h1 class='title is-1'>Done</h1>
                <p class='subtitle'>Refreshing...</p>
                `
        })

})