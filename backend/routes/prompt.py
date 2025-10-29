from typing import List, Dict
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
from datetime import datetime, timedelta, timezone

from backend.models.stock import StockAiPrompt

from ..database import get_db
from ..models import User, Exchange, Stock, Financial  # SQLAlchemy database model
from ..schemas import FinancialMetrics, FinancialDataBase, FinancialCreate  # Pydantic API schemas
from ..services.auth import get_current_user
from ..services.openai import query_ai_prompt, query_company_description
from .stocks import get_stock_by_id

class PromptsResponse(BaseModel):
    """Response schema for prompts endpoint"""
    prompts: Dict[str, str]

router = APIRouter(prefix="/prompts", tags=["prompts"])

PROMPTS = {
    "Q1": "What is the business the company does and how is it profitable?",
    "Q2": "Who are the competitors? Does this company have any competitive advantages or moats over them?",
    "Q3": "Based on the company's revenue and earnings trend, what is the contributing factors to the growth or decline?",
    "Q4": "What is the category of the company? Is it slow/medium/fast grower, cyclical, or speculative?",
    "Q5": "What are the risks and challenges the company is facing?",
    "Q6": "What are the company's recent developments and future plans?",
    "Q7": "Did the company had acquisitions or other investments in the past 5 years? If yes, how successful or impactful were they to its financial result?",
    "Q8": "What is the company's management like? Do they have a good track record?",
    "Q9": "What is the company's status of balance sheet and cash flow? Is it creating or destroying value?",
    "Q10": "What is the company's valuation? Is it undervalued or overvalued compared to its peers and historical averages?",
    "Q11": "What is the overall outlook for the company and its industry?",
    "Q12": "Based on the analysis, would you consider investing in this company from a fundamental value investor point of view?"
}

prompts_take_data = ["Q3", "Q4", "Q7", "Q10", "Q12"]
prompts_take_previous_prompts = ["Q12"]


@router.get("/", response_model=PromptsResponse, status_code=status.HTTP_200_OK)
async def get_prompts(
    current_user: User = Depends(get_current_user)
):
    """Get all available AI prompts"""
    return {"prompts": PROMPTS}


@router.get("/responses/{stock_id}", response_model=PromptsResponse, status_code=status.HTTP_200_OK)
async def get_responses(
    stock_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all AI responses for the current user"""

    result = await db.execute(
        select(StockAiPrompt)
        .where(
            StockAiPrompt.stock_id == stock_id,
            StockAiPrompt.user_id == current_user.id,
        )
    )
    ai_responses = result.scalars().all()

    return {"prompts": 
            {resp.prompt: resp.response for resp in ai_responses}
        }


def extract_financial_data(financial_data: Dict[str, FinancialMetrics]) -> str:
    """Convert financial data to simple string for OpenAI"""
    lines = []
    
    for date, metrics in financial_data.items():
        metrics_dict = metrics.model_dump(exclude_none=True)
        
        # Format each metric as "Field: Value"
        metric_strings = [f"{field.replace('_', ' ').title()}: {value:,.2f}" 
                         for field, value in metrics_dict.items() if value is not None]
        
        lines.append(f"Financial Results: {date} " + ", ".join(metric_strings))
    
    return "\n".join(lines)


@router.post("/{prompt_id}", response_model=PromptsResponse, status_code=status.HTTP_201_CREATED)
async def get_ai_response(
    prompt_id: str,
    data: FinancialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    stock = await get_stock_by_id(data.stock_id, db, current_user)

    
    if prompt_id not in PROMPTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid prompt ID"
        )
    
    if prompt_id in prompts_take_data:
        financial_info = extract_financial_data(data.data)
    else: 
        financial_info = "No financial data provided."

    previous_answers = ""

    if prompt_id in prompts_take_previous_prompts :
        ai_responses = await db.execute(
            select(StockAiPrompt)
            .where(
                StockAiPrompt.stock_id == stock.id,
                StockAiPrompt.user_id == current_user.id,
            )
        )
        ai_responses_all = ai_responses.scalars().all()

        if ai_responses_all:
            previous_answers = "\n".join([f"{PROMPTS[response.prompt]}: {response.response}" for response in ai_responses_all])


    ai_status, ai_response = query_ai_prompt(stock.company_name, stock.exchange.name, stock.country, PROMPTS[prompt_id], financial_info, previous_answers)

    if not ai_status:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get AI answer"
        )
    
    elif "company not found" in ai_response.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found by AI"
        )

    else:
        logging.info(f"AI answer for {stock.company_name} received.")

        if len(ai_response) > 500:
            logging.warning(f"AI answer length ({len(ai_response)}) exceeds 500 characters. Response will be truncated.")

        truncated = ai_response[:500] if len(ai_response) > 500 else ai_response

        ai_result = await db.execute(
            select(StockAiPrompt)
            .where(
                StockAiPrompt.stock_id == stock.id,
                StockAiPrompt.user_id == current_user.id,
                StockAiPrompt.prompt == prompt_id
            )
        )
        ai_record = ai_result.scalar_one_or_none()

        # if no existing record, create new
        if not ai_record:
            ai_record = StockAiPrompt(
                stock_id=stock.id,
                user_id=current_user.id,
                prompt=prompt_id,
                response=truncated
            )
            db.add(ai_record)

        else:
            ai_record.prompt = prompt_id
            ai_record.response = truncated
            ai_record.created_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(ai_record)

        return {"prompts": {
            prompt_id: ai_record.response
        }}