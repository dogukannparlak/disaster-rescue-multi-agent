from __future__ import annotations

import os
import json
import datetime as _dt
import secrets
from typing import Dict, List
from colorama import Fore
from agents.llm.planner import LLMPlannerAgent
from agents.llm.assignment import LLMAssignmentAgent
from agents.llm.critic import LLMCriticAgent
from config import GRID_SIZE, NUM_TASKS, RANDOM_SEED
from environment import DisasterEnvironment
from metrics import display_metrics, evaluate
from robot_agents import RobotAgent, run_all_robots
from robot_model import Robot, build_robot_fleet
from task_generator import Task, generate_tasks

# ── Helper: apply an assignment dict to tasks + robots ────────────────────────

def _apply_assignments(
    tasks: List[Task],
    robots: List[Robot],
    assignment: Dict[str, str],
) -> List[RobotAgent]:

    task_map = {t.task_id: t for t in tasks}
    robot_map = {r.robot_id: r for r in robots}

    # Reset previous assignments
    for r in robots:
        r.assigned_tasks = []
        r.completed_tasks = []

    for task_id, robot_id in assignment.items():
        task = task_map.get(task_id)
        robot = robot_map.get(robot_id)
        if task and robot:
            task.assigned_robot_id = robot_id
            robot.assigned_tasks.append(task)
        elif task:
            task.assigned_robot_id = "UNASSIGNED"

    # Wrap each robot in a RobotAgent and sort its tasks by priority
    agents = []
    for robot in robots:
        agent = RobotAgent(robot)
        agent.load_tasks(robot.assigned_tasks)
        agents.append(agent)

    return agents

# ── Main simulation entry-point ───────────────────────────────────────────────

def run_simulation(
    num_tasks: int = NUM_TASKS,
    grid_size: int = GRID_SIZE,
    seed: int | None = RANDOM_SEED,
    simulate_delay: bool = True,
    export_path: str | None = None,
) -> Dict:

    # ── Step 1: Build environment ─────────────────────────────────────────────
    print(Fore.WHITE + "\n" + "=" * 60)
    print(Fore.WHITE + "  DISASTER RESCUE MULTI-AGENT SYSTEM")
    print(Fore.WHITE + "  Mode: LLM  |  Backend: OLLAMA")
    print(Fore.WHITE + "=" * 60)

    tasks  = generate_tasks(num_tasks, seed=seed, grid_size=grid_size)
    robots = build_robot_fleet()
    env    = DisasterEnvironment(grid_size, tasks, robots)

    env.display_tasks()
    env.display_robots()

    # ── Instantiate LLM agents ────────────────────────────────────────────────
    planner  = LLMPlannerAgent()
    assigner = LLMAssignmentAgent()
    critic   = LLMCriticAgent()

    # ── Step 2: Planner Agent ─────────────────────────────────────────────────
    plan_str = planner.run(env)

    # ── Step 3: Assignment Agent ──────────────────────────────────────────────
    assignment = assigner.run(env, plan_str)

    # Apply provisional assignments for display
    _apply_assignments(tasks, robots, assignment)
    env.display_assignments()

    # ── Step 4: Critic Agent ──────────────────────────────────────────────────
    critique_text, corrected_assignment = critic.run(env, assignment)

    # ── Step 5: Apply corrected assignments ───────────────────────────────────
    if corrected_assignment != assignment:
        print(Fore.GREEN + "\n[Critic Agent] Corrected assignments applied.")
        assignment = corrected_assignment
        _apply_assignments(tasks, robots, assignment)
        env.display_assignments()
    else:
        # Re-apply to refresh robot queues after critic phase
        _apply_assignments(tasks, robots, assignment)

    # ── Step 6: Robot execution ───────────────────────────────────────────────
    robot_agents = [RobotAgent(r) for r in robots]
    for agent in robot_agents:
        agent.load_tasks(agent.robot.assigned_tasks)
    run_all_robots(robot_agents, simulate_delay=simulate_delay)

    # ── Step 7: Evaluation metrics ────────────────────────────────────────────
    metrics = evaluate(tasks, robots)
    display_metrics(metrics, robots)

    # ── Step 8: Export JSON for HTML dashboard ────────────────────────────────
    result = {
        "config": {
            "num_tasks": num_tasks,
            "grid_size": grid_size,
            "seed": seed,
        },
        "tasks":                tasks,
        "robots":               robots,
        "plan":                 plan_str,
        "assignment":           assignment,
        "critique":             critique_text,
        "corrected_assignment": corrected_assignment,
        "metrics":              metrics,
    }
    written_paths = _export_simulation_result(result, path=export_path)
    result["export_paths"] = written_paths

    return result

def _export_simulation_result(
    result: Dict,
    path: str | None = None,
) -> Dict[str, str]:

    payload = {
        "mode":    "LLM",
        "backend": "OLLAMA",
        "config":  result.get("config", {}),
        "tasks": [
            {
                "id": t.task_id,
                "type": t.task_type,
                "priority": t.priority,
                "capability": t.required_capability,
                "x": t.x,
                "y": t.y,
            }
            for t in result["tasks"]
        ],
        "robots": [
            {
                "id": r.robot_id,
                "name": r.name,
                "capability": r.capability,
                "speed": r.speed,
            }
            for r in result["robots"]
        ],
        "assignments": [
            {"task_id": tid, "robot_id": rid}
            for tid, rid in result["corrected_assignment"].items()
        ],
        "metrics": result["metrics"],
    }
    cfg = result.get("config", {}) or {}
    num_tasks = cfg.get("num_tasks")
    grid_size = cfg.get("grid_size")
    seed = cfg.get("seed")

    # Default: create a traceable filename under results/
    if not path:
        seed_part = "none" if seed is None else str(seed)
        ts = _dt.datetime.now().strftime("%Y%m%d-%H%M")
        uniq = secrets.token_hex(3)  # 6 hex chars
        path = os.path.join(
            "results",
            f"t{num_tasks}_g{grid_size}_s{seed_part}_{ts}_{uniq}.json",
        )

    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    # Dashboard default: always keep results/latest.json in sync.
    latest_path = os.path.join("results", "latest.json")
    os.makedirs(os.path.dirname(latest_path), exist_ok=True)
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return {"export_path": path, "latest_json": latest_path}
