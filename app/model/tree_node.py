from pydantic import BaseModel, Field, validator
from typing import Optional, List

class TreeNodeInput(BaseModel):
    """
    TreeNodeInput 定义了用于接收决策树结构的基本输入格式。

    属性说明：
    - name: 节点名称（必填）
    - value: 节点的最终收益值（叶子节点专用，可为负数）
    - probability: 当前节点相对于其父节点的发生概率（仅用于机会节点）
    - children: 子节点列表（嵌套 TreeNodeInput）

    规则：
    - 如果节点不是叶子节点（没有 value），则必须提供 children。
    - 概率值限制在 [0, 1] 区间内。
    """
    name: str
    value: Optional[float] = None
    probability: Optional[float] = Field(default=None, ge=0, le=1)
    children: Optional[List["TreeNodeInput"]] = None

    @validator("children", always=True)
    def check_children_not_empty(cls, v, values):
        """
        校验逻辑：
        若节点没有提供 value（不是叶子节点），则必须包含至少一个子节点。
        """
        if "value" not in values or values["value"] is None:
            if not v:
                raise ValueError("Non-terminal node must have children.")
        return v

    class Config:
        json_schema_extra = {
            "example": {
              "name": "Choose Project",
              "children": [
                {
                  "name": "Dev A",
                  "children": [
                    {"name": "A Success", "value": 100, "probability": 0.7},
                    {"name": "A Failure", "value": -20, "probability": 0.3}
                  ]
                },
                {
                  "name": "Dev B",
                  "children": [
                    {"name": "B Success", "value": 150, "probability": 0.5},
                    {"name": "B Failure", "value": -40, "probability": 0.5}
                  ]
                }
              ]
            }
        }

TreeNodeInput.model_rebuild()
