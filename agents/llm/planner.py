from __future__ import annotations

from colorama import Fore
from agents.base import BasePlannerAgent
from agents.llm.client import call_llm
from environment import DisasterEnvironment

_SYSTEM_PROMPT = """\
You are the Planner Agent in a disaster-response multi-agent system.
Your job is to:
1. Analyse the list of tasks in the disaster environment.
2. Identify which tasks are most urgent (high > medium > low priority).
3. Produce a clear, numbered rescue plan that orders tasks by urgency.
4. For each task, briefly justify why it has been placed in that position.
Keep the plan concise — one paragraph per task is enough.
"""

class LLMPlannerAgent(BasePlannerAgent):

    def run(self, env: DisasterEnvironment) -> str:
        print(Fore.CYAN + "\n[Planner Agent - LLM] Analysing environment and generating rescue plan...")

        user_prompt = (
            f"Grid size: {env.grid_size}x{env.grid_size}\n\n"
            f"{env.tasks_as_text()}\n\n"
            f"{env.robots_as_text()}\n\n"
            "Please produce the prioritised rescue plan."
        )

        plan_str = call_llm(_SYSTEM_PROMPT, user_prompt, json_mode=False)

        print(Fore.CYAN + "[Planner Agent - LLM] Plan generated.\n")
        print("-" * 60)
        print(plan_str)
        print("-" * 60)

        return plan_str