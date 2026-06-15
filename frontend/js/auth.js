// js/auth.js

function getToken() {
    return localStorage.getItem("token")
}

function isLoggedIn() {
    return !!getToken()
}

function logout() {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    window.location.href = "/login"
}

// Update navbar based on login state
function updateNavbar() {
    const loggedIn = isLoggedIn()
    const guestLinks = document.getElementById("guest-links")
    const userLinks = document.getElementById("user-links")
    const userEmail = document.getElementById("user-email")

    if (loggedIn) {
        if (guestLinks) guestLinks.style.display = "none"
        if (userLinks) userLinks.style.display = "flex"
        const user = JSON.parse(localStorage.getItem("user") || "{}")
        if (userEmail) userEmail.textContent = user.email || "My Account"
    } else {
        if (guestLinks) guestLinks.style.display = "flex"
        if (userLinks) userLinks.style.display = "none"
    }
}

// Protect pages that require login
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = "/login"
    }
}