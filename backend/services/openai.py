import logging
import os
import time
from typing import Any

import openai

_openai_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = openai.OpenAI()

    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    _openai_client.api_key = openai_api_key
    # openai.api_key = openai_api_key

    return _openai_client


def _openai_response(
    instructions: str,
    input: str,
    model: str,
    purpose: str = "general",
    **kwargs,
) -> str:
    """
    Helper to call OpenAI ChatCompletion with standard parameters and extra kwargs.
    """
    logging.info(
        f"Calling OpenAI model: {model}, "
        f"Purpose: {purpose}, "
        f"Input: {input} "
        f"with params: {kwargs}"
    )
    client = _get_openai_client()

    try:
        start_ts = time.perf_counter()
        response = client.responses.parse(
            model=model,
            instructions=instructions,
            input=input,
            **kwargs,
        )
        elapsed = time.perf_counter() - start_ts
        logging.info(
            f"OpenAI call status: {response.status}. "
            f"Purpose: {purpose}, Tokens used: "
            f"input_tokens: {response.usage.input_tokens}, "
            f"output_tokens: {response.usage.output_tokens}, "
            f"total_tokens: {response.usage.total_tokens}, "
            f"elapsed={elapsed:.3f}s"
        )

    except Exception as e:
        msg = f"OpenAI request failed: {e}"
        logging.exception(msg)
        raise RuntimeError(msg)

    return response


def query_company_description(
    company_name: str, 
    exchange: str, 
    country: str
) -> Any:
    """
    Get AI description about company.
    """
    instructions = """
        You are a knowledgeable and experienced financial analyst with huge expertise in investment analysis. 
        For the company name provided within the stock exchange or country, provide
        brief and concise description of what is the company about, its main business activities and operations.
        I do not need citations or references.
        Provide the answer in three or four sentences with a character limit of 500.
        If the company is not found, respond with "Company not found".
        """

    input = (
        f"Company Name: {company_name}, "
        f"Stock Exchange: {exchange}, "
        f"Country Name: {country}"
    )

    # max_output_tokens = 1000
    reasoning = {"effort": "medium"}
    text = {"verbosity": "low"}
    # model = "gpt-5"
    model = "gpt-5-mini"
    # model = "gpt-4.1-mini"
    purpose = "company description"
    tools = [{"type": "web_search"}]

    try:
        response = _openai_response(
            instructions=instructions,
            input=input,
            model=model,
            purpose=purpose,
            # max_output_tokens=max_output_tokens,
            # text_format=AnalysisCompany,
            reasoning=reasoning,
            text=text,
            tools=tools,
        )

        output = response.output_text

        if output is None:
            msg = "No valid output from AI"
            logging.error(msg)
            return False, msg

        return True, output

    except Exception as e:
        logging.exception("Analysis API call failed")
        raise RuntimeError(f"OpenAI request failed: {e}")


def query_ai_prompt(
    company_name: str,
    exchange: str,
    country: str,
    prompt: str,
    data: Any = None,
    prev_queries: str = "",
) -> Any:
    """
    Get AI answers about some prompts/questions
    """
    instructions = """
        You are a knowledgeable and experienced financial analyst.
        You also have huge expertise in investment analysis with proven track record in fundamental value investing.
        Your investment philosophy mimics Warren Buffett, Benjamin Graham, Charlie Munger and Peter Lynch.
        For the company name provided within the stock exchange or country, answer the question/prompt provided.
        The Financial Data collected for the company may be provided in the input.
        Previous answer to queries/prompts may also be provided in the input.
        Strictly there must not be any citations, references or links to any source in the answer.
        Strictly provide the answer in three or four sentences with a character limit of 500.
        If the company is not found, respond with "Company not found".
        """

    input = (
        f"Company Name: {company_name}, "
        f"Stock Exchange: {exchange}, "
        f"Country Name: {country}, "
        f"Question/Prompt: {prompt}, "
        f"Financial Data: {data}, "
        f"Previous Queries/Answers: {prev_queries}"
    )

    # max_output_tokens = 1000
    reasoning = {"effort": "medium"}
    text = {"verbosity": "low"}
    # model = "gpt-5"
    model = "gpt-5-mini"
    # model = "gpt-4.1-mini"
    purpose = "company description"
    tools = [{"type": "web_search"}]

    try:
        response = _openai_response(
            instructions=instructions,
            input=input,
            model=model,
            purpose=purpose,
            # max_output_tokens=max_output_tokens,
            # text_format=AnalysisCompany,
            reasoning=reasoning,
            text=text,
            tools=tools,
        )

        output = response.output_text

        if output is None:
            msg = "No valid output from AI"
            logging.error(msg)
            return False, msg

        return True, output

    except Exception as e:
        logging.exception("Analysis API call failed")
        raise RuntimeError(f"OpenAI request failed: {e}")
