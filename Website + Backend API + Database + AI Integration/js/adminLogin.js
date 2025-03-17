const endPoint = 'http://localhost:5000'

// Form and Login
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");

function errorChecking() {

    if (usernameInput.value == '') {
        usernameInput.classList.add("is-danger");
        return false;
    }

    if (passwordInput.value == '') {
        passwordInput.classList.add("is-danger");
        return false;
    }

    return true;
}


document.getElementById("loginBtn").addEventListener("click", (e) => {

    if (errorChecking()) { 
        toSend = {
            password: passwordInput.value,
            username: usernameInput.value,
        };

        fetch(`${endPoint}/adminLogin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(toSend)
        })
            .then(response => response.json())
            .then(data => {
                console.log(data)
                if('jwt' in data){
                    localStorage.setItem('jwt', data.jwt)
                    console.log('Logged in!')
                    
                    window.location = "/adminDashboard.html"
                }else{
                    console.log('Error', data.error)

                }
            })
            .catch(error => {
                console.log('Error', error)
            })
    }
})