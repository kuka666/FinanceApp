import asyncio
from typing import Dict, Any
import numpy_financial as npf
from models import UserInput, ResponseAdvice
from fastapi import HTTPException

# Constants for clarity
PERCENTAGE_BASE = 100.0
MONTHS_PER_YEAR = 12

def calculate_inflation_factor(rate: float, years: int) -> float:
    """
    Calculate the compound inflation factor over a given period.

    Args:
        rate: Annual inflation rate as a percentage (e.g., 5.0 for 5%).
        years: Number of years.

    Returns:
        Inflation factor (e.g., 1.05^years).
    """
    return (1 + rate / PERCENTAGE_BASE) ** years

def calculate_monthly_savings(
    future_value: float,
    present_value: float,
    annual_rate: float,
    years: int
) -> float:
    """
    Calculate monthly savings needed to reach a future value with compound interest.

    Args:
        future_value: Target amount adjusted for inflation.
        present_value: Current savings.
        annual_rate: Annual investment return rate as a percentage.
        years: Number of years to save.

    Returns:
        Monthly savings amount.

    Raises:
        ValueError: If years is zero or negative, or if rate calculation fails.
    """
    if years <= 0:
        raise ValueError("Years must be positive")
    
    monthly_rate = annual_rate / PERCENTAGE_BASE / MONTHS_PER_YEAR
    total_months = years * MONTHS_PER_YEAR
    
    # Future value of present savings
    pv_future = present_value * (1 + monthly_rate) ** total_months
    
    # Amount still needed
    savings_needed = future_value - pv_future
    
    if monthly_rate == 0:
        if total_months == 0:
            raise ValueError("Cannot calculate savings with zero rate and zero months")
        return savings_needed / total_months
    
    # Use numpy_financial.pmt for precision and readability
    monthly_savings = npf.pmt(
        rate=monthly_rate,
        nper=total_months,
        pv=0,  # No additional present value beyond initial savings
        fv=-savings_needed  # Negative because it's the target to reach
    )
    return max(monthly_savings, 0)  # Ensure non-negative result

def calculate_full_information(user_input: UserInput) -> Dict[str, float]:
    """
    Compute financial savings plan based on user input across three scenarios.

    Args:
        user_input: User-provided financial data (income, expenses, rates, etc.).

    Returns:
        Dictionary with calculated financial metrics matching ResponseAdvice.

    Raises:
        ValueError: If calculations encounter invalid inputs (e.g., zero years).
    """
    try:
        # Basic calculations
        remain_money = user_input.required_capital - user_input.current_savings
        balance = user_input.monthly_income - user_input.monthly_expenses

        # Inflation factors for each scenario
        inflation_optimist = calculate_inflation_factor(user_input.inflow, user_input.optimist_years)
        inflation_base = calculate_inflation_factor(user_input.inflow, user_input.base_year)
        inflation_pessimist = calculate_inflation_factor(user_input.inflow, user_input.pessimist_years)

        # Future values adjusted for inflation
        need_capital_optimist = user_input.required_capital * inflation_optimist
        need_capital_base = user_input.required_capital * inflation_base
        need_capital_pessimist = user_input.required_capital * inflation_pessimist

        # Monthly savings for each scenario
        month_save_optimist = calculate_monthly_savings(
            need_capital_optimist,
            user_input.current_savings,
            user_input.optimist_procent,
            user_input.optimist_years
        )
        month_save_base = calculate_monthly_savings(
            need_capital_base,
            user_input.current_savings,
            user_input.base_procent,
            user_input.base_year
        )
        month_save_pessimist = calculate_monthly_savings(
            need_capital_pessimist,
            user_input.current_savings,
            user_input.pessimist_procent,
            user_input.pessimist_years
        )

        # Construct result
        return {
            "remain_money": remain_money,
            "balance": balance,
            "month_save_optimist": month_save_optimist,
            "month_save_base": month_save_base,
            "month_save_pessimist": month_save_pessimist,
            "need_capital_with_inflation_optimist": need_capital_optimist,
            "need_capital_with_inflation_base": need_capital_base,
            "need_capital_with_inflation_pessimist": need_capital_pessimist,
            "inflation_full_period_optimist": inflation_optimist,
            "inflation_full_period_base": inflation_base,
            "inflation_full_period_pessimist": inflation_pessimist,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def calculate_full(user_input: UserInput) -> ResponseAdvice:
    """
    Asynchronously calculate financial advice based on user input.

    Args:
        user_input: User-provided financial data.

    Returns:
        ResponseAdvice object with calculated savings plan.

    Raises:
        HTTPException: Propagates errors from calculate_full_information.
    """
    # Synchronous call since computation is lightweight
    result = calculate_full_information(user_input)
    return ResponseAdvice(**result)