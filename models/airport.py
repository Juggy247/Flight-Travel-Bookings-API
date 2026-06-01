from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, ForeignKey,Boolean
from datetime import datetime, timezone
from database import Base
from sqlalchemy.orm import relationship

class Airport(Base):
    __tablename__ = "airports"

    id = Column(Integer,primary_key=True, index=True )
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    timezone = Column(String, nullable=False)

    departing_flights = relationship("Flight", foreign_keys="Flight.origin_id", back_populates="origin_airport")
    arriving_flights = relationship("Flight", foreign_keys="Flight.destination_id", back_populates="destination_airport")