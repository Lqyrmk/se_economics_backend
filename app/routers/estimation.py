import random
import numpy as np

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from typing import Annotated, List, Tuple, Dict

from app.dependencies import SessionDep
from app.model.estimation import EstimationPublic, CocomoCreate, Estimation, FunctionPointsCreate, ExpertCreate, \
    DelphiCreate, RegressionCreate, EstimationBase

router = APIRouter(
    prefix="/estimate",
    tags=["estimation"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[EstimationPublic])
def read_estimations(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
):
    """
    Show all estimations.
    """
    estimations = session.exec(select(Estimation).offset(offset).limit(limit)).all()
    print(f"Estimations: {estimations}")
    return estimations


def common_db_post(res: Dict, estimation: EstimationBase, session: SessionDep) -> EstimationPublic:
    """
    common operation of DB while creating an estimation
    """
    db_estimation = Estimation.model_validate(estimation)
    db_estimation.effort = res['effort']
    db_estimation.time = res['time']
    # write to database
    session.add(db_estimation)
    session.commit()
    session.refresh(db_estimation)
    return db_estimation


# 1. Empirical Estimation
def cocomo_model(kloc: float, complexity: str) -> Dict:
    """
    COCOMO model:
    Effort = a * (KLOC) ^ b
    Time = c * (KLOC) ^ d
    [a, b, c, d] are adjusted according to complexity

    :param kloc: kilo line of code
    :param complexity: complexity of the project
    :return: res
    """
    params = {
        "organic": (2.4, 1.05, 2.5, 0.38),
        "semi": (3.0, 1.12, 2.5, 0.35),
        "embedded": (3.6, 1.20, 2.5, 0.32)
    }
    a, b, c, d = params.get(complexity, params["organic"])
    effort = a * (kloc ** b)
    time = c * (effort ** d)
    res = {
        "effort": effort,
        "time": time,
    }
    return res


@router.post("/empirical/cocomo", response_model=EstimationPublic)
def cocomo_estimate(estimation: CocomoCreate, session: SessionDep) -> EstimationPublic:
    """
    Interface of COCOMO model
    """
    # calculate
    res = cocomo_model(estimation.size, estimation.complexity)
    # database
    db_estimation = common_db_post(res, estimation, session)
    return db_estimation


def function_points_analysis(fp: float, complexity: str) -> Dict:
    """
    Function Points Analysis (FPA)
    Effort = FP * multiplier
    multiplier are adjusted according to complexity
    :param fp: function point multiplier
    :param complexity: complexity of the project
    :return: res
    """
    multipliers = {
        "low": 1.0,
        "medium": 1.2,
        "high": 1.5
    }
    multiplier = multipliers.get(complexity, 1.2)
    effort = fp * multiplier
    res = {
        "effort": effort,
        "time": -1,
    }
    return res


@router.post("/empirical/function_points", response_model=EstimationPublic)
def function_points_estimate(estimation: FunctionPointsCreate, session: SessionDep) -> EstimationPublic:
    """
    Interface of Function Points Analysis (FPA)
    """
    # calculate
    res = function_points_analysis(estimation.size, estimation.complexity)
    # database
    db_estimation = common_db_post(res, estimation, session)
    return db_estimation


# 2. Heuristic Estimation
def expert_judgment(size: float, experience: int) -> Dict:
    """
    Expert Judgment
    Assume that the experts give estimates based on scale and experience:
    The larger the scale, the more person-months;
    the more experienced, the more efficient (fewer person-month)
    :param size: scale of project
    :param experience: experience level of several provided experts
    :return: res
    """
    noise = random.uniform(-0.2, 0.2)  # +/-20%波动
    base = size * (1.0 + noise)
    adjustment = max(0.5, 3 - experience) * 0.3  # 经验越高调整越小
    effort = base * adjustment
    res = {
        "effort": effort,
        "time": -1,
    }
    return res


@router.post("/heuristic/expert", response_model=EstimationPublic)
def expert_judgment_estimate(estimation: ExpertCreate, session: SessionDep) -> EstimationPublic:
    """
    Interface of Expert Judgment
    """
    # calculate
    res = expert_judgment(estimation.size, estimation.experience)
    # database
    db_estimation = common_db_post(res, estimation, session)
    return db_estimation


def delphi_method(size: float, experience_list: List[int]) -> Dict:
    """
    Here we use random simulation to estimate multiple times and then take the average
    :param size: scale of project
    :param experience_list: multiple experience levels in multiple rounds of evaluation
    :return: res
    """
    effort = sum(expert_judgment(size, e) for e in experience_list) / len(experience_list)
    res = {
        "effort": effort,
        "time": -1,
    }
    return res


@router.post("/heuristic/delphi", response_model=EstimationPublic)
def delphi_method_estimate(estimation: DelphiCreate, session: SessionDep) -> EstimationPublic:
    """
    Interface of Delphi Method Estimation
    """
    # calculate
    res = expert_judgment(estimation.size, estimation.experience_list)
    # database
    db_estimation = common_db_post(res, estimation, session)
    return db_estimation


# 3. Analytical Mathematical Models


def regression_analysis(size: float, history: List[Tuple[float, float]]) -> Dict:
    """
    Linear regression using historical data: ** y = a * x + b **
    Returns the estimated effort corresponding to size
    :param size: scale of project
    :param history: historical data
    :return: res
    """
    X = np.array([x for x, y in history])
    Y = np.array([y for x, y in history])
    A = np.vstack([X, np.ones(len(X))]).T
    a, b = np.linalg.lstsq(A, Y, rcond=None)[0]
    effort = a * size + b
    res = {
        "effort": effort,
        "time": -1,
    }
    return res


@router.post("/mathematical/regression", response_model=EstimationPublic)
def regression_analysis_estimate(estimation: RegressionCreate, session: SessionDep) -> EstimationPublic:
    """
    Interface of regression analysis estimation
    """
    # calculate
    res = regression_analysis(estimation.size, estimation.historical_data)
    # database
    db_estimation = common_db_post(res, estimation, session)
    return db_estimation
