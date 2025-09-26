from fastapi import APIRouter, HTTPException
from ..schemas import Stocks, Holding, User, Transaction
from ..services.backend_services import Services

router = APIRouter()

@router.get("/", tags=["Root"])
def root():
    return {"message": "Stock Tracker Backend is running!"}


@router.get("/holdings", response_model=list[Holding])
def get_stocks():
    services = Services()
    holdings = services.get_holdings()
    return holdings


@router.get("/users", response_model=list[User])
def get_users():
    services = Services()
    users = services.get_users()
    return users


@router.get("/transactions", response_model=list[Transaction])
def get_transactions():
    services = Services()
    transactions = services.get_transactions()
    return transactions


# @router.get("/stocks/{list_id}", response_model=StockBase)
# def get_stock(list_id: int = 0):
#     try:
#         return stock_list[list_id]
#     except IndexError:
#         raise HTTPException(status_code=404, detail="Stock not found")

# @router.post("/stock", response_model=StockBase)
# def add_stock(stock: StockBase):
#     stock_list.append(stock)
#     return stock