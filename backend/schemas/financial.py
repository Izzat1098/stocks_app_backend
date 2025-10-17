from datetime import datetime
from ipaddress import v4_int_to_packed
from typing import Dict, Optional
from wsgiref import validate
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

class FinancialMetrics(BaseModel):
    """Schema for individual year's financial metrics"""
    share_price: Optional[float] = Field(None, ge=0)
    revenue: Optional[float] = Field(None)
    earnings: Optional[float] = Field(None)
    earnings_per_share: Optional[float] = Field(None)


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


class FinancialUpdate(BaseModel):
    stock_id: Optional[int] = Field(None, gt=0)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    field: Optional[str] = Field(None, max_length=50)
    value: Optional[float] = None

    @field_validator('field')
    @classmethod
    def validate_field(cls, v):
        """Ensure field is always in title case"""
        return v.title()