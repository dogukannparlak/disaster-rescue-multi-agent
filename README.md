# Disaster Rescue Multi-Agent System

> CSE419 Homework 01 — Student ID: 221805040 — Dogukan Parlak 

A multi-agent system for disaster rescue coordination, powered by **LLM-based agents** via Ollama.

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Install and configure Ollama
```bash
# 1. Install Ollama
# Official site: https://ollama.com 

# Windows (PowerShell)
irm https://ollama.com/install.ps1 | iex

# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull a Model
ollama pull qwen2.5-coder:7b

# 3. Verify Installation (optional)
ollama run qwen2.5-coder:7b
```



### 3. Configure your environment
```bash
copy .env.example .env
```

### 4. Run the simulation
```bash
python main.py
```

---
## All CLI Flags

```
--tasks        N            Generate N tasks (default: 10)
--seed         N            Random seed for reproducibility (default: 42)
--no-delay                  Skip simulated execution delays (faster demo)
--interactive, -i           Run in interactive mode with parameter menu
```

Example:
```bash
python main.py --tasks 12 --seed 7 --no-delay
```

---

## Interactive Mode

Run the simulation with a dynamic menu to change parameters on-the-fly:

```bash
python main.py --interactive
# or
python main.py -i
```

### Features

- **Live parameter adjustment** — change tasks, seed, grid size, delay, and output path without restarting
- **Random seed generator** — quickly test different scenarios with `[R]`
- **Auto-incrementing output** — `results/latest.json` always stays current; each run also saves a traceable file
- **Re-run simulation instantly** — experiment with different configurations

### Interactive Menu

```
============================================================
  DISASTER RESCUE SIMULATION — INTERACTIVE MODE
  Backend: OLLAMA (LLM-based)
============================================================

Current Settings
------------------------------------------------------------
  Tasks        : 10
  Seed         : 42
  Grid         : 20x20
  Delay        : Off
  JSON output  : (auto: results/t{tasks}_g{grid}_s{seed}_<id>.json)
------------------------------------------------------------
  [E] Edit settings (tasks/seed/grid/delay/output)
  [R] Random seed (quick)
  [S] Run simulation
  [Q] Quit
```

Press `E` to open the settings sub-menu where you can change any individual value (with min/max hints shown).

---

## Configuration

Copy `.env.example` to `.env`:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
```

---

## Project Structure

```
cse419_hw01_221805040/
│
├── agents/
│   ├── base.py                    # BasePlannerAgent, BaseAssignmentAgent, BaseCriticAgent
│   │
│   └── llm/                       # LLM-based implementations (Ollama)
│       ├── client.py              # Ollama HTTP client
│       ├── planner.py             # LLMPlannerAgent
│       ├── assignment.py          # LLMAssignmentAgent
│       └── critic.py              # LLMCriticAgent
│
├── report/
│   ├── index.html                 # Dashboard home page
│   ├── report.html                # Redirects to index.html (backwards compat)
│   ├── report.md                  # Written project report
│   ├── css/
│   │   └── styles.css             # Dashboard styles
│   ├── js/
│   │   └── app.js                 # Dashboard JavaScript
│   └── pages/
│       ├── tasks.html             # Detailed tasks view
│       ├── robots.html            # Detailed robots view
│       ├── metrics.html           # Detailed metrics view
│       ├── architecture.html      # System architecture docs
│       └── guide.html             # User guide
│
├── config.py                      # All constants & settings (reads .env)
├── environment.py                 # DisasterEnvironment class
├── task_generator.py              # Task dataclass + generate_tasks()
├── robot_model.py                 # Robot dataclass + build_robot_fleet()
├── robot_agents.py                # RobotAgent execution engine
├── metrics.py                     # Evaluation metrics
├── simulation.py                  # Full pipeline orchestration
├── results/                       # Output runs (auto-created)
│   ├── latest.json                # Dashboard data (latest run)
│   └── t*_g*_s*_*.json           # Individual traceable runs
├── main.py                        # CLI entry point
├── colab_notebook.ipynb           # Google Colab notebook
├── requirements.txt
├── .env.example
└── README.md
```

---

## Architecture
```
┌───────────────────────────────┐
│        BaseAgent ABCs         │  (agents/base.py)
│                               │
│  - BasePlannerAgent           │
│  - BaseAssignmentAgent        │
│  - BaseCriticAgent            │
└───────────────┬───────────────┘
                │
                │ implements
                ▼
        agents/llm/
┌───────────────────────────────┐
│      LLM-based Agents         │
│                               │
│  - LLMPlannerAgent            │
│  - LLMAssignmentAgent         │
│  - LLMCriticAgent             │
└───────────────┬───────────────┘
                │
                │ used by
                ▼
┌───────────────────────────────┐
│        simulation.py          │
└───────────────────────────────┘
```
### Pipeline

```
1. generate_tasks()       →  randomised tasks with priorities & locations
2. Planner Agent          →  prioritised rescue plan (text)
3. Assignment Agent       →  task_id → robot_id mapping
4. Critic Agent           →  validates / corrects assignments
5. RobotAgent.execute()   →  simulates task completion
6. metrics.evaluate()     →  capability match, priority order, balance, completion
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OLLAMA_URL` | No | Ollama server URL (default: `http://localhost:11434`) |
| `OLLAMA_MODEL` | No | Ollama model name (default: `qwen2.5-coder:7b`) |

---

## Visual Report (HTML Dashboard)

The simulation exports results to JSON and provides a **multi-page HTML dashboard** for visual inspection.

**1. Run the simulation** (JSON is generated automatically):
```bash
python main.py --no-delay
```

**2. Open the dashboard** in your browser:
```
report/index.html
```

### Dashboard Pages

| Page | Description |
|------|-------------|
| **Dashboard** (index.html) | Overview with all key data |
| **Tasks** | Detailed task list and catalogue info |
| **Robots** | Robot fleet details and statistics |
| **Metrics** | Performance scores with explanations |
| **Architecture** | System design and agent pipeline |
| **User Guide** | Setup instructions and troubleshooting |

### How it Works

```
python main.py  →  results/latest.json  →  Dashboard (HTML/JS)
      ↑                   ↑                        ↑
  Run simulation    Auto-generated           Reads JSON data
```

The dashboard is **semi-dynamic**: HTML/CSS/JS files are static, but data is loaded from `results/latest.json` at runtime. Run the simulation again and refresh the browser to see updated results.

To view a specific past run in the dashboard:
```
report/index.html?json=results/t10_g20_s42_20260317-143000_ab12cd.json
```
