from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
from datetime import datetime, timedelta, timezone

from ..database import get_db
from ..models import User, Exchange, Stock, Financial  # SQLAlchemy database model
from ..schemas import StockCreate, StockResponse, StockUpdate  # Pydantic API schemas
from ..services.auth import get_current_user
from ..services.openai import query_company_description

router = APIRouter(prefix="/stocks", tags=["stocks"])


async def get_stock_by_id(
    stock_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Stock:
    """
    Helper function to get a stock by ID and ensure it belongs to the current user
    """
    result = await db.execute(
        select(Stock)
        .options(selectinload(Stock.exchange))
        .where(
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
    
    return stock


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
    stock = await get_stock_by_id(stock_id, db, current_user)
    
    # Update only provided fields
    updated_data = stock_data.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
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
    stock = await get_stock_by_id(stock_id, db, current_user)

    await db.delete(stock)
    await db.commit()
    
    # 204 No Content - successful deletion with no response body
    return None


@router.get("/{stock_id}/ai_description", response_model=StockResponse, status_code=status.HTTP_200_OK)
async def get_ai_description(
    stock_id: int,
    # stock_data: StockUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-generated description for a stock and update it
    """
    stock = await get_stock_by_id(stock_id, db, current_user)
    
    if stock.ai_description:
        # check the ai_description_created_at time and if still within 30 days, return existing
        if stock.ai_description_created_at and (datetime.now(timezone.utc) - stock.ai_description_created_at) < timedelta(days=30):
            logging.info("Returning existing AI description (within 30 days)")
            return stock
    
    ai_status, ai_response = query_company_description(stock.company_name, stock.exchange.name, stock.country)
    
    if not ai_status:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get AI description"
        )
    
    elif "company not found" in ai_response.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found by AI"
        )
    
    else:
        logging.info(f"AI description for {stock.company_name} received.")

        if len(ai_response) > 500:
            logging.warning(f"AI description length ({len(ai_response)}) exceeds 500 characters. Response will be truncated.")

        truncated = ai_response[:500] if len(ai_response) > 500 else ai_response

        setattr(stock, 'ai_description', truncated)

        await db.commit()
        await db.refresh(stock)

        return stock