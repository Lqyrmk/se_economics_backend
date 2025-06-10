from typing import Annotated, List, Tuple

import numpy as np
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

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
    estimations = session.exec(select(Estimation).offset(offset).limit(limit)).all()
    print(f"Estimations: {estimations}")
    return estimations


def common_db_post(res: float, estimation: EstimationBase, session: SessionDep) -> EstimationPublic:
    db_estimation = Estimation.model_validate(estimation)
    db_estimation.effort = res
    # write to database
    session.add(db_estimation)
    session.commit()
    session.refresh(db_estimation)
    return db_estimation

# 1. Empirical Estimation
def cocomo_model(kloc: float, complexity: str) -> float:
    params = {
        "low": (2.4, 1.05),
        "medium": (3.0, 1.12),
        "high": (3.6, 1.20)
    }
    a, b = params.get(complexity, params["medium"])
    effort = a * (kloc ** b)

    return effort  # 单位：人月


@router.post("/empirical/cocomo", response_model=EstimationPublic)
def cocomo_estimate(estimation: CocomoCreate, session: SessionDep) -> EstimationPublic:
    """
    COCOMO模型： Effort = a * (KLOC)^b
    参数a, b根据complexity调整
    """
    # calculate
    effort = cocomo_model(estimation.size, estimation.complexity)
    # database
    db_estimation = common_db_post(effort, estimation, session)
    return db_estimation

def function_points_model(fp: float, complexity: str) -> float:
    """
    功能点估算：
    Effort = FP * multiplier
    multiplier根据complexity调整
    """
    multipliers = {
        "low": 1.0,
        "medium": 1.2,
        "high": 1.5
    }
    multiplier = multipliers.get(complexity, 1.2)
    effort = fp * multiplier
    return effort  # 人月

@router.post("/empirical/function_points", response_model=EstimationPublic)
def function_points_estimate(estimation: FunctionPointsCreate, session: SessionDep) -> EstimationPublic:
    # calculate
    effort = function_points_model(estimation.size, estimation.complexity)
    # database
    db_estimation = common_db_post(effort, estimation, session)
    return db_estimation

# 2. Heuristic Estimation
def expert_judgment(size: float, experience: int) -> float:
    """
    假设专家基于规模和经验给出估计：
    规模越大，人月越多；经验越丰富，效率越高（人月减少）
    """
    base = size * 1.1
    adjustment = max(0.5, 3 - experience) * 0.3  # 经验越高调整越小
    effort = base * adjustment
    return effort

@router.post("/heuristic/expert", response_model=EstimationPublic)
def expert_judgment_estimate(estimation: ExpertCreate, session: SessionDep) -> EstimationPublic:

    # calculate
    effort = expert_judgment(estimation.size, estimation.experience)
    # database
    db_estimation = common_db_post(effort, estimation, session)
    return db_estimation


def delphi_method(size: float, rounds: int = 3) -> float:
    """
    Delphi法：多轮专家估计后取均值
    这里用随机模拟多次估计后取平均
    """
    import random
    estimates = []
    for _ in range(rounds):
        noise = random.uniform(-0.2, 0.2)  # +/-20%波动
        estimate = size * (1.0 + noise)
        estimates.append(estimate)
    return sum(estimates) / rounds


@router.post("/heuristic/delphi", response_model=EstimationPublic)
def delphi_method_estimate(estimation: DelphiCreate, session: SessionDep) -> EstimationPublic:
    # calculate
    effort = expert_judgment(estimation.size, estimation.experience)
    # database
    db_estimation = common_db_post(effort, estimation, session)
    return db_estimation


# 3. Analytical Mathematical Models


def regression_analysis(size: float, history: List[Tuple[float, float]]) -> float:
    """
    用历史数据做线性回归 y = a * x + b
    返回对应size的估计effort
    """
    X = np.array([x for x, y in history])
    Y = np.array([y for x, y in history])
    A = np.vstack([X, np.ones(len(X))]).T
    a, b = np.linalg.lstsq(A, Y, rcond=None)[0]
    effort = a * size + b
    return effort


@router.post("/mathematical/regression", response_model=EstimationPublic)
def regression_analysis_estimate(estimation: RegressionCreate, session: SessionDep) -> EstimationPublic:
    # calculate
    effort = regression_analysis(estimation.size, estimation.historical_data)
    # database
    db_estimation = common_db_post(effort, estimation, session)
    return db_estimation
