// js/flights.js

const LIMIT = 6
let currentPage = 1
let currentFilters = { destination: "", origin: "", max_price: "" }
let totalPages = 1

document.addEventListener("DOMContentLoaded", () => {
    updateNavbar()
    loadFlights()
})

function updateNavbar() {
    const loggedIn = isLoggedIn()
    document.getElementById("nav-login").style.display = loggedIn ? "none" : "block"
    document.getElementById("nav-register").style.display = loggedIn ? "none" : "block"
    document.getElementById("nav-logout").style.display = loggedIn ? "block" : "none"
    document.getElementById("nav-user").style.display = loggedIn ? "block" : "none"
    document.getElementById("guest-links-bookings").style.display = loggedIn ? "block" : "none"
    document.getElementById("guest-links-payments").style.display = loggedIn ? "block" : "none"

    if (loggedIn) {
        const user = JSON.parse(localStorage.getItem("user") || "{}")
        document.getElementById("user-email").textContent = user.first_name || "Account"
    }
}

// Load flights with current filters and page
async function loadFlights() {
    showLoading(true)
    hideAlerts()

    const { destination, origin, max_price } = currentFilters
    const isFiltered = destination || origin || max_price

    // Get total count first for pagination
    const countData = await getFlightsCount(destination, origin, max_price)
    const total = (countData && countData.total !== undefined) ? countData.total : null

    totalPages = Math.max(1, Math.ceil(total / LIMIT))

    // Clamp current page
    if (currentPage > totalPages) currentPage = totalPages
    if (currentPage < 1) currentPage = 1

    let data = []

    if (isFiltered) {
        // Use search endpoint with pagination
        data = await searchFlightsPaginated(destination, origin, max_price, currentPage, LIMIT)
    } else {
        // Use regular paginated endpoint
        data = await getFlights(currentPage, LIMIT)
    }

    showLoading(false)

    if (!Array.isArray(data)) {
        showAlert("error", data.message || "Failed to load flights.")
        renderFlights([])
        renderPagination(total)
        return
    }

    renderFlights(data)
    renderPagination(total)

    // Update results header
    document.getElementById("results-header").style.display = "flex"
    document.getElementById("results-title").textContent = isFiltered
        ? "Search Results" : "Available Flights"
    document.getElementById("results-count").textContent = isFiltered
        ? `${total} flight${total !== 1 ? "s" : ""} found`
        : `Page ${currentPage} of ${totalPages}`
}

// Handle search form
async function handleSearch(e) {
    e.preventDefault()

    const destination = document.getElementById("destination").value.trim()
    const origin = document.getElementById("origin").value.trim()
    const maxPrice = document.getElementById("max_price").value

    // Reset errors
    document.querySelectorAll(".form-error").forEach(el => el.classList.remove("show"))

    // Validate
    let valid = true
    const codePattern = /^[A-Z]{3,4}$/

    if (destination && !codePattern.test(destination)) {
        document.getElementById("destination-error").classList.add("show")
        valid = false
    }
    if (origin && !codePattern.test(origin)) {
        document.getElementById("origin-error").classList.add("show")
        valid = false
    }
    if (maxPrice && parseFloat(maxPrice) <= 0) {
        document.getElementById("price-error").classList.add("show")
        valid = false
    }

    if (!valid) return

    // Update filters and reset to page 1
    currentFilters = { destination, origin, max_price: maxPrice }
    currentPage = 1
    loadFlights()
}

// Clear search
function clearSearch() {
    document.getElementById("destination").value = ""
    document.getElementById("origin").value = ""
    document.getElementById("max_price").value = ""
    document.querySelectorAll(".form-error").forEach(el => el.classList.remove("show"))
    currentFilters = { destination: "", origin: "", max_price: "" }
    currentPage = 1
    loadFlights()
}

// Change page
function changePage(direction) {
    const newPage = currentPage + direction
    if (newPage < 1 || newPage > totalPages) return
    currentPage = newPage
    loadFlights()
    window.scrollTo(0, 0)
}

function goToPage(page) {
    currentPage = page
    loadFlights()
    window.scrollTo(0, 0)
}

// Render flight cards
function renderFlights(flights) {
    const grid = document.getElementById("flights-grid")

    if (!flights || flights.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <div class="icon">✈️</div>
                <h3>No flights found</h3>
                <p>Try different search criteria</p>
            </div>
        `
        return
    }

    grid.innerHTML = flights.map(flight => `
        <div class="flight-card card">
            <div class="flight-header">
                <span class="airline-name">${flight.name}</span>
                <span class="flight-number">${flight.flight_number}</span>
            </div>
            <div class="flight-route">
                <div class="airport">
                    <span class="airport-code">
                        ${flight.origin_airport?.code || flight.origin_id}
                    </span>
                    <span class="airport-city">
                        ${flight.origin_airport?.city || "Origin"}
                    </span>
                </div>
                <div class="route-line">
                    <span class="plane-icon">✈</span>
                    <div class="line"></div>
                </div>
                <div class="airport">
                    <span class="airport-code">
                        ${flight.destination_airport?.code || flight.destination_id}
                    </span>
                    <span class="airport-city">
                        ${flight.destination_airport?.city || "Destination"}
                    </span>
                </div>
            </div>
            <div class="flight-details">
                <div class="detail">
                    <span class="detail-label">🕐 Boarding</span>
                    <span class="detail-value">${formatDateTime(flight.boarding_time)}</span>
                </div>
                <div class="detail">
                    <span class="detail-label">🕐 Arrival</span>
                    <span class="detail-value">${formatDateTime(flight.arrival_time)}</span>
                </div>
                <div class="detail">
                    <span class="detail-label">💺 Seats</span>
                    <span class="detail-value seats ${flight.seats < 10 ? "seats-low" : ""}">
                        ${flight.seats} left
                    </span>
                </div>
            </div>
            <div class="flight-footer">
                <span class="price">$${flight.price.toFixed(2)}</span>
                <button class="btn btn-primary btn-sm"
                    onclick="openBookModal(${flight.id}, '${flight.name}',
                    '${flight.origin_airport?.code || ""}',
                    '${flight.destination_airport?.code || ""}',
                    ${flight.price})"
                    ${flight.seats <= 0 ? "disabled" : ""}>
                    ${flight.seats <= 0 ? "Full" : "Book Now"}
                </button>
            </div>
        </div>
    `).join("")
}

// Render pagination with correct page count
function renderPagination(total) {
    const pagination = document.getElementById("pagination")

    if (total <= LIMIT && currentPage === 1) {
        pagination.style.display = "none"
        return
    }

    pagination.style.display = "flex"

    const prevBtn = document.getElementById("prev-btn")
    const nextBtn = document.getElementById("next-btn")
    const pageNumbers = document.getElementById("page-numbers")

    prevBtn.disabled = currentPage === 1
    nextBtn.disabled = currentPage >= totalPages

    // Page number buttons
    let pageHTML = ""
    for (let i = 1; i <= totalPages; i++) {
        pageHTML += `
            <button class="btn btn-sm ${i === currentPage ? "btn-primary" : "btn-secondary"}"
                onclick="goToPage(${i})">${i}</button>
        `
    }
    pageNumbers.innerHTML = pageHTML
}

// Book Modal
function openBookModal(flightId, name, origin, destination, price) {
    if (!isLoggedIn()) {
        window.location.href = "/login"
        return
    }
    selectedFlightId = flightId
    document.getElementById("modal-flight-info").innerHTML = `
        <div class="modal-flight-info">
            <strong>${name}</strong>
            <span>${origin} → ${destination}</span>
            <span class="modal-price">$${price.toFixed(2)}</span>
        </div>
    `
    document.getElementById("seat_number").value = ""
    document.getElementById("seat-error").classList.remove("show")
    document.getElementById("modal-error").classList.remove("show")
    document.getElementById("modal-success").classList.remove("show")
    document.getElementById("confirm-book-btn").disabled = false
    document.getElementById("confirm-book-btn").textContent = "Confirm Booking"
    document.getElementById("modal-overlay").style.display = "flex"
}

function closeModal() {
    document.getElementById("modal-overlay").style.display = "none"
    selectedFlightId = null
}

async function confirmBooking() {
    const seatInput = document.getElementById("seat_number")
    const seatError = document.getElementById("seat-error")
    const modalError = document.getElementById("modal-error")
    const modalSuccess = document.getElementById("modal-success")
    const btn = document.getElementById("confirm-book-btn")

    seatError.classList.remove("show")
    modalError.classList.remove("show")
    modalSuccess.classList.remove("show")

    const seat = seatInput.value.trim()
    if (seat && !/^([1-9]|[1-4][0-9]|50)[A-F]$/.test(seat)) {
        seatError.classList.add("show")
        return
    }

    btn.disabled = true
    btn.textContent = "Booking..."

    const result = await createBooking(selectedFlightId, seat || null)

    if (result.id) {
        modalSuccess.textContent = "Flight booked successfully!"
        modalSuccess.classList.add("show")
        btn.disabled = false
        btn.textContent = "Confirm Booking"
        setTimeout(() => {
            closeModal()
            loadFlights()
        }, 1500)
    } else {
        modalError.textContent = result.message || "Booking failed."
        modalError.classList.add("show")
        btn.disabled = false
        btn.textContent = "Confirm Booking"
    }
}

// Helpers
let selectedFlightId = null

function formatDateTime(dt) {
    if (!dt) return "—"
    const d = new Date(dt)
    return d.toLocaleDateString("en-GB", {
        day: "2-digit", month: "short", year: "numeric"
    }) + " " + d.toLocaleTimeString("en-GB", {
        hour: "2-digit", minute: "2-digit"
    })
}

function showLoading(show) {
    document.getElementById("loading").style.display = show ? "block" : "none"
    document.getElementById("flights-grid").style.display = show ? "none" : "grid"
}

function hideAlerts() {
    document.getElementById("error-alert").classList.remove("show")
    document.getElementById("info-alert").classList.remove("show")
}

function showAlert(type, message) {
    const el = document.getElementById(`${type}-alert`)
    el.textContent = message
    el.classList.add("show")
}

let allAirports = []

async function openAirportCodesModal() {
    document.getElementById("airport-codes-modal").style.display = "flex"
    document.getElementById("airport-codes-search").value = ""

    if (allAirports.length === 0) {
        const data = await getAirports()
        allAirports = Array.isArray(data) ? data : []
    }
    renderAirportCodes(allAirports)
}

function closeAirportCodesModal() {
    document.getElementById("airport-codes-modal").style.display = "none"
}

function renderAirportCodes(airports) {
    const tbody = document.getElementById("airport-codes-tbody")
    if (airports.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3">No airports found</td></tr>`
        return
    }
    tbody.innerHTML = airports.map(a => `
        <tr>
            <td><strong>${a.code}</strong></td>
            <td>${a.city}</td>
            <td>${a.country}</td>
        </tr>
    `).join("")
}

function filterAirportCodes() {
    const term = document.getElementById("airport-codes-search").value.toLowerCase()
    const filtered = allAirports.filter(a =>
        a.code.toLowerCase().includes(term) ||
        a.city.toLowerCase().includes(term) ||
        a.country.toLowerCase().includes(term)
    )
    renderAirportCodes(filtered)
}