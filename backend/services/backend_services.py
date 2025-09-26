from ..database.database import create_db, initialize_db, SESSIONS_DB, HOLDINGS_DB, USERS_DB, TRANSACTIONS_DB


class Services():
    def __init__(self):
        self.current_session = SESSIONS_DB.get("session1")
        if not self.current_session:
            initialize_db()

        self.current_user = self.current_session.get("user_id")
        if not self.current_user:
            raise ValueError("No user is currently logged in.")


    def get_holdings(self) -> list:
        """
        Fetch the holdings for the current user
        """
        user_holdings = []
        for holdings in HOLDINGS_DB.holdings:
            if holdings.user_id == self.current_user:
                user_holdings.append(holdings)
        
        return user_holdings
    
    
    def get_transactions(self) -> list:
        """
        Fetch the transactions for the current user
        """
        user_transactions = []
        for transaction in TRANSACTIONS_DB.transactions:
            if transaction.user_id == self.current_user:
                user_transactions.append(transaction)
        
        return user_transactions
    

    def get_users(self) -> list:
        """
        Fetch all users
        """
        return USERS_DB.users
    

    # def get_holdings(user: int):

    #     return [
    #         {"symbol": "AAPL", "quantity": 10, "price": 150.0},
    #         {"symbol": "GOOGL", "quantity": 5, "price": 2800.0},
    #         {"symbol": "AMZN", "quantity": 2, "price": 3400.0}
    #     ]