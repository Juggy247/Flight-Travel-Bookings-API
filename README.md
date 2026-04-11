# Travel Booking API

A RESTful travel booking API built with **FastAPI** and **SQLAlchemy**.
Designed as a backend learning project focused on real-world API development patterns.

---

## Features

* **Flight Management** — Create, search, update, and delete flights (admin only)
* **User Authentication** — Register, login with JWT tokens
* **Role-Based Access** — Admin and regular user roles
* **Booking System** — Book flights, cancel bookings, seat management
* **Overbooking Prevention** — Seats reduce on booking, return on cancellation
* **Input Validation** — Pydantic v2 validation on all endpoints
* **Pagination** — Paginated flight listings
* **Consistent Error Handling** — Standardized error responses across all endpoints

---

## Tech Stack

| Technology        | Purpose          |
| ----------------- | ---------------- |
| FastAPI           | Web framework    |
| SQLAlchemy        | ORM              |
| SQLite            | Database         |
| Pydantic v2       | Data validation  |
| JWT (python-jose) | Authentication   |
| Passlib + bcrypt  | Password hashing |
| pytest + httpx    | Testing          |

---

## Project Structure

```
travel-api/
├── main.py              # App entry point, middleware, exception handlers
├── database.py          # DB engine, session, base
├── auth.py              # JWT creation, token validation, admin check
├── utils.py             # Shared response helpers
├── models/
│   ├── flight.py        # Flight DB model
│   ├── user.py          # User DB model
│   └── booking.py       # Booking DB model (FK relationships)
├── schemas/
│   ├── flight.py        # Flight Pydantic schemas
│   ├── user.py          # User Pydantic schemas
│   └── booking.py       # Booking Pydantic schemas
├── routers/
│   ├── flights.py       # Flight endpoints
│   ├── users.py         # User endpoints
│   └── bookings.py      # Booking endpoints
└── tests/
    └── test_flights.py  # Pytest test suite
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/travel-api.git
cd travel-api
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

```
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Run the app

```bash
uvicorn main:app --reload
```

### 6. Open API docs

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Flights

| Method | Endpoint          | Auth   | Description                   |
| ------ | ----------------- | ------ | ----------------------------- |
| GET    | `/flights`        | Public | List all flights (paginated)  |
| POST   | `/flights`        | Admin  | Create a flight               |
| GET    | `/flights/search` | Public | Search by destination + price |
| GET    | `/flights/{id}`   | Public | Get flight by ID              |
| PUT    | `/flights/{id}`   | Admin  | Update flight                 |
| DELETE | `/flights/{id}`   | Admin  | Delete flight                 |

---

### Users

| Method | Endpoint          | Auth   | Description        |
| ------ | ----------------- | ------ | ------------------ |
| POST   | `/users/register` | Public | Register new user  |
| POST   | `/users/login`    | Public | Login, returns JWT |
| GET    | `/users/me`       | User   | Get current user   |

---

### Bookings

| Method | Endpoint         | Auth | Description           |
| ------ | ---------------- | ---- | --------------------- |
| POST   | `/bookings`      | User | Book a flight         |
| GET    | `/bookings/me`   | User | Get my bookings       |
| PUT    | `/bookings/{id}` | User | Update booking status |
| DELETE | `/bookings/{id}` | User | Cancel booking        |

---

## Authentication

This API uses **JWT Bearer tokens**.

### Register

```bash
curl -X POST "http://127.0.0.1:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "email": "john@example.com", "password": "password123"}'
```

### Login

```bash
curl -X POST "http://127.0.0.1:8000/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=password123"
```

### Use Token

```bash
curl -X GET "http://127.0.0.1:8000/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

##  Key Design Decisions

### 1. Separated models and schemas

SQLAlchemy models define database structure. Pydantic schemas handle validation and serialization.
Keeps concerns separate and prevents leaking DB internals to the API layer.

### 2. JWT stored in Authorization header

User ID is never trusted from the request body — always extracted from the verified JWT token.
Prevents users from impersonating others.

### 3. Atomic seat management

`with_for_update()` lock prevents race conditions when multiple users book the last seat simultaneously.

### 4. Consistent error responses

All errors return:

```json
{"status": "error", "message": "..."}
```

Validation errors include a detailed `errors` array with field-level messages.

---

## What I Learned

* Designing RESTful APIs with FastAPI
* SQLAlchemy ORM — models, sessions, relationships, foreign keys
* JWT authentication and authorization
* Role-based access control (RBAC)
* Password hashing with bcrypt
* Pydantic v2 data validation
* Database constraints and integrity
* Writing automated tests with pytest
* Separating concerns (models / schemas / routers)
