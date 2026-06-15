let selectedBookingId = null
let selectedBookingAmount = null

document.addEventListener("DOMContentLoaded", () => {
    requireAuth()
    updateNavbar()
    loadBookings()
})

function updateNavbar() {
    const user = JSON.parse(localStorage.getItem("user") || "{}")
    const emailEl = document.getElementById("user-email")
    if (emailEl) emailEl.textContent = user.first_name || user.email || "Account"
}

async function loadBookings() {
    showLoading(true)
    hideAlerts()

    const data = await getBookings()
    showLoading(false)

    const list = document.getElementById("bookings-list")
    list.style.display = "block"

    if (data.status === "error" || data.message) {
        if (data.message === "You have no bookings yet.") {
            list.innerHTML = `
                <div class="empty-state">
                    <div class="icon">🎫</div>
                    <h3>No bookings yet</h3>
                    <p>Start by searching for a flight</p>
                    <a href="/" class="btn btn-primary" style="margin-top: 16px">
                        Browse Flights
                    </a>
                </div>
            `
        } else {
            showAlert("error", data.message || "Failed to load bookings.")
        }
        return
    }

    if (!Array.isArray(data) || data.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="icon">🎫</div>
                <h3>No bookings yet</h3>
                <p>Start by searching for a flight</p>
                <a href="/" class="btn btn-primary" style="margin-top: 16px">
                    Browse Flights
                </a>
            </div>
        `
        return
    }

    list.innerHTML = data.map(booking => `
        <div class="booking-card card" id="booking-${booking.id}">
            <div class="booking-header">
                <div class="booking-id">Booking #${booking.id}</div>
                <span class="badge badge-${booking.status}">${booking.status}</span>
            </div>

            ${booking.flight ? `
            <div class="booking-route">
                <div class="route-airline">
                    <strong>${booking.flight.name}</strong>
                    <span class="flight-number">${booking.flight.flight_number}</span>
                </div>
                <div class="route-path">
                    <span class="route-code">${booking.flight.origin_airport?.code || "?"}</span>
                    <span class="route-arrow">✈</span>
                    <span class="route-code">${booking.flight.destination_airport?.code || "?"}</span>
                </div>
                <div class="route-price">$${booking.flight.price.toFixed(2)}</div>
            </div>
            ` : ''}

            <div class="booking-details">
            <div class="booking-detail">
                <span class="detail-label">💺 Seat</span>
                <span class="detail-value">
                    ${booking.seat_number || "Not selected"}
                </span>
            </div>
            <div class="booking-detail">
                <span class="detail-label">🕐 Boarding</span>
                <span class="detail-value">
                    ${booking.flight ? formatDateTime(booking.flight.boarding_time) : "—"}
                </span>
            </div>
            <div class="booking-detail">
                <span class="detail-label">📅 Booked At</span>
                <span class="detail-value">
                    ${formatDateTime(booking.booked_at)}
                </span>
            </div>
        </div>

            ${booking.status === "confirmed" ? `
            <div class="booking-actions">
                <button class="btn btn-success btn-sm" onclick="openPayModal(${booking.id})">
                    💳 Pay Now
                </button>
                <button class="btn btn-danger btn-sm" onclick="openCancelModal(${booking.id})">
                    ✕ Cancel
                </button>
            </div>
            ` : `
            <div class="booking-actions">
                <span class="cancelled-text">This booking has been cancelled</span>
                <button class="btn btn-secondary btn-sm" onclick="removeBooking(${booking.id})">
                    🗑️ Remove
                </button>
            </div>
            `}
        </div>
    `).join("")
}

// Cancel Modal
function openCancelModal(bookingId) {
    selectedBookingId = bookingId
    document.getElementById("cancel-error").classList.remove("show")
    document.getElementById("cancel-modal").style.display = "flex"
}

function closeCancelModal() {
    document.getElementById("cancel-modal").style.display = "none"
    selectedBookingId = null
}

async function confirmCancel() {
    const btn = document.getElementById("confirm-cancel-btn")
    const cancelError = document.getElementById("cancel-error")

    btn.disabled = true
    btn.textContent = "Cancelling..."

    const result = await updateBooking(selectedBookingId, "cancelled")

    if (result.status === "cancelled" || result.id) {
        closeCancelModal()
        showAlert("success", "Booking cancelled successfully.")
        loadBookings()
    } else {
        cancelError.textContent = result.message || "Failed to cancel booking."
        cancelError.classList.add("show")
        btn.disabled = false
        btn.textContent = "Yes, Cancel"
    }
}

// Pay Modal
function openPayModal(bookingId) {
    selectedBookingId = bookingId
    document.getElementById("pay-error").classList.remove("show")
    document.getElementById("pay-success").classList.remove("show")
    document.getElementById("currency").value = "USD"
    document.getElementById("pay-flight-info").innerHTML = `
        <div class="pay-info">
            <p>Payment for <strong>Booking #${bookingId}</strong></p>
            <p class="pay-note">Amount will be shown in the payment tab.</p>
        </div>
    `
    document.getElementById("pay-modal").style.display = "flex"
}

function closePayModal() {
    document.getElementById("pay-modal").style.display = "none"
    selectedBookingId = null
}

async function confirmPayment() {
    const btn = document.getElementById("confirm-pay-btn")
    const payError = document.getElementById("pay-error")
    const paySuccess = document.getElementById("pay-success")
    const currency = document.getElementById("currency").value

    btn.disabled = true
    btn.textContent = "Processing..."
    payError.classList.remove("show")
    paySuccess.classList.remove("show")

    const result = await createPayment(selectedBookingId, currency)

    if (result.id) {
        paySuccess.textContent = "Payment created successfully!"
        paySuccess.classList.add("show")
        setTimeout(() => {
            closePayModal()
            window.location.href = "/payments-page"
        }, 1500)
    } else {
        payError.textContent = result.message || "Payment failed."
        payError.classList.add("show")
        btn.disabled = false
        btn.textContent = "Confirm Payment"
    }
}

// Helpers
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
}

function hideAlerts() {
    document.getElementById("error-alert").classList.remove("show")
    document.getElementById("success-alert").classList.remove("show")
}

function showAlert(type, message) {
    const el = document.getElementById(`${type}-alert`)
    el.textContent = message
    el.classList.add("show")
}

async function removeBooking(bookingId) {
    if (!confirm("Remove this booking from your list?")) return
    const result = await hideBooking(bookingId)
    if (result === null || result.status !== "error") {
        loadBookings()
    } else {
        showAlert("error", result.message || "Failed to remove booking.")
    }
}