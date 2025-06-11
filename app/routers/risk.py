from fastapi import FastAPI, HTTPException, Body, APIRouter
from typing import Optional, List
from app.model.decision_tree import build_tree, export_tree_with_ev, sensitivity_analysis, format_for_chart, multi_sensitivity_analysis, monte_carlo_simulation
from app.model.tree_node import TreeNodeInput


router = APIRouter(
    prefix="/decision-tree",
    tags=["decision-tree"],
    responses={404: {"description": "Not found"}},
)

@router.post("/sensitivity")
def run_sensitivity_analysis(
    payload: dict = Body(
            ...,
            example={
                "tree": {
                    "name": "Choose Project",
                    "children": [
                        {
                            "name": "Dev A",
                            "children": [
                                {"name": "A Success", "value": 100, "probability": 0.7},
                                {"name": "A Failure", "value": -20, "probability": 0.3}
                            ]
                        }
                    ]
                },
                "target_path": ["Dev A", "A Success"],
                "field": "probability",
                "range": {
                    "start": 0.6,
                    "end": 0.9,
                    "step": 0.05
                }
            }
        )
):
    """
    对某个节点执行敏感性分析，并返回图表友好的结构
    """
    try:
        result = sensitivity_analysis(
            tree_data=payload["tree"],
            target_path=payload["target_path"],
            field=payload["field"],
            value_range=payload["range"]
        )
        return {
            "chart_data": format_for_chart(result),  # 图表格式
            "sensitivity_result": result              # 原始结构
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
"""
front can use it like this(ECharts):
option = {
  title: { text: 'Sensitivity Analysis' },
  xAxis: { type: 'category', data: chart_data.xAxis },
  yAxis: { type: 'value', name: 'Expected Value' },
  series: [{
    type: 'line',
    data: chart_data.series
  }]
}
"""

@router.post("/sensitivity/multi")
def run_multi_sensitivity(
payload: dict = Body(
        ...,
        example={
            "tree": {
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
            },
            "fields": [
                {
                    "target_path": ["Dev A", "A Success"],
                    "field": "probability",
                    "range": { "start": 0.6, "end": 0.9, "step": 0.1 }
                },
                {
                    "target_path": ["Dev B", "B Success"],
                    "field": "probability",
                    "range": { "start": 0.4, "end": 0.7, "step": 0.1 }
                }
            ]
        }
    )
):
    """
    多字段敏感性分析接口，返回所有组合下的 EV 值
    """
    try:
        result = multi_sensitivity_analysis(
            tree_data=payload["tree"],
            fields=payload["fields"]
        )
        return {"grid_data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/evaluate")
def evaluate_decision_tree(input_tree: dict = Body(
        ...,
        example={
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
    )):
    """
    接收决策树结构数据，计算每个子路径的期望值，返回完整决策树及最优方案

    请求体: TreeNodeInput (嵌套的 Pydantic 模型)
    返回值:
        {
            "branch_expected_values": {子路径名: 期望值},
            "optimal_expected_value": 最大期望值,
            "tree_with_ev": 嵌套 JSON 树结构，含每个节点期望值
        }
    """
    try:
        root = build_tree(input_tree)
        results = {}
        for child in root.children:
            results[child.name] = child.expected_value()

        return {
            "branch_expected_values": results,
            "optimal_expected_value": root.expected_value(),
            "tree_with_ev": export_tree_with_ev(root)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.post("/monte-carlo")
def run_monte_carlo(
    payload: dict = Body(
        ...,
        example={
            "tree": {
                "name": "Choose Project",
                "children": [
                    {
                        "name": "Dev A",
                        "children": [
                            {"name": "A Success", "value": 100, "probability": 0.7},
                            {"name": "A Failure", "value": -20, "probability": 0.3}
                        ]
                    }
                ]
            },
            "target_path": ["Dev A", "A Success"],
            "field": "value",
            "distribution": "normal",
            "params": {
                "mean": 100,
                "stddev": 15
            },
            "runs": 1000,
            "bins": 10
        }
    )
):
    """
    蒙特卡洛模拟接口：模拟节点某字段的随机变化下，整体期望值分布
    """
    try:
        result = monte_carlo_simulation(
            tree_data=payload["tree"],
            target_path=payload["target_path"],
            field=payload["field"],
            distribution=payload["distribution"],
            params=payload["params"],
            runs=payload.get("runs", 1000),
            bins=payload.get("bins", 10)
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
