from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User, Exchange, Stock, Financial  # SQLAlchemy database model
from ..schemas import StockCreate, StockResponse, StockUpdate  # Pydantic API schemas
from ..services.auth import get_current_user

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.post("/", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
async def create_stock(
    stock_data: StockCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new stock
    """
    db_stock = Stock(
        user_id=current_user.id,
        ticker=stock_data.ticker,
        company_name=stock_data.company_name,
        abbreviation=stock_data.abbreviation,
        description=stock_data.description,
        exchange_id=stock_data.exchange_id,
        sector=stock_data.sector
    )

    db.add(db_stock)
    await db.commit()
    await db.refresh(db_stock)
    
    return db_stock  # Pydantic will convert SQLAlchemy model to UserResponse


@router.get("/", response_model=List[StockResponse], status_code=status.HTTP_200_OK)
async def get_all_stocks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all stocks for the current user
    """
    stocks = await db.execute(
        select(Stock).where(Stock.user_id == current_user.id))
    return stocks.scalars().all()


@router.put("/{stock_id}", response_model=StockResponse, status_code=status.HTTP_200_OK)
async def update_stock(
    stock_id: int,
    stock_data: StockUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing stock
    """
    # First, check if the stock exists and belongs to the current user
    result = await db.execute(
        select(Stock).where(
            Stock.id == stock_id,
            Stock.user_id == current_user.id
        )
    )
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found"
        )
    
    # Update only provided fields
    update_data = stock_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stock, field, value)

    await db.commit()
    await db.refresh(stock)

    return stock


@router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock(
    stock_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a stock
    """
    # First, check if the stock exists and belongs to the current user
    result = await db.execute(
        select(Stock).where(
            Stock.id == stock_id,
            Stock.user_id == current_user.id
        )
    )
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found"
        )

    await db.delete(stock)
    await db.commit()
    
    # 204 No Content - successful deletion with no response body
    return None