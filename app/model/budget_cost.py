from typing import Annotated, Optional, Dict, Literal, List, Tuple
from sqlmodel import Field, SQLModel


class BudgetCostBase(SQLModel):
    method: str = Field(index=True)


# roi
class ROI(BudgetCostBase, table=True):
    __tablename__ = "budget_roi"
    id: Optional[int] = Field(default=None, primary_key=True)
    method: Optional[str] = Field(default="roi")
    gain: Optional[float] = Field(default=20.0)
    cost: Optional[float] = Field(default=10.0)
    roi_value: Optional[float] = Field(default=0.0)

class ROICreate(BudgetCostBase):
    method: Optional[str] = Field(default="roi")
    gain: Optional[float] = Field(default=20.0)
    cost: Optional[float] = Field(default=10.0)


class ROIPublic(BudgetCostBase):
    method: str
    roi_value: float


# npv
class NPV(BudgetCostBase, table=True):
    __tablename__ = "budget_npv"
    id: Optional[int] = Field(default=None, primary_key=True)
    method: Optional[str] = Field(default="npv")
    discount_rate: float
    npv_value: Optional[float] = Field(default=0.0)


class NPVCreate(BudgetCostBase):
    method: Optional[str] = Field(default="npv")
    cash_flows: List[float]
    discount_rate: float


class NPVPublic(BudgetCostBase):
    method: str
    npv_value: float


# irr
class IRR(BudgetCostBase, table=True):
    __tablename__ = "budget_irr"
    id: Optional[int] = Field(default=None, primary_key=True)
    method: Optional[str] = Field(default="irr")
    irr_value: Optional[float] = Field(default=0.0)


class IRRCreate(BudgetCostBase):
    method: Optional[str] = Field(default="irr")
    cash_flows: List[float]


class IRRPublic(BudgetCostBase):
    method: str
    irr_value: float
    msg: str = "record"


# Payback Period
class PaybackPeriod(BudgetCostBase, table=True):
    __tablename__ = "budget_payback_period"
    id: Optional[int] = Field(default=None, primary_key=True)
    method: Optional[str] = Field(default="pp")
    pp_value: Optional[float] = Field(default=0.0)


class PaybackPeriodCreate(BudgetCostBase):
    method: Optional[str] = Field(default="pp")
    cash_flows: List[float]


class PaybackPeriodPublic(BudgetCostBase):
    method: str
    pp_value: float
    msg: str = "record"


class ForecastCreate(BudgetCostBase):
    method: Optional[str] = Field(default="forecast")
    historical_data: List[float]
    future_periods: int

class ForecastPublic(BudgetCostBase):
    method: str
    res: float
    msg: str