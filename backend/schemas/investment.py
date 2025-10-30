from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InvestSummaryCreate(BaseModel):
    curr_date: Optional[str] = Field(
        None, description="Date of the investment summary in YYYY-MM-DD format"
    )
    current_share_price: Optional[float] = Field(None, ge=0)
    past_4q_revenue: Optional[float] = Field(None, ge=0)
    past_4q_net_profit: Optional[float] = Field(None, ge=0)
    past_4q_earnings_per_share: Optional[float] = Field(None, ge=0)

    stock_type: Optional[str] = Field(None, max_length=50, description="Stock name")
    invest: Optional[str] = Field(
        None, max_length=50, description="Investment decision"
    )
    investment_reasoning: Optional[str] = Field(
        None, max_length=500, description="Investment reasoning"
    )

    @field_validator("curr_date")
    @classmethod
    def validate_dates(cls, v):
        """Validate that keys are valid dates"""
        if v is None:
            return None
        if isinstance(v, date):
            return v

        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {v}. Use YYYY-MM-DD")


class InvestSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    curr_date: Optional[date]
    current_share_price: Optional[float]
    past_4q_revenue: Optional[float]
    past_4q_net_profit: Optional[float]
    past_4q_earnings_per_share: Optional[float]

    stock_type: Optional[str]
    invest: Optional[str]
    investment_reasoning: Optional[str]
    created_at: Optional[datetime]
