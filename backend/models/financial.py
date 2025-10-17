from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, DateTime, Date, Integer, Numeric, Text, func, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Financial(Base):
    __tablename__ = "financials"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    year: Mapped[Date] = mapped_column(Date, nullable=False)
    field: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="financial")
    stock = relationship("Stock", back_populates="financial")
