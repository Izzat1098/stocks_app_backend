from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    exchange = relationship("Exchange", back_populates="user")
    stock = relationship("Stock", back_populates="user")
    financial = relationship("Financial", back_populates="user")
    investment = relationship("Investment", back_populates="user")
    stock_ai_prompt = relationship("StockAiPrompt", back_populates="user")

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, "
            f"username='{self.username}', "
            f"email='{self.email}')>"
        )
