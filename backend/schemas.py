from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Stock(BaseModel):
    id: int
    symbol: str
    name: str
    exchange: str


class Stocks(BaseModel):
    stocks: list[Stock]


class User(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str
    created_at: Optional[datetime] = None


class Users(BaseModel):
    users: list[User]


class Transaction(BaseModel):
    id: int
    stock_symbol: str
    user_id: int
    type: str
    quantity: int
    price: float
    timestamp: datetime


class Transactions(BaseModel):
    transactions: list[Transaction]


class Holding(BaseModel):
    id: int
    user_id: int
    stock_symbol: str
    quantity: int
    avg_buy_price: float


class Holdings(BaseModel):
    holdings: list[Holding]
