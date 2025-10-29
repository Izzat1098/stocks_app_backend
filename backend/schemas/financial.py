from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

class FinancialMetrics(BaseModel):
    """Schema for individual year's financial metrics"""
    # per share infor
    share_price_at_report_date: Optional[float] = Field(None, ge=0)
    max_share_price: Optional[float] = Field(None, ge=0)
    min_share_price: Optional[float] = Field(None, ge=0)
    earnings_per_share: Optional[float] = Field(None)
    dividend_per_share: Optional[float] = Field(None, ge=0)

    # profit loss
    revenue: Optional[float] = Field(None)
    gross_profit: Optional[float] = Field(None)
    profit_before_tax: Optional[float] = Field(None)
    profit_after_tax: Optional[float] = Field(None)
    profit_after_tax_for_shareholders: Optional[float] = Field(None)

    # current assets
    cash: Optional[float] = Field(None)
    inventories: Optional[float] = Field(None)
    receivables: Optional[float] = Field(None)
    investments_in_securities: Optional[float] = Field(None)
    other_current_assets: Optional[float] = Field(None)

    # non-current assets
    property_plant_equipment: Optional[float] = Field(None)
    land_and_real_estate: Optional[float] = Field(None)
    investments_subsidiaries: Optional[float] = Field(None)
    intangible_assets: Optional[float] = Field(None)
    non_current_investments: Optional[float] = Field(None)
    other_non_current_assets: Optional[float] = Field(None)

    # current liabilities
    borrowings: Optional[float] = Field(None)
    payables: Optional[float] = Field(None)
    lease_liabilities: Optional[float] = Field(None)
    tax_liabilities: Optional[float] = Field(None)
    other_current_liabilities: Optional[float] = Field(None)

    # non-current liabilities
    long_term_debts: Optional[float] = Field(None)
    long_term_lease_liabilities: Optional[float] = Field(None)
    deferred_tax_liabilities: Optional[float] = Field(None)
    other_non_current_liabilities: Optional[float] = Field(None)

    # equity
    share_capital: Optional[float] = Field(None)
    retained_earnings: Optional[float] = Field(None)
    reserves: Optional[float] = Field(None)
    non_controlling_interests: Optional[float] = Field(None)

    # cash flow
    net_cash_from_operating_activities: Optional[float] = Field(None)
    investments_in_ppe: Optional[float] = Field(None)
    investments_in_subsidiaries: Optional[float] = Field(None)
    investments_in_acquisitions: Optional[float] = Field(None)


class FinancialDataBase(BaseModel):
    """Base schema with common financial data structure"""
    stock_id: int = Field(..., gt=0, description="ID of the stock")
    data: Dict[str, FinancialMetrics] = Field(
        ..., 
        description="Financial data by date (YYYY-MM-DD format)"
    )

    @field_validator('data')
    @classmethod
    def validate_dates(cls, v):
        """Validate that keys are valid dates"""
        for date_str in v.keys():
            try:
                datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")
        return v
    
    
class FinancialCreate(FinancialDataBase):
    """Schema for bulk financial data creation"""
    pass  # Inherits everything from FinancialDataBase


class FinancialResponse(FinancialDataBase):
    """Schema for bulk financial data response"""
    model_config = ConfigDict(from_attributes=True)
    
    # Add response-specific fields if needed
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None