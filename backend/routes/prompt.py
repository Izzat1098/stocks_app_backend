import logging
from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.stock import StockAiPrompt

from ..database import get_db
from ..models import User  # SQLAlchemy database model
from ..schemas import FinancialCreate, FinancialMetrics  # Pydantic API schemas
from ..services.auth import get_current_user
from ..services.openai import query_ai_prompt
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
    "Q12": "Check on the latest quarterly results and summarize the key points.",
    # Specialized prompts for value investors with additional rules - see below
    "Q100": "Answer with YES or NO: Based on the financial data and analysis, is this a good company to invest in from a value investor point of view? State your reasons",
    "Q101": "If you recommended to buy this stock in prompt Q100, tell me what the investment strategy should be? Should I buy at current price or wait for lower price? When should I sell?"
}

VALUE_INVESTOR_RULES = """
    These are some rules to follow when answering regarding investment decisions:
    1- Price to Earnings (P/E) ratio should be at similar level with earnings growth rate. If company pays dividend, that can justify some premium on P/E ratio.
    2- Company can be categorized based on earnings growth rate as follows: slow grower (0% to 10%), medium grower (10% to 20%) and fast grower (more than 20%).
    3- Company that don't have consistent earnings growth should be avoided but it can be considered for turnaround, cyclical or asset play investment targets.
    4- Current assets is more than current liabilities. 
    5- Cash is king. Company should have cash more than long term debt, and the cash should increasing over time.
    6- Company has great net profit margin of more than 10%, and gross margin of more than 40%.
    7- Debt to equity ratio should be less than 0.8.
    8- Return on Equity (ROE) should be more than 20%.
    9- Check to ensure that revenue and earnings growth are logical and not due to one-time events, accounting tricks or scam/manipulation.
    10- For Slow grower company, not much share price increase can be expected. We can invest but only for dividend income and that should be more than 6% yield.
    11- For Medium grower company, moderate share price increase can be expected of 20% to 50%. after few years. However, we need to buy at lower price earnings ratio and sell when the share price goes up.
    12- For Fast grower company, very high share price increase upto 100 times (100-baggers) can be expected provided the company can maintain the growth. 
    12- For Fast grower company, we can buy at high price earnings ratio but need to sell when the growth slows down. However, be cautious of very high P/E that is higher than growth rate.
    13- For non-growing company, avoid it entirely unless it is a target of takeover when the target price is 10 percent higher than current price.
    14- Avoid company that is in highly competitive industry without any competitive advantages or moats.
    """

prompts_take_data = ["Q3", "Q4", "Q7", "Q10", "Q100", "Q101"]
prompts_take_previous_prompts = ["Q100", "Q101"]


@router.get("/", response_model=PromptsResponse, status_code=status.HTTP_200_OK)
async def get_prompts(current_user: User = Depends(get_current_user)):
    """Get all available AI prompts"""
    return {"prompts": PROMPTS}


@router.get(
    "/responses/{stock_id}",
    response_model=PromptsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_responses(
    stock_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all AI responses for the current user"""

    result = await db.execute(
        select(StockAiPrompt).where(
            StockAiPrompt.stock_id == stock_id,
            StockAiPrompt.user_id == current_user.id,
        )
    )
    ai_responses = result.scalars().all()

    return {"prompts": {resp.prompt: resp.response for resp in ai_responses}}


def extract_financial_data(financial_data: Dict[str, FinancialMetrics]) -> str:
    """Convert financial data to simple string for OpenAI"""
    lines = []

    for date, metrics in financial_data.items():
        metrics_dict = metrics.model_dump(exclude_none=True)

        # Format each metric as "Field: Value"
        metric_strings = [
            f"{field.replace('_', ' ').title()}: {value:,.2f}"
            for field, value in metrics_dict.items()
            if value is not None
        ]

        lines.append(f"Financial Results: {date} " + ", ".join(metric_strings))

    return "\n".join(lines)


@router.post(
    "/{prompt_id}", response_model=PromptsResponse, status_code=status.HTTP_201_CREATED
)
async def get_ai_response(
    prompt_id: str,
    data: FinancialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    stock = await get_stock_by_id(data.stock_id, db, current_user)

    if prompt_id not in PROMPTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid prompt ID"
        )

    if prompt_id in prompts_take_data:
        financial_info = extract_financial_data(data.data)
    else:
        financial_info = "No financial data provided."

    previous_answers = ""

    if prompt_id in prompts_take_previous_prompts:
        ai_responses = await db.execute(
            select(StockAiPrompt).where(
                StockAiPrompt.stock_id == stock.id,
                StockAiPrompt.user_id == current_user.id,
            )
        )
        ai_responses_all = ai_responses.scalars().all()

        if ai_responses_all:
            for response in ai_responses_all:
                if response.prompt in PROMPTS and response.prompt != prompt_id:
                    previous_answers += f"Prompt id: {response.prompt}, Prompt: {PROMPTS[response.prompt]}, Answer: {response.response}.\n"

    ai_status, ai_response = query_ai_prompt(
        company_name=stock.company_name,
        exchange=stock.exchange.name,
        country=stock.country,
        prompt=PROMPTS[prompt_id],
        add_instruction=VALUE_INVESTOR_RULES if prompt_id in prompts_take_data else "",
        data=financial_info,
        prev_queries=previous_answers,
    )

    if not ai_status:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get AI answer",
        )

    elif "company not found" in ai_response.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found by AI"
        )

    else:
        logging.info(f"AI answer for {stock.company_name} received.")

        truncated = ""
        if len(ai_response) > 500:
            logging.warning(
                f"AI answer length ({len(ai_response)}) exceeds 500 characters. "
                "Response will be truncated."
            )
            truncated = ai_response[:500]
        else:
            truncated = ai_response

        ai_result = await db.execute(
            select(StockAiPrompt).where(
                StockAiPrompt.stock_id == stock.id,
                StockAiPrompt.user_id == current_user.id,
                StockAiPrompt.prompt == prompt_id,
            )
        )
        ai_record = ai_result.scalar_one_or_none()

        # if no existing record, create new
        if not ai_record:
            ai_record = StockAiPrompt(
                stock_id=stock.id,
                user_id=current_user.id,
                prompt=prompt_id,
                response=truncated,
            )
            db.add(ai_record)

        else:
            ai_record.prompt = prompt_id
            ai_record.response = truncated
            ai_record.created_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(ai_record)

        return {"prompts": {prompt_id: ai_record.response}}
