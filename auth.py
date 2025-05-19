from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

from fastapi.security import OAuth2PasswordBearer

# This is the URL where your token will be obtained (should match your /token route)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
print(oauth2_scheme)

from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY = "taskfastapi"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
