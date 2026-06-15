from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from routers import flights as flights_router
from routers import users as users_router
from routers import bookings as bookings_router
from routers import airports as airports_router
from routers import payments as payments_router
from models import flight as flight_table      
from models import airport as airport_table    
from models import payment as payment_table    
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
    title="Flight Agency"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("frontend/index.html")

@app.get("/login")
def login_page():
    return FileResponse("frontend/login.html")

@app.get("/register")
def register_page():
    return FileResponse("frontend/register.html")

@app.get("/bookings-page")
def bookings_page():
    return FileResponse("frontend/bookings.html")

@app.get("/payments-page")
def payments_page():
    return FileResponse("frontend/payments.html")

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