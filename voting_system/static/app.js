// ========== COMMON VALIDATION FILE ==========

function validateRegisterForm() {
    let name = document.querySelector("input[name='name']").value;
    let voterId = document.querySelector("input[name='voter_id']").value;
    let email = document.querySelector("input[name='email']").value;

    if (name === "" || voterId === "" || email === "") {
        Swal.fire({
            icon: 'warning',
            title: 'Required',
            text: 'All fields are required!',
            background: '#ffffff', color: '#1e293b'
        });
        return false;
    }

    return true;
}

function validateLoginForm() {
    let loginEmail = document.getElementById("login_email");
    let loginOtp = document.getElementById("login_otp");
    
    // We only validate what's present in the current DOM (since it splits between email and otp)
    if (loginEmail && loginEmail.value === "") {
        Swal.fire({
            icon: 'warning',
            title: 'Required',
            text: 'Email is required!',
            background: '#ffffff', color: '#1e293b'
        });
        return false;
    }

    if (loginOtp && loginOtp.value === "") {
        Swal.fire({
            icon: 'warning',
            title: 'Required',
            text: 'OTP is required!',
            background: '#ffffff', color: '#1e293b'
        });
        return false;
    }

    return true;
}

// ========== SUCCESS & ERROR POPUP HANDLER ==========
window.onload = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const success = urlParams.get("success");
    const error = urlParams.get("error");

    if (error) {
        let msg = "Something went wrong!";
        if (error === "voterid") msg = "This Voter ID is already registered!";
        if (error === "email") msg = "This Email is already registered!";
        if (error === "invalid") msg = "Invalid Voter ID, Email or Password!";
        if (error === "notfound") msg = "Registered Email not found!";
        if (error === "already_voted") msg = "You have already cast your vote!";
        if (error === "face_failed") msg = "Face verification failed. Please try again.";

        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: msg,
            background: '#ffffff',
            color: '#1e293b',
            confirmButtonColor: '#e74c3c'
        });
        // Clear params from url so it doesn't pop up again on refresh
        window.history.replaceState({}, document.title, window.location.pathname);
        return;
    }

    if (success === "1") {
        let msg = "Operation successful!";
        let redirectUrl = null;

        if (window.location.pathname.includes("login")) {
            msg = "Login successful! Welcome to the voting system.";
            redirectUrl = "/face_verify";
        }
        else if (window.location.pathname.includes("register")) {
            msg = "Registration successful! Please login.";
            redirectUrl = "/login";
        }
        else if (window.location.pathname.includes("vote")) {
            msg = "Vote cast successfully! Thank you.";
            redirectUrl = "/result";
        }

        Swal.fire({
            icon: 'success',
            title: 'Success',
            text: msg,
            background: '#ffffff',
            color: '#1e293b',
            confirmButtonColor: '#4CAF50',
            timer: 2500,
            timerProgressBar: true
        }).then(() => {
            if(redirectUrl) window.location.href = redirectUrl;
        });
        
        window.history.replaceState({}, document.title, window.location.pathname);
    }
};