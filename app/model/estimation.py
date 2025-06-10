from typing import Annotated, Optional, Dict, Literal, List, Tuple
from sqlmodel import Field, SQLModel


class EstimationBase(SQLModel):
    method: str = Field(index=True)
    size: float = Field(default=0, ge=0)
    complexity: Optional[str] = Field(default="medium")  # low/medium/high
    experience: Optional[int] = Field(default=3, ge=0)


class Estimation(EstimationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    effort: Optional[float] = Field(default=None)

class CocomoCreate(EstimationBase):
    method: Literal["cocomo"] = "cocomo"


class FunctionPointsCreate(EstimationBase):
    method: Literal["function_points"] = "function_points"


class ExpertCreate(EstimationBase):
    method: Literal["expert"] = "expert"


class DelphiCreate(EstimationBase):
    method: Literal["delphi"] = "delphi"


class RegressionCreate(EstimationBase):
    method: Literal["regression"] = "regression"
    historical_data: list[tuple[float, float]]  # 传入回归模型数据

class EstimationPublic(EstimationBase):
    id: int
    method: str
    effort: float
