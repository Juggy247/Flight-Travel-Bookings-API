// js/payments.js

let selectedPaymentId = null

document.addEventListener("DOMContentLoaded", () => {
    requireAuth()
    updateNavbar()
    loadPayments()
})

function updateNavbar() {
    const user = JSON.parse(localStorage.getItem("user") || "{}")
    const emailEl = document.getElementById("user-email")
    if (emailEl) emailEl.textContent = user.first_name || user.email || "Account"
}

async function loadPayments() {
    showLoading(true)
    hideAlerts()

    const data = await getPayments()
    showLoading(false)

    const list = document.getElementById("payments-list")
    list.style.display = "block"

    if (data.status === "error" || data.message) {
        if (data.message === "You have no payments yet.") {
            list.innerHTML = `
                <div class="empty-state">
                    <div class="icon">💳</div>
                    <h3>No payments yet</h3>
                    <p>Book a flight and make a payment to see it here</p>
                    <a href="/" class="btn btn-primary" style="margin-top: 16px">
                        Browse Flights
                    </a>
                </div>
            `
        } else {
            showAlert("error", data.message || "Failed to load payments.")
        }
        return
    }

    if (!Array.isArray(data) || data.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="icon">💳</div>
                <h3>No payments yet</h3>
                <p>Book a flight and make a payment to see it here</p>
                <a href="/" class="btn btn-primary" style="margin-top: 16px">
                    Browse Flights
                </a>
            </div>
        `
        return
    }

    list.innerHTML = data.map(payment => `
        <div class="payment-card card" id="payment-${payment.id}">
            <div class="payment-header">
                <div class="payment-id">Payment #${payment.id}</div>
                <span class="badge badge-${payment.status}">${payment.status}</span>
            </div>

            <div class="payment-details">
                <div class="payment-detail">
                    <span class="detail-label">🎫 Booking</span>
                    <span class="detail-value">Booking #${payment.booking_id}</span>
                </div>
                <div class="payment-detail">
                    <span class="detail-label">💰 Amount</span>
                    <span class="detail-value payment-amount">
                        $${payment.amount.toFixed(2)}
                    </span>
                </div>
                <div class="payment-detail">
                    <span class="detail-label">💱 Currency</span>
                    <span class="detail-value">${payment.currency}</span>
                </div>
                <div class="payment-detail">
                    <span class="detail-label">📅 Paid At</span>
                    <span class="detail-value">
                        ${payment.paid_at ? formatDateTime(payment.paid_at) : "Not paid yet"}
                    </span>
                </div>
            </div>

            <div class="payment-actions">
                <button class="btn btn-primary btn-sm"
                    onclick="openStatusModal(${payment.id}, '${payment.status}',
                    ${payment.amount}, '${payment.currency}')">
                    ✏️ Update Status
                </button>
                <a href="/bookings-page" class="btn btn-secondary btn-sm">
                    View Booking
                </a>
            </div>
        </div>
    `).join("")
}

// Status Modal
function openStatusModal(paymentId, currentStatus, amount, currency) {
    selectedPaymentId = paymentId
    document.getElementById("new-status").value = currentStatus
    document.getElementById("status-error").classList.remove("show")
    document.getElementById("status-success").classList.remove("show")
    document.getElementById("confirm-status-btn").disabled = false
    document.getElementById("confirm-status-btn").textContent = "Update Status"
    document.getElementById("modal-payment-info").innerHTML = `
        <div class="pay-info">
            <p>Payment <strong>#${paymentId}</strong></p>
            <p>Amount: <strong>$${amount.toFixed(2)} ${currency}</strong></p>
            <p>Select new status below:</p>
        </div>
    `
    document.getElementById("status-modal").style.display = "flex"
}

function closeStatusModal() {
    document.getElementById("status-modal").style.display = "none"
    selectedPaymentId = null
}

async function confirmStatusUpdate() {
    const btn = document.getElementById("confirm-status-btn")
    const statusError = document.getElementById("status-error")
    const statusSuccess = document.getElementById("status-success")
    const newStatus = document.getElementById("new-status").value

    btn.disabled = true
    btn.textContent = "Updating..."
    statusError.classList.remove("show")
    statusSuccess.classList.remove("show")

    const result = await updatePayment(selectedPaymentId, newStatus)

    if (result.id) {
        statusSuccess.textContent = "Payment status updated!"
        statusSuccess.classList.add("show")
        setTimeout(() => {
            closeStatusModal()
            loadPayments()
        }, 1500)
    } else {
        statusError.textContent = result.message || "Failed to update payment."
        statusError.classList.add("show")
        btn.disabled = false
        btn.textContent = "Update Status"
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

function toggleMenu() {
    document.getElementById("navbar-menu").classList.toggle("open")
}