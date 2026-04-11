from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, Boolean
from datetime import datetime, timezone
from database import Base
from sqlalchemy.orm import relationship     #Object Relational Mapper

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True )
    first_name = Column(String(100), nullable = False)
    last_name = Column(String(100), nullable = True)
    password = Column(String(100), nullable = False)
    #we will use username as email
    email = Column(String(100), nullable = False, unique = True)
    phone = Column(String(20), nullable =True)
    is_active = Column(Boolean, default=True ,nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False, nullable=False)

    bookings = relationship("Booking", back_populates="user")
    #relationship() is used to link two models (tables)
    #back_populates - connect both sides of the relationship.
    #one to many relationship
