from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User, Exchange, Stock, Financial  # SQLAlchemy database model
from ..schemas import ExchangeCreate, ExchangeResponse, ExchangeUpdate  # Pydantic API schemas
from ..services.auth import get_current_user

router = APIRouter(prefix="/exchanges", tags=["exchanges"])


@router.post("/", response_model=ExchangeResponse, status_code=status.HTTP_201_CREATED)
async def create_exchange(
    exchange_data: ExchangeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new exchange
    """
    db_exchange = Exchange(
        abbreviation=exchange_data.abbreviation,
        name=exchange_data.name,
        country=exchange_data.country,
        user_id=current_user.id
    )

    db.add(db_exchange)
    await db.commit()
    await db.refresh(db_exchange)
    
    return db_exchange  # Pydantic will convert SQLAlchemy model to UserResponse


@router.get("/", response_model=List[ExchangeResponse], status_code=status.HTTP_200_OK)
async def get_all_exchanges(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all exchanges for the current user
    """
    exchanges = await db.execute(select(Exchange).filter(Exchange.user_id == current_user.id))
    return exchanges.scalars().all()


# @router.get("/{exchange_id}", response_model=ExchangeResponse, status_code=status.HTTP_200_OK)
# async def get_exchange(
#     exchange_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get a specific exchange by ID
#     """
#     result = await db.execute(
#         select(Exchange).where(
#             Exchange.id == exchange_id,
#             Exchange.user_id == current_user.id
#         )
#     )
#     exchange = result.scalar_one_or_none()
    
#     if not exchange:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Exchange not found"
#         )
    
#     return exchange


@router.put("/{exchange_id}", response_model=ExchangeResponse, status_code=status.HTTP_200_OK)
async def update_exchange(
    exchange_id: int,
    exchange_data: ExchangeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing exchange
    """
    # First, check if the exchange exists and belongs to the current user
    result = await db.execute(
        select(Exchange).where(
            Exchange.id == exchange_id,
            Exchange.user_id == current_user.id
        )
    )
    exchange = result.scalar_one_or_none()
    
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found"
        )
    
    # Update only provided fields
    update_data = exchange_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exchange, field, value)
    
    await db.commit()
    await db.refresh(exchange)
    
    return exchange


@router.delete("/{exchange_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exchange(
    exchange_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an exchange
    """
    # First, check if the exchange exists and belongs to the current user
    result = await db.execute(
        select(Exchange).where(
            Exchange.id == exchange_id,
            Exchange.user_id == current_user.id
        )
    )
    exchange = result.scalar_one_or_none()
    
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found"
        )
    
    await db.delete(exchange)
    await db.commit()
    
    # 204 No Content - successful deletion with no response body
    return None