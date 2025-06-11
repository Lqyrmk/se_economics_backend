import numpy as np
import numpy_financial as npf

from sklearn.linear_model import LinearRegression
from fastapi import APIRouter, Query
from sqlmodel import select
from typing import List, Annotated

from app.dependencies import SessionDep
from app.model.budget_cost import ROI, ROICreate, ROIPublic, NPV, NPVCreate, NPVPublic, IRR, IRRCreate, IRRPublic, \
    PaybackPeriod, PaybackPeriodCreate, PaybackPeriodPublic, ForecastPublic, ForecastCreate

router = APIRouter(
    prefix="/cost",
    tags=["budget_cost"],
    responses={404: {"description": "Not found"}},
)


@router.get("/roi", response_model=list[ROIPublic])
def read_roi_records(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
):
    """
    Show all record.
    """
    roi_records = session.exec(select(ROI).offset(offset).limit(limit)).all()
    return roi_records


def roi(gain: float, cost: float) -> float:
    return ((gain - cost) / cost) * 100


@router.post("/roi", response_model=ROIPublic)
def roi_calculate(cost: ROICreate, session: SessionDep) -> ROIPublic:
    # calculate
    db_cost = ROI.model_validate(cost)
    db_cost.roi_value = roi(cost.gain, cost.cost)
    # database
    session.add(db_cost)
    session.commit()
    session.refresh(db_cost)
    return db_cost


@router.get("/npv", response_model=list[NPVPublic])
def read_npv_records(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
):
    """
    Show all record.
    """
    npv_records = session.exec(select(NPV).offset(offset).limit(limit)).all()
    return npv_records


def npv(c: List[float], r: float) -> float:
    return sum(r_t / (1 + r) ** t for t, r_t in enumerate(c, start=1)) - c[0]


@router.post("/npv", response_model=NPVPublic)
def npv_calculate(cost: NPVCreate, session: SessionDep) -> NPVPublic:
    # calculate
    db_cost = NPV.model_validate(cost)
    db_cost.npv_value = npv(cost.cash_flows, cost.discount_rate)
    # database
    session.add(db_cost)
    session.commit()
    session.refresh(db_cost)
    return db_cost


@router.get("/irr", response_model=list[IRRPublic])
def read_irr_records(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
):
    """
    Show all record.
    """
    irr_records = session.exec(select(IRR).offset(offset).limit(limit)).all()
    return irr_records


@router.post("/irr", response_model=IRRPublic)
def irr_calculate(cost: IRRCreate, session: SessionDep) -> IRRPublic:
    # calculate
    db_cost = IRR.model_validate(cost)
    res = npf.irr(cost.cash_flows) * 100  # 转换为百分比
    if np.isnan(res):
        return IRRPublic(method=db_cost.method, irr_value=None, msg="Incorrect input value")
    db_cost.irr_value = float(res)
    # database
    session.add(db_cost)
    session.commit()
    session.refresh(db_cost)
    return IRRPublic(method=db_cost.method, irr_value=db_cost.irr_value, msg="IRR has been solved")


def payback_period(cash_flows: List[float]):
    cumulative = 0
    for i, cf in enumerate(cash_flows):
        cumulative += cf
        if cumulative >= 0:
            return i
    return None


@router.get("/pp", response_model=list[PaybackPeriodPublic])
def read_pp_records(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
):
    """
    Show all record.
    """
    pp_records = session.exec(select(PaybackPeriod).offset(offset).limit(limit)).all()
    return pp_records


@router.post("/pp", response_model=PaybackPeriodPublic)
def payback_period_calculate(cost: PaybackPeriodCreate, session: SessionDep) -> PaybackPeriodPublic:
    # calculate
    db_cost = PaybackPeriod.model_validate(cost)
    res = payback_period(cost.cash_flows)
    if np.isnan(res) or res is None:
        return PaybackPeriodPublic(method=db_cost.method, pp_value=None, msg="Incorrect input value")
    db_cost.pp_value = res
    # database
    session.add(db_cost)
    session.commit()
    session.refresh(db_cost)
    return PaybackPeriodPublic(method=db_cost.method, pp_value=db_cost.pp_value, msg="Payback Period has been solved")


@router.post("/forecast", response_model=ForecastPublic)
def forecast_costs(cost: ForecastCreate, session: SessionDep) -> ForecastPublic:
    print(f"cost: {cost}")
    historical_data = cost.historical_data
    future_periods = cost.future_periods

    X = np.array(range(len(historical_data))).reshape(-1, 1)
    y = np.array(historical_data)
    model = LinearRegression().fit(X, y)
    future = np.array(range(len(historical_data), len(historical_data) + future_periods)).reshape(-1, 1)
    res = model.predict(future)
    if res is None:
        return ForecastPublic(method="forecast", res=None, msg="Incorrect input value or the model dose not work")
    return ForecastPublic(method="forecast", res=float(res[-1]), msg="Has been solved")
