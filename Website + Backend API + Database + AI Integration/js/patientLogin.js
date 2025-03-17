const endPoint = 'http://localhost:5000'


// For toggling b/w login and signup forms
const loginForm = document.querySelector('.patientLoginForm');
const signupForm = document.querySelector('.patientSignupForm');

document.getElementById("showSignup").addEventListener("click", () => {
    loginForm.classList.remove('visibleForm');
    loginForm.classList.add('hiddenForm');

    signupForm.classList.remove('hiddenForm');
    signupForm.classList.add('visibleForm');
});

document.getElementById("showLogin").addEventListener("click", () => {
    signupForm.classList.remove('visibleForm');
    signupForm.classList.add('hiddenForm');

    loginForm.classList.remove('hiddenForm');
    loginForm.classList.add('visibleForm');
});


// Form and Login
const nameInput = document.getElementById("name");
const signUpEmailInput = document.getElementById("signupEmail");
const signUpPasswordInput = document.getElementById("signupPassword");
const genderInput = document.getElementById("gender");
const ageInput = document.getElementById("age");
const medicalHistory = document.getElementById("medicalHistory")

const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");

function errorChecking(mode) {
    if (mode == 0) {

        if (nameInput.value == '') {
            nameInput.classList.add("is-danger");
            return false;
        }

        if (signUpEmailInput.value == '') {
            signUpEmailInput.classList.add("is-danger");
            return false;
        }

        if (signUpPasswordInput.value == '') {
            signUpPasswordInput.classList.add("is-danger");
            return false;
        }

        if (!['M', 'F', 'O'].includes(genderInput.value)) {
            genderInput.classList.add("is-danger");
            return false;
        }

        if (ageInput.value == '') {
            ageInput.classList.add("is-danger")
            return false
        }

    } else {
        if (emailInput.value == '') {
            emailInput.classList.add("is-danger");
            return false;
        }

        if (passwordInput.value == '') {
            passwordInput.classList.add("is-danger");
            return false;
        }
    }

    return true;
}

document.getElementById("signUpBtn").addEventListener("click", (e) => {

    if (errorChecking(0)) {
        nameValue = nameInput.value
        emailValue = signUpEmailInput.value
        passwordValue = signUpPasswordInput.value
        ageValue = ageInput.value
        genderValue = genderInput.value

        medicalHistoryValue = medicalHistory.value

        toSend = {
            name: nameValue,
            password: passwordValue,
            gender: genderValue,
            email: emailValue,
            age: ageValue,
            medicalHistory: medicalHistoryValue
        };

        fetch(`${endPoint}/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(toSend)
        })
            .then(response => response.json())
            .then(data => {
                console.log(data)

                if (data.message == 7) {
                    document.getElementById("mainContainer").innerHTML = `
                 <h1 class="title is-1">Signup Successful.. Please login to continue</h1>
                <p class="subtitle is-3">Redirecting...</p>
            `
                    setTimeout(() => {
                        window.location = "/patientLogin.html"

                    }, 2000)
                }
            })
            .catch(error => {
                console.log('Error', error)
            })
    }
})

document.getElementById("loginBtn").addEventListener("click", (e) => {

    if (errorChecking(1)) {

        emailValue = emailInput.value
        passwordValue = passwordInput.value
        toSend = {
            password: passwordValue,
            email: emailValue,
        };

        fetch(`${endPoint}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(toSend)
        })
            .then(response => response.json())
            .then(data => {
                console.log(data)
                if ('jwt' in data) {
                    localStorage.setItem('jwt', data.jwt)
                    console.log('Logged in!')

                    window.location = "/patientDashboard.html"
                } else {
                    console.log('Error', data.error)

                }

            })
            .catch(error => {
                console.log('Error', error)
            })
    }
})