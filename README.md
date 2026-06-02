# ✈️ Flight Agency API

A RESTful travel booking API built with **FastAPI** and **SQLAlchemy**.

---


---

## Tech Stack

| Technology      | Purpose                    |
|-----------------|----------------------------|
| Python 3.14     | Primary language           |
| FastAPI         | Web framework              |
| SQLAlchemy      | ORM                        |
| SQLite          | Database                   |
| Pydantic v2     | Data validation            |
| JWT             | Authentication             |
| Passlib + bcrypt| Password hashing           |
| sqladmin        | Admin panel                |
| pytest          | Testing                    |
| GitHub Actions  | CI/CD                      |

---

## Project Structure
travel-api/
├── main.py              # App entry point, sqladmin, exception handlers
├── database.py          # DB engine, session, base
├── auth.py              # JWT creation, validation, password hashing
├── utils.py             # Shared response helpers
├── constants.py         # Shared API response codes
├── seed.py              # Populate airport data
├── export_openapi.py    # Generate openapi.yaml
├── openapi.yaml         # API specification
├── models/
│   ├── airport.py       # Airport DB model
│   ├── flight.py        # Flight DB model
│   ├── user.py          # User DB model
│   ├── booking.py       # Booking DB model
│   └── payment.py       # Payment DB model
├── schemas/
│   ├── airport.py       # Airport Pydantic schemas
│   ├── flight.py        # Flight Pydantic schemas
│   ├── user.py          # User Pydantic schemas
│   ├── booking.py       # Booking Pydantic schemas
│   └── payment.py       # Payment Pydantic schemas
├── routers/
│   ├── airports.py      # Airport endpoints
│   ├── flights.py       # Flight endpoints
│   ├── users.py         # User endpoints
│   ├── bookings.py      # Booking endpoints
│   └── payments.py      # Payment endpoints
└── tests/
├── conftest.py      # Shared test database setup
├── test_airports.py # Airport tests
├── test_flights.py  # Flight tests
├── test_users.py    # User tests
├── test_bookings.py # Booking tests
└── test_payments.py # Payment tests

---

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Juggy247/Flight-Travel-Bookings-API.git
cd Flight-Travel-Bookings-API
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

### 5. Run the application
```bash
uvicorn main:app --reload
```

### 6. Populate airport data
```bash
python seed.py
```

### 7. Open API documentation
http://127.0.0.1:8000/docs

### 8. Open Admin Panel
http://127.0.0.1:8000/admin

---

## API Endpoints

### Flights
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/flights` | Public | List all flights (paginated) |
| GET | `/flights/search` | Public | Search by destination/origin/price |
| GET | `/flights/{id}` | Public | Get flight by ID |

### Users
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/users/register` | Public | Register new user |
| POST | `/users/login` | Public | Login, returns JWT token |
| GET | `/users/me` | User | Get current user profile |

### Bookings
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/bookings` | User | Book a flight |
| GET | `/bookings` | User | Get my bookings |
| PUT | `/bookings/{id}` | User | Update booking status |
| DELETE | `/bookings/{id}` | User | Cancel booking |

### Airports
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/airports` | Public | List all airports (paginated) |
| GET | `/airports/search` | Public | Search by city/country |

### Payments
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/payments` | User | Create payment for booking |
| GET | `/payments` | User | Get my payments |
| PUT | `/payments/{id}` | User | Update payment status |

---

## Authentication

This API uses **JWT Bearer tokens**.

### Register
```bash
curl -X POST "http://127.0.0.1:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST "http://127.0.0.1:8000/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=password123"
```

### Use Token
```bash
curl -X GET "http://127.0.0.1:8000/bookings" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Admin Panel

The admin panel at `/admin` allows managing all data without touching the database directly:

- ✅ Create, edit, delete flights
- ✅ Manage airports
- ✅ View and manage users (set admin role, deactivate)
- ✅ View all bookings
- ✅ View all payments

### Creating an admin user
1. Register via `POST /users/register`
2. Go to `http://127.0.0.1:8000/admin/user/list`
3. Click **Edit** on your user
4. Check `is_admin` ✅ and **Save**

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific file
pytest tests/test_flights.py -v
pytest tests/test_users.py -v
pytest tests/test_bookings.py -v
pytest tests/test_airports.py -v
pytest tests/test_payments.py -v
```

See [TESTING.md](TESTING.md) for full test documentation.

---

## Database

5 tables with proper relationships:

| Table | Description |
|-------|-------------|
| users | Registered users |
| airports | 41 real airports worldwide |
| flights | Flights between airports |
| bookings | User flight bookings |
| payments | Payments for bookings |

### Relationships
airports ──< flights (origin)
airports ──< flights (destination)
users    ──< bookings
flights  ──< bookings
bookings ──  payments (one to one)

---

## Input Validation

All endpoints are protected against invalid input:

| Field | Validation |
|-------|------------|
| email | Valid email format |
| password | Minimum 8 characters |
| phone | Valid phone number format |
| flight_number | Format: 2 uppercase letters + 1-4 digits e.g. AK101 |
| boarding_time | Must be in the future |
| arrival_time | Must be after boarding time |
| price | Must be greater than 0 |
| seats | Must be between 1 and 853 |
| airport code | 3-4 uppercase letters e.g. KUL, WMKK |
| seat_number | Format: row 1-50 + letter A-F e.g. 12A |
| currency | Must be one of: USD, EUR, GBP, PLN, MYR, SGD, JPY, THB |

---

## JWT Authentication
User identity is always extracted from the verified JWT token — never trusted from the request body. Prevents impersonation.



