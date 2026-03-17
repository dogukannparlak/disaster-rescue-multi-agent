import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL: str   = os.getenv("OLLAMA_URL",   "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

# ── Simulation settings ───────────────────────────────────────────────────────
GRID_SIZE: int = 20          # NxN disaster grid
NUM_TASKS: int = 10          # number of tasks to generate
RANDOM_SEED: int = 42        # reproducibility seed (None = fully random)

# ── Priority levels (lower number = higher urgency) ───────────────────────────
PRIORITY_ORDER = {"high": 1, "medium": 2, "low": 3}

# ── Task catalogue  ──────────────────────────────────────────────────────────
#   Each entry: (task_type, priority, required_capability)
TASK_CATALOGUE = [
    ("rescue victim",    "high",   "medical support"),
    ("rescue victim",    "high",   "search and mapping"),
    ("clear debris",     "medium", "heavy debris removal"),
    ("map building",     "low",    "search and mapping"),
    ("deliver medicine", "medium", "medical support"),
]

# ── Robot definitions ─────────────────────────────────────────────────────────
#   Each entry: (robot_id, name, capability, speed)
ROBOT_DEFINITIONS = [
    ("R1", "Search and Mapping Robot",   "search and mapping",   "fast"),
    ("R2", "Medical Support Robot",      "medical support",      "medium"),
    ("R3", "Heavy Debris Removal Robot", "heavy debris removal", "slow"),
]

# ── Speed → simulated seconds per task ───────────────────────────────────────
SPEED_DELAY = {"fast": 1, "medium": 2, "slow": 3}

