from datetime import datetime, timedelta,timezone
from jose import JWTError, jwt  
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer #defines how FastAPI extracts the token from the request.
from sqlalchemy.orm import Session #QLAlchemy database session type
from database import get_db
from models.user import User as UserModel
from dotenv import load_dotenv
from passlib.context import CryptContext 
import os   #Python’s built-in os module to access environment variables via os.getenv().

# -- Config
# to load variables from .env 
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))

if not SECRET_KEY: 
    raise RuntimeError("Secret key is not in the env file. ")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pwd(password: str) -> str:  
    return pwd_context.hash(password)
# Create Token

def create_access_token(data: dict) -> str:

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY,algorithm=ALGORITHM )

def get_current_user(
        token: str = Depends(oauth2_scheme), #This uses FastAPI’s OAuth2PasswordBearer
        db: Session = Depends(get_db)) -> UserModel:
    
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials")
    
    try: 
        payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM]) #decode variables
        email: str = payload.get("sub") #get the value(email) from the token
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserModel).filter(UserModel.email==email).first()
    if user is None:
        raise HTTPException(status_code = 401, detail="Invalid Token.")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated.")
    
    return user

def get_admin_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action."
        )
    return current_user