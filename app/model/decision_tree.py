from anytree import NodeMixin
from typing import Optional, List
from itertools import product
from copy import deepcopy
import numpy as np
from collections import Counter

class DecisionNode(NodeMixin):
    """
    决策树节点类，继承 anytree 的 NodeMixin 支持树结构

    属性:
        name (str): 节点名称
        value (float): 叶节点的收益/成本值
        probability (float): 当前节点相对于父节点的发生概率（仅机会节点使用）
    """
    def __init__(self, name: str, value: Optional[float] = None, probability: Optional[float] = None, parent=None):
        self.name = name
        self.value = value
        self.probability = probability
        self.parent = parent

    def expected_value(self):
        """
        递归计算当前节点的期望值（Expected Value）

        Returns:
            float: 当前节点及其子树的期望值
        """
        # 叶子节点
        if not self.children:
            return self.value

        # 概率节点（机会节点）
        elif all(c.probability is not None for c in self.children):
            return sum(c.expected_value() * c.probability for c in self.children)

        # 决策节点（没有概率，选最大）
        else:
            return max(c.expected_value() for c in self.children)

def build_tree(data: dict, parent=None) -> DecisionNode:
    """
    递归构建决策树结构

    Args:
        data (dict): 输入的嵌套字典结构，符合 TreeNodeInput 格式
        parent (DecisionNode): 父节点引用（递归用）

    Returns:
        DecisionNode: 构建完成的树根节点
    """
    node = DecisionNode(
        name=data["name"],
        value=data.get("value"),
        probability=data.get("probability"),
        parent=parent
    )

    children_data = data.get("children") or []
    for child_data in children_data:
        build_tree(child_data, parent=node)

    return node

def export_tree_with_ev(node):
    """
    导出当前决策树为嵌套 JSON，包括每个节点的期望值（ev）

    Args:
        node (DecisionNode): 决策树根节点

    Returns:
        dict: 可序列化的 JSON 树结构，包含每个节点的 ev、value、probability 等信息
    """
    result = {
        "name": node.name,
        "ev": node.expected_value()
    }
    if node.value is not None:
        result["value"] = node.value
    if node.probability is not None:
        result["probability"] = node.probability

    if node.children:
        result["children"] = [export_tree_with_ev(child) for child in node.children]

    return result

def find_node_by_path(node, path):
    """
    根据路径（列表）找到目标子节点，例如 ["Dev A", "A Success"]
    """
    current = node
    for name in path:
        current = next((child for child in current.children if child.name == name), None)
        if current is None:
            raise ValueError(f"Node path {' -> '.join(path)} not found.")
    return current


def sensitivity_analysis(tree_data, target_path, field, value_range):
    """
    对指定路径的字段做敏感性分析

    Args:
        tree_data (dict): 原始树结构
        target_path (List[str]): 节点路径（从根到目标）
        field (str): 被修改的字段，如 "probability" 或 "value"
        value_range (dict): 浮动范围，包括 start/end/step

    Returns:
        List[Dict]: 每个值对应的 EV
    """
    results = []
    start = value_range["start"]
    end = value_range["end"]
    step = value_range["step"]

    val = start
    while val <= end + 1e-8:  # 保证包含结束值
        tree_copy = build_tree(tree_data)  # 每次构建新树
        target_node = find_node_by_path(tree_copy, target_path)
        setattr(target_node, field, val)  # 设置字段

        ev = tree_copy.expected_value()
        results.append({"input_value": round(val, 3), "ev": round(ev, 3)})
        val += step

    return results
def format_for_chart(results: list):
    """
    格式化敏感性分析结果以兼容前端图表（ECharts/D3）

    Args:
        results (list): 原始敏感性分析结果 [{"input_value": x, "ev": y}, ...]

    Returns:
        dict: 格式化后的数据结构，包含 xAxis 和 series
    """
    xAxis = [str(point["input_value"]) for point in results]
    series = [point["ev"] for point in results]
    return {
        "xAxis": xAxis,
        "series": series,
        "raw_data": results
    }



def multi_sensitivity_analysis(tree_data, fields: list):
    """
    多字段敏感性分析：生成所有组合，修改节点值并计算 EV

    Args:
        tree_data (dict): 原始树结构
        fields (list): 每个字段含 path, field, range

    Returns:
        list: 每组组合对应的输入值 + EV
    """
    # 构建所有输入组合
    input_axes = []
    axis_labels = []

    for f in fields:
        r = f["range"]
        steps = [round(r["start"] + i * r["step"], 5)
                 for i in range(int((r["end"] - r["start"]) / r["step"]) + 1)]
        input_axes.append(steps)
        label = " → ".join(f["target_path"])
        axis_labels.append(label)

    results = []
    for values in product(*input_axes):
        tree_copy = build_tree(deepcopy(tree_data))  # 拷贝构建
        for f, val in zip(fields, values):
            node = find_node_by_path(tree_copy, f["target_path"])
            setattr(node, f["field"], val)

        results.append({
            "inputs": dict(zip(axis_labels, values)),
            "ev": round(tree_copy.expected_value(), 3)
        })

    return results
def monte_carlo_simulation(tree_data, target_path, field, distribution, params, runs=1000, bins=10):
    """
    执行蒙特卡洛模拟：对指定节点的某个字段值做随机采样，重复模拟期望值

    Returns:
        dict: 含统计摘要 + EV分布数组 + 直方图数据
    """
    ev_results = []

    for _ in range(runs):
        tree = build_tree(tree_data)
        node = find_node_by_path(tree, target_path)

        # 抽样设置字段
        if distribution == "normal":
            value = np.random.normal(params["mean"], params["stddev"])
        elif distribution == "uniform":
            value = np.random.uniform(params["low"], params["high"])
        else:
            raise ValueError("Unsupported distribution type")

        setattr(node, field, value)
        ev_results.append(tree.expected_value())

    mean = np.mean(ev_results)
    std = np.std(ev_results)
    min_val = np.min(ev_results)
    max_val = np.max(ev_results)

    # 直方图数据（用于前端绘图）
    counts, bin_edges = np.histogram(ev_results, bins=bins)
    histogram = [
        {
            "range": f"{round(bin_edges[i], 1)} - {round(bin_edges[i+1], 1)}",
            "count": int(counts[i])
        }
        for i in range(len(counts))
    ]

    return {
        "summary": {
            "mean": round(mean, 3),
            "stddev": round(std, 3),
            "min": round(min_val, 3),
            "max": round(max_val, 3)
        },
        "histogram": histogram,
        "raw_ev_samples": [round(x, 3) for x in ev_results]
    }