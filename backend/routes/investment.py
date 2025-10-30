from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Investment, User  # SQLAlchemy database model
from ..schemas import InvestSummaryCreate, InvestSummaryResponse
from ..services.auth import get_current_user
from .stocks import get_stock_by_id

router = APIRouter(prefix="/investment_summary", tags=["investment_summary"])


@router.get(
    "/{stock_id}", response_model=InvestSummaryResponse, status_code=status.HTTP_200_OK
)
async def get_investment_summary(
    stock_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvestSummaryResponse:

    await get_stock_by_id(stock_id, db, current_user)

    result = await db.execute(
        select(Investment).where(
            Investment.stock_id == stock_id, Investment.user_id == current_user.id
        )
    )
    investment_summary = result.scalar_one_or_none()

    if not investment_summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investment summary not found"
        )

    return investment_summary


@router.post(
    "/{stock_id}",
    response_model=InvestSummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_investment_summary(
    data: InvestSummaryCreate,
    stock_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvestSummaryResponse:

    stock = await get_stock_by_id(stock_id, db, current_user)

    result = await db.execute(
        select(Investment).where(
            Investment.stock_id == stock_id, Investment.user_id == current_user.id
        )
    )
    investment_summary = result.scalar_one_or_none()

    if investment_summary:
        updated_data = data.model_dump(exclude_unset=True)
        for field, value in updated_data.items():
            setattr(investment_summary, field, value)

        await db.commit()
        await db.refresh(investment_summary)
        return investment_summary

    else:
        new_investment_summary = Investment(
            stock_id=stock.id,
            user_id=current_user.id,
            curr_date=data.curr_date,
            current_share_price=data.current_share_price,
            past_4q_revenue=data.past_4q_revenue,
            past_4q_net_profit=data.past_4q_net_profit,
            past_4q_earnings_per_share=data.past_4q_earnings_per_share,
            stock_type=data.stock_type,
            invest=data.invest,
            investment_reasoning=data.investment_reasoning,
        )
        db.add(new_investment_summary)
        await db.commit()
        await db.refresh(new_investment_summary)
        return new_investment_summary
