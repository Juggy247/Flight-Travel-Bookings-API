from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session , declarative_base

engine = create_engine("sqlite:///./users.db", connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
#SessionLocal() creates a Session object — 
#think of it as a temporary workspace between your Python code and the database.
    """
    A Session is what stores the objects in memory and keeps track of any changes
    needed in the data, then it uses the engine to communicate with the database.
    """
    db = SessionLocal()     #“temporary session tied to one HTTP request”
    try:
        yield db
    finally:
        db.close()