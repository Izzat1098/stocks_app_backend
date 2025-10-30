from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Exchange(Base):
    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    abbreviation: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="exchange")
    stocks = relationship("Stock", back_populates="exchange")

    def __repr__(self) -> str:
        return (
            f"<Exchange(id={self.id}, "
            f"abbreviation='{self.abbreviation}', "
            f"name='{self.name}', country='{self.country}')>"
        )


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    ticker: Mapped[str] = mapped_column(String(10), nullable=False)
    company_name: Mapped[str] = mapped_column(String(50), nullable=False)
    abbreviation: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    exchange_id: Mapped[int] = mapped_column(
        ForeignKey("exchanges.id", ondelete="SET NULL"), nullable=True
    )
    sector: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ai_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ai_description_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="stock")
    financial = relationship(
        "Financial", back_populates="stock", cascade="all, delete-orphan"
    )
    investment = relationship(
        "Investment", back_populates="stock", cascade="all, delete-orphan"
    )
    exchange = relationship("Exchange", back_populates="stocks")
    stock_ai_prompt = relationship(
        "StockAiPrompt", back_populates="stock", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Stock(id={self.id}, ticker='{self.ticker}', "
            f"company_name='{self.company_name}', "
            f"exchange_id={self.exchange_id})>"
        )


class StockAiPrompt(Base):
    __tablename__ = "stock_ai_prompts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    stock_id: Mapped[int] = mapped_column(
        ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )
    prompt: Mapped[str] = mapped_column(String(10), nullable=True)
    response: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="stock_ai_prompt")
    stock = relationship("Stock", back_populates="stock_ai_prompt")

    def __repr__(self) -> str:
        return (
            f"<StockAiPrompt(id={self.id}, stock_id={self.stock_id}, "
            f"created_at={self.created_at})>"
        )
