from fastapi import FastAPI, Request, HTTPException
from routers import flights as flights_router
from database import engine,Base
from models import flight as flight_table
from routers import users as users_router
from routers import bookings as bookings_router
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()
Base.metadata.create_all(bind=engine)   #create all data base table
app.include_router(flights_router.router)
app.include_router(users_router.router)
app.include_router(bookings_router.router)

#handles validation errors from Pydantic
#exception_handler is a method of the FastAPI app object
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request,
                                       exc: RequestValidationError):
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": error["loc"][-1],
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

