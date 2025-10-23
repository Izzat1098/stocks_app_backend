import os
from datetime import datetime, timedelta, timezone
from types import NoneType
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "this-is-definitely-not-the-secret-key-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600

# Security scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return username
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        username: str = payload.get("username")

        if email is None or username is None:
            return None

        return email, username

    except JWTError:
        return None
    

async def verify_token_user(
    token: str, 
    db: AsyncSession = Depends(get_db)
):
    """
    Verify JWT token and check user details in db
    """
    token_data = verify_token(token)
    if not token_data:
        return None

    email, username = token_data

    result = await db.execute(
        select(User).where((User.username == username) & (User.email == email))
    )
    user = result.scalar_one_or_none()
    return user



async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = await verify_token_user(credentials.credentials, db)

    if user is None:
        raise credentials_exception
    
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get current authenticated admin user
    (You can extend this later with role-based access)
    """
    # For now, just return current user
    # Later you can add admin role checking:
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user