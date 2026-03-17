from __future__ import annotations

import json
from typing import Dict
from colorama import Fore
from agents.base import BaseAssignmentAgent
from agents.llm.client import call_llm
from environment import DisasterEnvironment

_SYSTEM_PROMPT = """\
You are the Assignment Agent in a disaster-response multi-agent system.
You receive:
  - A rescue plan produced by the Planner Agent.
  - A list of tasks (with IDs, types, priorities, and required capabilities).
  - A list of available robots (with IDs, names, and capabilities).

Your job is to assign each task to exactly one robot whose capability
matches the task's required capability.  Higher-priority tasks must be
handled first (i.e. appear earlier in each robot's queue).

Return ONLY a valid JSON object with this exact structure:
{
  "assignments": [
    {"task_id": "T01", "robot_id": "R1"},
    ...
  ]
}

Rules:
- Every task must appear exactly once in "assignments".
- A robot can only be assigned tasks that match its capability.
- Order tasks within each robot's assignments by priority (high first).
"""

_RETRY_SYSTEM_PROMPT = """\
You are the Assignment Agent. Your previous response was invalid.
You MUST return ONLY a valid JSON object. No explanation, no markdown.

CRITICAL: Return exactly this structure:
{"assignments": [{"task_id": "T01", "robot_id": "R1"}, ...]}

Match each task to a robot with the SAME capability.
Every task MUST be assigned. Do not skip any task.
"""


class LLMAssignmentAgent(BaseAssignmentAgent):

    def _parse_assignments(self, raw: str, env: DisasterEnvironment) -> Dict[str, str]:

        data = json.loads(raw)
        assignment: Dict[str, str] = {}
        for entry in data.get("assignments", []):
            assignment[entry["task_id"]] = entry["robot_id"]

        missing = [t.task_id for t in env.tasks if t.task_id not in assignment]
        if missing:
            raise ValueError(f"LLM missed tasks: {missing}")

        return assignment

    def run(self, env: DisasterEnvironment, plan_str: str) -> Dict[str, str]:
        print(Fore.YELLOW + "\n[Assignment Agent - LLM] Assigning tasks to robots...")

        user_prompt = (
            f"=== RESCUE PLAN ===\n{plan_str}\n\n"
            f"=== TASKS ===\n{env.tasks_as_text()}\n\n"
            f"=== ROBOTS ===\n{env.robots_as_text()}\n\n"
            "Please assign each task to the appropriate robot and return the JSON."
        )

        raw = call_llm(_SYSTEM_PROMPT, user_prompt, json_mode=True)

        try:
            assignment = self._parse_assignments(raw, env)
        except Exception as first_exc:
            print(Fore.YELLOW + f"[Assignment Agent - LLM] First attempt failed ({first_exc}). Retrying...")

            retry_prompt = (
                f"=== TASKS ===\n{env.tasks_as_text()}\n\n"
                f"=== ROBOTS ===\n{env.robots_as_text()}\n\n"
                "Assign EVERY task to a robot with matching capability. Return ONLY JSON."
            )

            raw_retry = call_llm(_RETRY_SYSTEM_PROMPT, retry_prompt, json_mode=True)

            try:
                assignment = self._parse_assignments(raw_retry, env)
            except Exception as retry_exc:
                raise RuntimeError(
                    f"LLM failed to produce valid assignments after retry. "
                    f"First error: {first_exc}. Retry error: {retry_exc}"
                ) from retry_exc

        print(Fore.YELLOW + "[Assignment Agent - LLM] Assignments produced.")
        return assignment
