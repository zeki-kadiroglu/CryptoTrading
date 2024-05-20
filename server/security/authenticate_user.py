from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from server.db.schemas.user import User
from passlib.hash import bcrypt, pbkdf2_sha256, sha256_crypt

# Secret key to encode/decode JWT tokens
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#print("PSSWD", pwd_context.hash("password"))


# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)

def get_password_hash(password):
    return bcrypt.hash(password)

def get_user(db, username: str, password: str):
    if username in db.get_key("users", "username", username):
        print("username get user", username)
        user_dict = {
            "username": db.get_key("users", "username", username),
            "password": db.get_key("users", "password", password)}
        return User(**user_dict)
    return None

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username, password)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

