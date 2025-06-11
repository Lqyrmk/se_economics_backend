import numpy as np

from typing import Dict
from fastapi import APIRouter

from app.model.scheduler import Activity, ProjectData

router = APIRouter(
    prefix="/resource",
    tags=["estimation"],
    responses={404: {"description": "Not found"}},
)


def calc_earliest_start_times(activities: Dict[str, Activity]) -> Dict[str, int]:
    ES = {}
    while len(ES) < len(activities):
        for act, info in activities.items():
            if act in ES:
                continue
            if all(pred in ES for pred in info.predecessors):
                ES[act] = max([ES[pred] + activities[pred].duration for pred in info.predecessors] or [1])
    return ES


def calc_latest_start_times(activities: Dict[str, Activity], ES: Dict[str, int]) -> Dict[str, int]:
    project_end = max(ES[act] + activities[act].duration - 1 for act in activities)
    LF = {}
    while len(LF) < len(activities):
        for act, info in activities.items():
            if act in LF:
                continue
            successors = [a for a, i in activities.items() if act in i.predecessors]
            if all(suc in LF for suc in successors):
                if successors:
                    LF[act] = min([LF[suc] - info.duration for suc in successors])
                else:
                    LF[act] = project_end - info.duration + 1
    return LF


@router.post("/leveling", summary="resource leveling algorithm", tags=["Resource Optimization"])
def resource_leveling_api(data: ProjectData):
    # 转换活动为字典
    activities = {a.name: a for a in data.activities}
    resource_limit = data.resource_limit

    ES = calc_earliest_start_times(activities)
    start_times = ES.copy()
    project_end = max(start_times[act] + activities[act].duration - 1 for act in activities)

    while True:
        daily_resources = {day: 0 for day in range(1, project_end + 10)}
        for act, info in activities.items():
            st = start_times[act]
            for d in range(st, st + info.duration):
                daily_resources[d] += info.resource

        overloaded_days = [d for d, r in daily_resources.items() if r > resource_limit]
        if not overloaded_days:
            break
        od = overloaded_days[0]

        candidates = []
        for act, info in activities.items():
            st = start_times[act]
            if st <= od < st + info.duration:
                candidates.append(act)
        candidates.sort(key=lambda x: len(activities[x].predecessors), reverse=True)
        to_delay = candidates[0]
        start_times[to_delay] += 1
        project_end = max(project_end, start_times[to_delay] + activities[to_delay].duration - 1)

    return {"start_times": start_times, "project_end": project_end}


@router.post("/smoothing", summary="resource smoothing algorithm", tags=["Resource Optimization"])
def resource_smoothing_api(data: ProjectData):
    activities = {a.name: a for a in data.activities}
    resource_limit = data.resource_limit

    ES = calc_earliest_start_times(activities)
    LF = calc_latest_start_times(activities, ES)
    start_times = ES.copy()
    project_end = max(ES[act] + activities[act].duration - 1 for act in activities)

    max_iter = 1000
    for _ in range(max_iter):
        daily_resources = {day: 0 for day in range(1, project_end + 1)}
        for act, info in activities.items():
            st = start_times[act]
            for d in range(st, st + info.duration):
                daily_resources[d] += info.resource

        variance_before = np.var(list(daily_resources.values()))
        improved = False

        for act, info in activities.items():
            current_start = start_times[act]
            for new_start in range(ES[act], LF[act] + 1):
                if new_start == current_start:
                    continue
                start_times[act] = new_start
                daily_resources_tmp = {day: 0 for day in range(1, project_end + 1)}
                for a, i in activities.items():
                    st = start_times[a]
                    for d in range(st, st + i.duration):
                        daily_resources_tmp[d] += i.resource
                if max(daily_resources_tmp.values()) > resource_limit:
                    continue
                variance_after = np.var(list(daily_resources_tmp.values()))
                if variance_after < variance_before:
                    variance_before = variance_after
                    improved = True
                    break
                else:
                    start_times[act] = current_start
            if improved:
                break
        if not improved:
            break

    return {"start_times": start_times, "project_end": project_end}
