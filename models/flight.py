from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

class Flight(Base):
    __tablename__ = "flights"
    #For duplicated data with same name, destination and boarding time
    __table_args__ = (
        UniqueConstraint(
            "name", "destination", "boarding_time",
            name="unique_flight_constraint"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    flight_number = Column(String, nullable=False)
    boarding_time = Column(DateTime, nullable=False)
    price = Column(Float)
    seats = Column(Integer)
    bookings = relationship("Booking", back_populates="flight")
    