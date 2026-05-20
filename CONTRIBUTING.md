# Contributing

Thank you for your interest in contributing to **disaster-rescue-multi-agent**. This guide covers local setup, where to extend the system, and how to submit changes.

---

## Getting Started

### Prerequisites

- Python 3.10 or newer
- [Ollama](https://ollama.com) installed and running locally
- A pulled model (default: `qwen2.5-coder:7b`)

### Local setup

```bash
git clone <your-fork-url>
cd disaster-rescue-multi-agent

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux

ollama pull qwen2.5-coder:7b
python main.py --no-delay
```

After a successful run, open `report/index.html` in your browser to inspect `results/latest.json`.

---

## Extension Points

### Add a new task type

Edit `TASK_CATALOGUE` in [`config.py`](config.py):

```python
("evacuate zone", "high", "search and mapping"),
```

Each entry is `(task_type, priority, required_capability)`. Priorities must be `high`, `medium`, or `low`.

### Add a new robot

Edit `ROBOT_DEFINITIONS` in [`config.py`](config.py):

```python
("R4", "Water Rescue Robot", "water rescue", "medium"),
```

Add a matching `SPEED_DELAY` entry if you introduce a new speed label.

### Add a new agent implementation

1. Subclass the appropriate ABC in [`agents/base.py`](agents/base.py).
2. Implement `run()` with the same signature as the LLM agents.
3. Wire the new agent in [`simulation.py`](simulation.py) where `LLMPlannerAgent`, `LLMAssignmentAgent`, and `LLMCriticAgent` are instantiated.

Keep LLM-specific logic under `agents/llm/` so alternative backends (rule-based, API-based) can live in parallel packages.

### Add or adjust metrics

Extend `evaluate()` and `display_metrics()` in [`metrics.py`](metrics.py). Export any new fields in the JSON block inside [`simulation.py`](simulation.py) so the dashboard can consume them.

### Dashboard updates

- Static pages: `report/pages/`
- Data binding: `report/js/app.js`
- Styles: `report/css/styles.css`

Run the simulation first so `results/latest.json` exists before testing UI changes.

---

## Code Style

- Use `from __future__ import annotations` in new Python modules.
- Follow existing naming: `snake_case` for functions/variables, `PascalCase` for classes.
- Type-hint public function signatures.
- Keep agent prompts in the agent module that uses them.
- Prefer small, focused changes over large refactors unless discussed in an issue first.

---

## Pull Requests

1. Fork the repository and create a feature branch (`feat/short-description`).
2. Run the simulation locally and confirm it completes without errors.
3. If you change metrics or export JSON shape, update the dashboard or document the breaking change in the PR description.
4. Open a pull request with:
   - What changed and why
   - How you tested (CLI flags, seeds, models used)
   - Screenshots of the dashboard if UI was modified

---

## Reporting Issues

When opening an issue, include:

- OS and Python version
- Ollama model and `OLLAMA_URL`
- CLI command used
- Error message or unexpected metric output
- Relevant JSON snippet from `results/` (redact paths if needed)

---

## Questions

For design context and evaluation methodology, see [`report/report.md`](report/report.md) (Project Notes in the dashboard sidebar).
