from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.user import User as UserModel
from schemas.user import UserCreate, UserResponse
from database import get_db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from auth import create_access_token, get_current_user

#create router
router = APIRouter()

#bcrypt hashing setup
#Passlib is a password hashing framework for Python.
#CryptContext is a class provided by the Passlib library:
#Use bcrypt hashing algorithm
#deprecated="auto" - If a stored password hash uses an old algorithm, 
# that is no longer the preferred one, mark it as deprecated

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pwd(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/users/register", response_model=UserResponse)
#Depends - dependency injection
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    #check if email exist
    existing_user = db.query((UserModel)).filter(UserModel.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    #Hash the password
    hashed = hash_pwd(user.password)

    #Register in DB
    new_user = UserModel(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        password = hashed,
        phone = user.phone
    )
    db.add(new_user)
    db.commit()

    return new_user

# Login 
@router.post("/users/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    credentials_error = HTTPException(
        status_code=401, detail="Invalid credentials")
    #Find User  
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    # Look up in database using email
    if not user:
        raise credentials_error
    
    #Verify Password
    if not pwd_context.verify(form_data.password, user.password):
        raise credentials_error
    
    #Create Token
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user
