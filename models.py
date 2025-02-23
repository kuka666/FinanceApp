from pydantic import BaseModel, Field, confloat, conint, field_validator, ValidationInfo
from typing import Optional

class UserInput(BaseModel):
    required_capital: conint(ge=0) = Field(..., description="Необходимая сумма для цели (в тенге), например, стоимость квартиры")
    current_savings: confloat(ge=0) = Field(..., description="Текущие накопления (в тенге)")
    optimist_years: conint(ge=1) = Field(..., description="Количество лет для накопления по оптимистичному сценарию")
    base_year: conint(ge=1) = Field(..., description="Базовое количество лет для накоплений")
    pessimist_years: conint(ge=1) = Field(..., description="Количество лет для накопления по пессимистичному сценарию")
    inflow: confloat(ge=0) = Field(..., description="Прогнозируемая инфляция в процентах ежегодно")
    income_from_investing: confloat(ge=0) = Field(..., description="Ежегодный доход от инвестиций (в процентах)")
    monthly_income: confloat(ge=0) = Field(..., description="Ежемесячный доход (в тенге)")
    monthly_expenses: confloat(ge=0) = Field(..., description="Ежемесячные расходы (в тенге)")
    optimist_procent: confloat(ge=0, le=100) = Field(..., description="Процент доходности по оптимистичному сценарию")
    base_procent: confloat(ge=0, le=100) = Field(..., description="Процент доходности по базовому сценарию")
    pessimist_procent: confloat(ge=0, le=100) = Field(..., description="Процент доходности по пессимистичному сценарию")

    @field_validator('optimist_years', 'base_year', 'pessimist_years')
    @classmethod
    def check_years(cls, v: int, info: ValidationInfo) -> int:
        if v < 1:
            raise ValueError(f"{info.field_name} должно быть больше или равно 1 году.")
        return v
    
    @field_validator('optimist_procent', 'base_procent', 'pessimist_procent')
    @classmethod
    def check_percentage(cls, v: float, info: ValidationInfo) -> float:
        if v < 0 or v > 100:
            raise ValueError(f"{info.field_name} должно быть в пределах от 0 до 100.")
        return v

    @field_validator('inflow')
    @classmethod
    def check_inflation(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Инфляция не может быть отрицательной.")
        return v

    @field_validator('income_from_investing')
    @classmethod
    def check_investment_income(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Доход от инвестиций не может быть отрицательным.")
        return v

class ResponseAdvice(BaseModel):
    remain_money: confloat(ge=0) = Field(..., description="Остаток денег после достижения цели (в тенге)")
    balance: confloat() = Field(..., description="Ежемесячный остаток после расходов (доход - расходы, в тенге)")  
    month_save_optimist: confloat(ge=0) = Field(..., description="Ежемесячные сбережения по оптимистичному сценарию (в тенге)")
    month_save_base: confloat(ge=0) = Field(..., description="Ежемесячные сбережения по базовому сценарию (в тенге)")
    month_save_pessimist: confloat(ge=0) = Field(..., description="Ежемесячные сбережения по пессимистичному сценарию (в тенге)")
    need_capital_with_inflation_optimist: confloat(ge=0) = Field(..., description="Необходимый капитал с учетом инфляции по оптимистичному сценарию (в тенге)")
    need_capital_with_inflation_base: confloat(ge=0) = Field(..., description="Необходимый капитал с учетом инфляции по базовому сценарию (в тенге)")
    need_capital_with_inflation_pessimist: confloat(ge=0) = Field(..., description="Необходимый капитал с учетом инфляции по пессимистичному сценарию (в тенге)")
    inflation_full_period_optimist: confloat(ge=0) = Field(..., description="Общая инфляция за период по оптимистичному сценарию (коэффициент)")
    inflation_full_period_base: confloat(ge=0) = Field(..., description="Общая инфляция за период по базовому сценарию (коэффициент)")
    inflation_full_period_pessimist: confloat(ge=0) = Field(..., description="Общая инфляция за период по пессимистичному сценарию (коэффициент)")

    @field_validator('remain_money', 'month_save_optimist', 'month_save_base', 'month_save_pessimist', 
                     'need_capital_with_inflation_optimist', 'need_capital_with_inflation_base', 
                     'need_capital_with_inflation_pessimist', 'inflation_full_period_optimist', 
                     'inflation_full_period_base', 'inflation_full_period_pessimist')
    @classmethod
    def check_non_negative(cls, v: float, info: ValidationInfo) -> float:
        if v < 0:
            raise ValueError(f"{info.field_name} не может быть отрицательным.")
        return v