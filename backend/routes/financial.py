import logging
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Financial, User  # SQLAlchemy database model
from ..schemas import FinancialCreate, FinancialMetrics, FinancialResponse
from ..services.auth import get_current_user
from .stocks import get_stock_by_id

router = APIRouter(prefix="/stocks", tags=["financials"])


@router.post(
    "/{stock_id}/financials",
    response_model=FinancialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_financial_data(
    stock_id: int,
    data: FinancialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Save financial records
    """
    start_ts = time.perf_counter()
    stock = await get_stock_by_id(stock_id, db, current_user)

    if stock_id != data.stock_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock ID in path and body do not match",
        )

    for date_str, metrics in data.data.items():
        financial_year = datetime.strptime(date_str, "%Y-%m-%d").date()

        for field_name, value in metrics.model_dump().items():
            if value is not None:
                db_data = await db.execute(
                    select(Financial).where(
                        Financial.user_id == current_user.id,
                        Financial.year == financial_year,
                        Financial.field == field_name,
                        Financial.stock_id == stock.id,
                    )
                )
                current_record = db_data.scalar_one_or_none()

                if current_record and current_record.value != value:
                    current_record.value = value
                    current_record.created_at = datetime.now(timezone.utc)
                    db.add(current_record)

                elif not current_record:
                    new_record = Financial(
                        stock_id=stock.id,
                        user_id=current_user.id,
                        year=financial_year,
                        field=field_name,
                        value=value,
                    )
                    db.add(new_record)

    await db.commit()
    elapsed = time.perf_counter() - start_ts
    logging.info(f"Saved financial data for stock {stock_id} in {elapsed:.4f} seconds")
    return FinancialResponse(**data.model_dump(), updated_at=datetime.now(timezone.utc))


@router.get(
    "/{stock_id}/financials",
    response_model=FinancialResponse,
    status_code=status.HTTP_200_OK,
)
async def get_financial_data(
    stock_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get financial records
    """
    start_ts = time.perf_counter()
    stock = await get_stock_by_id(stock_id, db, current_user)

    result = await db.execute(
        select(Financial).where(
            (Financial.stock_id == stock.id) & (Financial.user_id == current_user.id)
        )
    )
    data = result.scalars().all()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No financial data found for this stock",
        )

    financial_data = {"stock_id": stock.id, "data": {}}

    for record in data:
        date_key = record.year.strftime("%Y-%m-%d")

        if date_key not in financial_data["data"]:
            financial_data["data"][date_key] = {}

        financial_data["data"][date_key][record.field] = record.value

    for date_key, metrics_dict in financial_data["data"].items():
        financial_data["data"][date_key] = FinancialMetrics(**metrics_dict)

    elapsed = time.perf_counter() - start_ts
    logging.info(
        f"Fetched financial data for stock {stock_id} in {elapsed:.4f} seconds"
    )
    return FinancialResponse(**financial_data, updated_at=datetime.now(timezone.utc))
