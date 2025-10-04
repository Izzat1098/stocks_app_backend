from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/reference", tags=["reference-data"])

class CountryResponse(BaseModel):
    name: str

class SectorResponse(BaseModel):
    name: str

# Predefined lists of countries and sectors
COUNTRIES = [
    "United States",
    # "Canada",
    # "United Kingdom",
    # "Germany",
    # "France",
    # "Italy",
    # "Spain",
    # "Netherlands",
    # "Switzerland",
    # "Sweden",
    # "Norway",
    # "Denmark",
    # "Finland",
    # "Japan",
    # "South Korea",
    # "China",
    # "Hong Kong",
    # "Singapore",
    # "Australia",
    # "New Zealand",
    # "India",
    # "Brazil",
    # "Mexico",
    # "Argentina",
    # "Chile",
    # "South Africa",
    # "Russia",
    # "Turkey",
    # "Saudi Arabia",
    # "United Arab Emirates",
    "Malaysia"
]

SECTORS = [
    "Agriculture",
    "Aerospace & Defense",
    "Automotive",
    "Banking",
    "Biotechnology",
    "Communication Services",
    "Construction",
    "Consumer Discretionary",
    "Consumer Staples",
    "Energy",
    "Financial Services",
    "Food & Beverages",
    "Healthcare",
    "Industrials",
    "Insurance",
    "Materials",
    "Media & Entertainment",
    "Mining",
    "Pharmaceuticals",
    "Real Estate",
    "Retail",
    "Technology",
    "Textiles",
    "Transportation",
    "Utilities",
]



@router.get("/countries", response_model=List[CountryResponse])
async def get_countries():
    """
    Get list of supported countries
    """
    response = [CountryResponse(name=country) for country in sorted(COUNTRIES)]
    return response


@router.get("/sectors", response_model=List[SectorResponse])
async def get_sectors():
    """
    Get list of stock sectors
    """
    response = [SectorResponse(name=sector) for sector in sorted(SECTORS)]
    return response