# ✈️ Flight Agency — Web GUI

A responsive web frontend for the Flight Agency API, built with vanilla HTML, CSS, and JavaScript. Served directly by the FastAPI backend via static files.

---

## Features

- **Flight Search** — search by destination/origin airport code and max price, with pagination
- **Airport Codes Reference** — searchable modal listing all airports with codes, cities, and countries
- **User Authentication** — register and login with JWT, persisted in localStorage
- **Booking Management** — book flights with optional seat selection, view and cancel bookings
- **Payment Management** — create payments for bookings, update payment status
- **Auto-Refund** — cancelling a booking automatically refunds its linked payment
- **Soft Hide** — cancelled bookings can be removed from view (and their payments hidden too) without losing history
- **Responsive Design** — adapts to mobile and tablet screen sizes

---

## Project Structure

```
frontend/
├── css/
│   ├── main.css           # Shared styles, navbar, layout
│   ├── auth.css           # Login / Register pages
│   ├── flights.css        # Flights search & listing page
│   ├── bookings.css        # My Bookings page
│   └── payments.css        # My Payments page
├── js/
│   ├── api.js              # All API calls (fetch wrappers)
│   ├── auth.js             # Auth helpers (requireAuth, logout, token)
│   ├── flights.js          # Flights page logic
│   ├── bookings.js          # Bookings page logic
│   └── payments.js          # Payments page logic
├── images/
│   ├── air-plane.png        # App logo / icon
│   └── airport-hero.jpg      # Background images
├── index.html               # Flights / homepage
├── login.html
├── register.html
├── bookings.html
└── payments.html
```

---

## Running the GUI

The GUI is served by the same FastAPI backend — **no separate server needed**.

### 1. Set up the backend

Follow the steps in the main `README.md` (virtual environment, dependencies, `.env` file, seed data).

### 2. Start the server

```bash
uvicorn main:app --reload
```

### 3. Open the GUI in your browser

```
http://127.0.0.1:8000
```

### Available pages

| Page | URL |
|------|-----|
| Flights / Home | `/` |
| Login | `/login` |
| Register | `/register` |
| My Bookings | `/bookings-page` |
| My Payments | `/payments-page` |

---

## Configuration

The frontend talks to the API at a base URL hardcoded in `frontend/js/api.js`:

```javascript
const BASE_URL = "http://127.0.0.1:8000"
```

If the backend runs on a different host or port, update this value accordingly.

---

## Caching Notes (Development)

Browsers aggressively cache CSS and JS files. If an edit to a stylesheet or script doesn't appear to take effect:

1. Bump the version query string on the relevant `<link>` / `<script>` tag, e.g. `auth.css?v=3`
2. Or open DevTools → Network tab → check "Disable cache" → reload

---

## Typical User Flow

```
1. Register / Login            → /register, /login
2. Search flights               → / (filter by destination, origin, price)
3. View airport codes reference  → "ℹ️ Airport Codes" modal
4. Book a flight                  → "Book" on a flight card
5. View bookings                   → /bookings-page
6. Pay for a booking                 → "Pay Now" → /payments-page
7. View / update payment status       → /payments-page
8. Cancel a booking                    → linked payment auto-refunds
9. Remove cancelled bookings             → "Remove" button hides booking & payment
```

---

## Input Validation

Client-side validation mirrors the API's rules using HTML attributes and JS:

| Field | Validation |
|-------|------------|
| Email | `type="email"` |
| Password | `minlength="8"` |
| Phone | regex pattern (optional field) |
| Destination / Origin code | 3-4 uppercase letters |
| Max price | `min="1"`, `step="0.01"` |
| Seat number | regex — row 1-50 + letter A-F (e.g. `12A`) |

---

## Pagination & Filtering

The Flights page (`/`) supports combined pagination and filtering:

- Filter by destination code, origin code, and/or max price
- Results are paginated (`GET /flights/search` + `GET /flights/count`)
- The total page count updates to reflect the filtered result set — e.g. filtering down to a handful of flights shows fewer pages, not the full unfiltered count

---

## Responsive Design

Layouts adapt at the `768px` breakpoint:

- Search form fields stack vertically on narrow screens
- Booking / payment route info stacks vertically
- Navbar collapses into a hamburger menu

---
