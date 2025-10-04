import bcrypt
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User  # SQLAlchemy database model
from ..schemas import UserCreate, UserResponse, UserUpdate, UserLogin, Token, UserTokenValidation  # Pydantic API schemas
from ..services.auth import create_access_token, get_current_user, verify_token_user, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/users", tags=["users"])


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt with salt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password as string
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        hashed_password: Previously hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user
    """
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user  # Pydantic will convert SQLAlchemy model to UserResponse


@router.post("/login", response_model=Token)
async def login_user(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "username": user.username,
        }, 
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer", username=user.username, email=user.email)


@router.post("/validate", response_model=Token)
async def validate_user(
    credentials: UserTokenValidation,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate user token
    """
    # Find user by email
    user = await verify_token_user(credentials.access_token, db)

    if user:
        return Token(access_token=credentials.access_token, token_type="bearer", username=user.username, email=user.email)

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )


# Add this if you need user search (with auth)
# @router.get("/me", response_model=UserResponse)
# async def get_me(current_user: User = Depends(get_current_user)):
#     """Get current authenticated user's profile"""
#     return current_user


# Just want to test
# @router.get("/{user_id}", response_model=UserResponse)
# async def get_user(
#     user_id: int, 
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get a specific user by ID
#     """
#     user = await db.get(User, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     return user  # Pydantic will convert SQLAlchemy model to UserResponse


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,  # Pydantic schema for input validation
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Require authentication
):
    """
    Update a user (only own profile)
    """
    # Check if user is updating their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update only provided fields
    if user_data.username is not None:
        user.username = user_data.username
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Require authentication
):
    """
    Delete a user (only own account)
    """
    # Check if user is deleting their own account
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )
    
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()