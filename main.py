from fastapi import FastAPI, Request, HTTPException
from routers import flights as flights_router
from routers import users as users_router
from routers import bookings as bookings_router
from routers import airports as airports_router
from routers import payments as payments_router
from models import flight as flight_table      # import models so SQLAlchemy knows about them
from models import airport as airport_table    # import models so SQLAlchemy knows about them
from models import payment as payment_table    # import models so SQLAlchemy knows about them
from models.user import User
from models.flight import Flight
from models.airport import Airport
from models.booking import Booking
from models.payment import Payment
from database import engine, Base
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqladmin import Admin, ModelView          # sqladmin — visual admin panel

app = FastAPI(
    title="Flight Agency",
)

# --- Admin Panel Setup ---
# sqladmin creates a visual dashboard at /admin
# allows managing all tables without touching the database directly
admin = Admin(app, engine)

# Admin views — each ModelView registers a table in the admin panel
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.first_name, User.is_admin, User.is_active]
    form_excluded_columns = [User.password]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

class FlightAdmin(ModelView, model=Flight):
    column_list = [Flight.id, Flight.name, Flight.flight_number, 
                   Flight.boarding_time, Flight.arrival_time, 
                   Flight.price, Flight.seats]
    name = "Flight"
    name_plural = "Flights"
    icon = "fa-solid fa-plane"

class AirportAdmin(ModelView, model=Airport):
    column_list = [Airport.id, Airport.code, Airport.name, 
                   Airport.city, Airport.country]
    name = "Airport"
    name_plural = "Airports"
    icon = "fa-solid fa-tower-control"

class BookingAdmin(ModelView, model=Booking):
    column_list = [Booking.id, Booking.user_id, Booking.flight_id, 
                   Booking.seat_number, Booking.status, Booking.booked_at]
    name = "Booking"
    name_plural = "Bookings"
    icon = "fa-solid fa-ticket"

class PaymentAdmin(ModelView, model=Payment):
    column_list = [Payment.id, Payment.booking_id, Payment.amount, 
                   Payment.currency, Payment.status]
    name = "Payment"
    name_plural = "Payments"
    icon = "fa-solid fa-credit-card"

# Register all admin views
admin.add_view(UserAdmin)
admin.add_view(FlightAdmin)
admin.add_view(AirportAdmin)
admin.add_view(BookingAdmin)
admin.add_view(PaymentAdmin)

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(flights_router.router)
app.include_router(users_router.router)
app.include_router(bookings_router.router)
app.include_router(airports_router.router)
app.include_router(payments_router.router)

# Handles validation errors from Pydantic
# exception_handler is a method of the FastAPI app object
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request,
                                       exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": error["loc"][-1],  # get the field name from error location
            "message": error["msg"]
        })
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Validation failed.", "errors": errors}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail}
    )