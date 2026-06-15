const BASE_URL = "http://127.0.0.1:8000"

function getToken() {
    return localStorage.getItem("token")
}

function authHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${getToken()}`
    }
}

// Flights
async function getFlights(page=1, limit=10) {
    const res = await fetch(`${BASE_URL}/flights?page=${page}&limit=${limit}`)
    return res.json()
}

async function searchFlights(destination="", origin="", maxPrice="") {
    const params = new URLSearchParams()
    if (destination) url += `destination=${destination}&`
    if (origin) url += `origin=${origin}&`
    if (maxPrice) url += `max_price=${maxPrice}`
    const res = await fetch(`${BASE_URL}/flights/search?${params.toString()}`)
    return res.json()
}

async function getFlightsCount(destination="", origin="", maxPrice="") {
    const params = new URLSearchParams()
    if (destination) params.append("destination", destination)
    if (origin) params.append("origin", origin)
    if (maxPrice) params.append("max_price", maxPrice)
    const res = await fetch(`${BASE_URL}/flights/count?${params.toString()}`)
    return res.json()
}

async function searchFlightsPaginated(destination="", origin="", maxPrice="", page=1, limit=6) {
    const params = new URLSearchParams()
    if (destination) params.append("destination", destination)
    if (origin) params.append("origin", origin)
    if (maxPrice) params.append("max_price", maxPrice)
    params.append("page", page)
    params.append("limit", limit)
    const res = await fetch(`${BASE_URL}/flights/search?${params.toString()}`)
    return res.json()
}

// Users
async function register(data) {
    const res = await fetch(`${BASE_URL}/users/register`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
    return res.json()
}

async function login(email, password) {
    const res = await fetch(`${BASE_URL}/users/login`, {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: `username=${email}&password=${password}`
    })
    return res.json()
}

async function getMe() {
    const res = await fetch(`${BASE_URL}/users/me`, {
        headers: authHeaders()
    })
    return res.json()
}

// Bookings
async function getBookings() {
    const res = await fetch(`${BASE_URL}/bookings`, {
        headers: authHeaders()
    })
    return res.json()
}

async function createBooking(flightId, seatNumber=null) {
    const res = await fetch(`${BASE_URL}/bookings`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
            flight_id: flightId,
            seat_number: seatNumber
        })
    })
    return res.json()
}

async function cancelBooking(bookingId) {
    const res = await fetch(`${BASE_URL}/bookings/${bookingId}`, {
        method: "DELETE",
        headers: authHeaders()
    })
    return res.json()
}

async function updateBooking(bookingId, status) {
    const res = await fetch(`${BASE_URL}/bookings/${bookingId}`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify({status})
    })
    return res.json()
}

// Payments
async function getPayments() {
    const res = await fetch(`${BASE_URL}/payments`, {
        headers: authHeaders()
    })
    return res.json()
}

async function createPayment(bookingId, currency="USD") {
    const res = await fetch(`${BASE_URL}/payments`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
            booking_id: bookingId,
            currency: currency
        })
    })
    return res.json()
}

async function updatePayment(paymentId, status) {
    const res = await fetch(`${BASE_URL}/payments/${paymentId}`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify({status})
    })
    return res.json()
}

// Airports
async function searchAirports(city="", country="") {
    let url = `${BASE_URL}/airports/search?`
    if (city) url += `city=${city}&`
    if (country) url += `country=${country}`
    const res = await fetch(url)
    return res.json()
}

async function getAirports() {
    const res = await fetch(`${BASE_URL}/airports?limit=50`)
    return res.json()
}

async function hideBooking(bookingId) {
    const res = await fetch(`${BASE_URL}/bookings/${bookingId}/hide`, {
        method: "PUT",
        headers: { "Authorization": `Bearer ${getToken()}` }
    })
    if (res.status === 204) return { status: "success" }
    return res.json()
}