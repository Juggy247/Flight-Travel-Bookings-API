from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Flight(Base):
    __tablename__ = "flights"

    __table_args__ = (
        UniqueConstraint(
            "name", "origin_id", "destination_id", "boarding_time",
            name="unique_flight_constraint"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    origin_id = Column(Integer, ForeignKey("airports.id"), nullable=False)       
    destination_id = Column(Integer, ForeignKey("airports.id"), nullable=False)   
    flight_number = Column(String, nullable=False, unique=True)
    boarding_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)                             
    price = Column(Float, nullable=False)
    seats = Column(Integer, nullable=False)

    origin_airport = relationship("Airport", foreign_keys=[origin_id],           
                                  back_populates="departing_flights")
    destination_airport = relationship("Airport", foreign_keys=[destination_id],  
                                       back_populates="arriving_flights")
    bookings = relationship("Booking", back_populates="flight")