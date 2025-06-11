from typing import Annotated, Optional, Dict, Literal, List, Tuple
from sqlmodel import Field, SQLModel


class EstimationBase(SQLModel):
    method: str = Field(index=True)
    size: float = Field(default=50, ge=0)


class Estimation(EstimationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    complexity: Optional[str] = Field(default="semi")  # organic/semi/embedded
    experience: Optional[float] = Field(default=3, ge=0)
    effort: Optional[float] = Field(default=None)
    time: Optional[float] = Field(default=None)


class CocomoCreate(EstimationBase):
    method: Optional[str] = Field(default="cocomo")
    complexity: Optional[str] = Field(default="semi")  # organic/semi/embedded


class FunctionPointsCreate(EstimationBase):
    method: Optional[str] = Field(default="function_points")
    complexity: Optional[str] = Field(default="semi")  # organic/semi/embedded


class ExpertCreate(EstimationBase):
    method: Optional[str] = Field(default="expert")
    experience: Optional[float] = Field(default=3, ge=0)


class DelphiCreate(EstimationBase):
    method: Optional[str] = Field(default="delphi")
    experience: Optional[float] = Field(default=3, ge=0)
    experience_list: List[float]


class RegressionCreate(EstimationBase):
    method: Optional[str] = Field(default="regression")
    historical_data: list[tuple[float, float]]  # 传入回归模型数据

class EstimationPublic(EstimationBase):
    id: int
    method: str
    effort: float
    time: float
