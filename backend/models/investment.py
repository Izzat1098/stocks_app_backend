from datetime import datetime
from typing import Optional

from sqlalchemy import DECIMAL, Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    stock_id: Mapped[int] = mapped_column(
        ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )

    curr_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)

    current_share_price: Mapped[Optional[float]] = mapped_column(
        DECIMAL(6, 2), nullable=True
    )
    past_4q_revenue: Mapped[Optional[float]] = mapped_column(
        DECIMAL(12, 2), nullable=True
    )
    past_4q_net_profit: Mapped[Optional[float]] = mapped_column(
        DECIMAL(12, 2), nullable=True
    )
    past_4q_earnings_per_share: Mapped[Optional[float]] = mapped_column(
        DECIMAL(6, 2), nullable=True
    )

    stock_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    invest: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    investment_reasoning: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="investment")
    stock = relationship("Stock", back_populates="investment")
