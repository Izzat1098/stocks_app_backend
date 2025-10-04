from datetime import datetime
from ipaddress import v4_int_to_packed
from typing import Optional, Literal
from wsgiref import validate
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from .util import valid_country, valid_sector, validate_country_required, validate_country_optional, validate_sector_optional


class ExchangeCreate(BaseModel):
    abbreviation: str = Field(..., max_length=10, description="Exchange abbreviation (e.g., NYSE)")
    name: str = Field(..., max_length=100, description="Full exchange name")
    country: str = Field(..., max_length=50, description="Country name (e.g., United States, Malaysia)")

    @field_validator('country')
    @classmethod
    def validate_country(cls, v):
        """Ensure country is valid and in title case"""
        return validate_country_required(v)

    @field_validator('abbreviation')
    @classmethod
    def validate_abbreviation(cls, v):
        """Ensure abbreviation is always uppercase"""
        return v.upper()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Ensure name is always in title case"""
        return v.title()

class ExchangeUpdate(BaseModel):
    abbreviation: Optional[str] = Field(None, max_length=10)
    name: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=50)

    @field_validator('country')
    @classmethod
    def validate_country(cls, v):
        """Ensure country is valid and in title case"""
        return validate_country_required(v)

    @field_validator('abbreviation')
    @classmethod
    def validate_abbreviation(cls, v):
        """Ensure abbreviation is always uppercase"""
        return v.upper()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Ensure name is always in title case"""
        return v.title()

class ExchangeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    abbreviation: str
    name: str
    country: str
    created_at: datetime


class StockCreate(BaseModel):
    ticker: str = Field(..., max_length=10, description="Stock ticker symbol (e.g., AAPL)")
    company_name: str = Field(..., max_length=50, description="Full company name")
    abbreviation: Optional[str] = Field(None, max_length=10, description="Company abbreviation")
    exchange_id: Optional[int] = Field(None, gt=0, description="ID of the exchange where stock is listed")
    sector: Optional[str] = Field(None, max_length=50, description="Business sector code")
    country: Optional[str] = Field(None, max_length=50, description="Country name (e.g., United States, Malaysia)")
    description: Optional[str] = Field(None, max_length=500, description="Detailed company description")
    ai_description: Optional[str] = Field(None, max_length=500, description="AI-generated description")

    @field_validator('country')
    @classmethod
    def validate_country(cls, v):
        """Ensure country is valid and in title case"""
        return validate_country_optional(v)
    
    @field_validator('sector')
    @classmethod
    def validate_sector(cls, v):
        """Ensure sector is valid and in title case"""
        return validate_sector_optional(v)

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v):
        """Ensure ticker is always uppercase"""
        return v.upper()
    
    @field_validator('abbreviation')
    @classmethod
    def validate_abbreviation(cls, v):
        """Ensure abbreviation is always uppercase"""
        return v.upper()
    
    @field_validator('company_name')
    @classmethod
    def validate_company_name(cls, v):
        """Ensure company_name is always in title case"""
        return v.title()
    
class StockUpdate(BaseModel):
    ticker: Optional[str] = Field(None, max_length=10)
    company_name: Optional[str] = Field(None, max_length=50)
    abbreviation: Optional[str] = Field(None, max_length=10)
    exchange_id: Optional[int] = Field(None, gt=0)
    sector: Optional[str] = Field(None, max_length=50, description="Business sector code")
    country: Optional[str] = Field(None, max_length=50, description="Country name (e.g., United States, Malaysia)")
    description: Optional[str] = Field(None, max_length=500)
    ai_description: Optional[str] = Field(None, max_length=500, description="AI-generated description")

    @field_validator('country')
    @classmethod
    def validate_country(cls, v):
        """Ensure country is valid and in title case"""
        return validate_country_optional(v)
    
    @field_validator('sector')
    @classmethod
    def validate_sector(cls, v):
        """Ensure sector is valid and in title case"""
        return validate_sector_optional(v)

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v):
        """Ensure ticker is always uppercase"""
        return v.upper()
    
    @field_validator('abbreviation')
    @classmethod
    def validate_abbreviation(cls, v):
        """Ensure abbreviation is always uppercase"""
        return v.upper()
    
    @field_validator('company_name')
    @classmethod
    def validate_company_name(cls, v):
        """Ensure company_name is always in title case"""
        return v.title()
    
class StockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    ticker: str
    company_name: str
    abbreviation: Optional[str]
    exchange_id: Optional[int]
    sector: Optional[str]
    country: Optional[str]
    created_at: datetime
    description: Optional[str]
    ai_description: Optional[str]


class FinancialCreate(BaseModel):
    stock_id: int = Field(..., gt=0, description="ID of the stock this financial data belongs to")
    year: int = Field(..., ge=1900, le=2100, description="Financial year")
    field: str = Field(..., max_length=50, description="Financial metric name (e.g., revenue)")
    value: float = Field(..., description="Financial value")

    @field_validator('field')
    @classmethod
    def validate_field(cls, v):
        """Ensure field is always in title case"""
        return v.title()
    
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

class FinancialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    stock_id: int
    year: int
    field: str
    value: float
    created_at: datetime