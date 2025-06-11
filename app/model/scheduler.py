from pydantic import BaseModel, Field
from typing import List

class Activity(BaseModel):
    name: str = Field(..., description="活动名称")
    duration: int = Field(..., gt=0, description="持续时间（天）")
    resource: int = Field(..., gt=0, description="资源需求人数")
    predecessors: List[str] = Field(default_factory=list, description="前置活动列表")


class ProjectData(BaseModel):
    activities: List[Activity] = Field(..., description="活动列表")
    resource_limit: int = Field(..., gt=0, description="资源总量限制")
