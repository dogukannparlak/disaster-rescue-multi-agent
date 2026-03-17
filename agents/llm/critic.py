from __future__ import annotations

import json
from typing import Dict, Tuple
from colorama import Fore
from agents.base import BaseCriticAgent
from agents.llm.client import call_llm
from environment import DisasterEnvironment

_SYSTEM_PROMPT = """\
You are the Critic Agent in a disaster-response multi-agent system.
You receive:
  - The current task-to-robot assignment (JSON).
  - The full task list with priorities and required capabilities.
  - The full robot list with capabilities.

Your job is to:
1. Detect any incorrect capability matches (robot capability ≠ task requirement).
2. Detect priority violations (a lower-priority task assigned before a higher-priority one
   to the same robot).
3. Detect unassigned tasks (robot_id == "UNASSIGNED").
4. Fix every issue you find.

Return a JSON object with this exact structure:
{
  "critique": "Your plain-English critique here. List every issue found, or say 'No issues found.'",
  "corrected_assignments": [
    {"task_id": "T01", "robot_id": "R1"},
    ...
  ]
}

Rules for corrections:
- Every task must appear exactly once.
- A robot can only handle tasks that match its capability.
- Within each robot's queue, higher-priority tasks come first.
"""


class LLMCriticAgent(BaseCriticAgent):

    def run(
        self,
        env: DisasterEnvironment,
        assignment: Dict[str, str],
    ) -> Tuple[str, Dict[str, str]]:
        print(Fore.GREEN + "\n[Critic Agent - LLM] Evaluating assignment plan...")

        assignment_lines = [f"  {tid} → {rid}" for tid, rid in assignment.items()]
        assignment_text  = "Current assignments:\n" + "\n".join(assignment_lines)

        user_prompt = (
            f"=== CURRENT ASSIGNMENTS ===\n{assignment_text}\n\n"
            f"=== TASKS ===\n{env.tasks_as_text()}\n\n"
            f"=== ROBOTS ===\n{env.robots_as_text()}\n\n"
            "Please critique and, if needed, correct the assignments."
        )

        raw = call_llm(_SYSTEM_PROMPT, user_prompt, json_mode=True)

        critique_text = ""
        corrected: Dict[str, str] = dict(assignment)

        try:
            data = json.loads(raw)
            critique_text = data.get("critique", "")
            entries = data.get("corrected_assignments", [])
            if entries:
                corrected = {e["task_id"]: e["robot_id"] for e in entries}
        except Exception as exc:
            print(Fore.RED + f"[Critic Agent - LLM] Parse error ({exc}). "
                             "Keeping original assignments.")
            critique_text = "Critic Agent failed to parse LLM response; original assignments retained."

        print(Fore.GREEN + "[Critic Agent - LLM] Critique complete.\n")
        print("-" * 60)
        print(f"CRITIQUE:\n{critique_text}")
        print("-" * 60)

        return critique_text, corrected
