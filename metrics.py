from __future__ import annotations

import statistics
from typing import Dict, List
from colorama import Fore
from tabulate import tabulate
from robot_model import Robot
from task_generator import Task

def evaluate(tasks: List[Task], robots: List[Robot]) -> Dict[str, float]:

    # ── 1. Capability match rate ──────────────────────────────────────────────
    robot_map = {r.robot_id: r for r in robots}

    total = len(tasks)
    correct_cap = 0
    for t in tasks:
        if t.assigned_robot_id and t.assigned_robot_id != "UNASSIGNED":
            robot = robot_map.get(t.assigned_robot_id)
            if robot and robot.can_handle(t):
                correct_cap += 1

    capability_match_rate = correct_cap / total if total > 0 else 0.0

    # ── 2. Priority order score ───────────────────────────────────────────────
    pairs_total = 0
    pairs_correct = 0
    for robot in robots:
        tasks_sorted_assigned = sorted(
            robot.completed_tasks, key=lambda t: t.priority_value
        )
        # Compare the actual completion order vs the ideal priority order
        actual_order = [t.task_id for t in robot.completed_tasks]
        ideal_order  = [t.task_id for t in tasks_sorted_assigned]

        for i in range(len(actual_order) - 1):
            pairs_total += 1
            if (
                ideal_order.index(actual_order[i])
                <= ideal_order.index(actual_order[i + 1])
            ):
                pairs_correct += 1

    priority_order_score = pairs_correct / pairs_total if pairs_total > 0 else 1.0

    # ── 3. Task distribution balance ─────────────────────────────────────────
    counts = [len(r.completed_tasks) for r in robots]
    if len(counts) > 1 and statistics.mean(counts) > 0:
        cv = statistics.stdev(counts) / statistics.mean(counts)
    else:
        cv = 0.0
    task_distribution_balance = 1.0 / (1.0 + cv)

    # ── 4. Completion rate ────────────────────────────────────────────────────
    completed = sum(1 for t in tasks if t.completed)
    completion_rate = completed / total if total > 0 else 0.0

    # ── 5. Unassigned task count ────────────────────────────────────────────────
    unassigned_count = sum(
        1 for t in tasks if t.assigned_robot_id in ("", "UNASSIGNED")
    )

    metrics = {
        "capability_match_rate":      round(capability_match_rate,      4),
        "priority_order_score":       round(priority_order_score,       4),
        "task_distribution_balance":  round(task_distribution_balance,  4),
        "completion_rate":            round(completion_rate,            4),
        "unassigned_count":           unassigned_count,
    }
    return metrics


def display_metrics(metrics: Dict[str, float], robots: List[Robot]) -> None:

    print(Fore.MAGENTA + "\n" + "=" * 60)
    print(Fore.MAGENTA + "  EVALUATION METRICS")
    print(Fore.MAGENTA + "=" * 60)

    rows = [
        ["Capability Match Rate",        f"{metrics['capability_match_rate'] * 100:.1f}%"],
        ["Priority Order Score",         f"{metrics['priority_order_score'] * 100:.1f}%"],
        ["Task Distribution Balance",    f"{metrics['task_distribution_balance'] * 100:.1f}%"],
        ["Completion Rate",              f"{metrics['completion_rate'] * 100:.1f}%"],
        ["Unassigned Tasks",             f"{metrics['unassigned_count']}"],
    ]
    print(tabulate(rows, headers=["Metric", "Score"], tablefmt="rounded_outline"))

    # Per-robot summary
    print(Fore.MAGENTA + "\n  PER-ROBOT SUMMARY")
    robot_rows = [
        [r.robot_id, r.name, len(r.assigned_tasks), len(r.completed_tasks)]
        for r in robots
    ]
    print(tabulate(
        robot_rows,
        headers=["ID", "Robot", "Assigned", "Completed"],
        tablefmt="rounded_outline",
    ))


