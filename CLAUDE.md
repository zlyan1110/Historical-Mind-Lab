# Historical Mind-Lab: Engineering Context

## Project Overview
Historical Mind-Lab is a Multi-Agent simulation platform that reconstructs historical decision-making processes using Cognitive Science (ISTP/Ti-Se) and 4D Spatio-Temporal tracking.
**Core Mission:** Simulate "Yan Zhitui" (and other historical figures) during the Hou Jing Rebellion (548 AD), prioritizing survival logic over historical determinism.

## Tech Stack & Architecture
- **Language:** Python 3.12+ (managed by `uv`)
- **Core Framework:** PydanticAI + LangGraph (Stateful Agents)
- **Data Model:** Pydantic (Strict Typing)
- **Streaming:** Kafka (Redpanda) + WebSocket (FastAPI)
- **Storage:**
  - Relational: PostgreSQL (Simulation State)
  - Graph: Neo4j (Social Connections/Genealogy)
  - Vector: ChromaDB (Historical Context/RAG)
- **Frontend:** Next.js + Mapbox GL JS

## Build & Run Commands
- **Dependency Mgmt:** `uv add <package>`, `uv sync`
- **Run Simulation (CLI):** `python src/main_cli.py`
- **Run API Server:** `uv run uvicorn src.api.server:app --reload`
- **Run Tests:** `pytest tests/`
- **Lint/Format:** `ruff check .`, `ruff format .`

## Coding Standards (Strict Enforcement)
1.  **Type Hints:** ALL function signatures must have type hints. Use `typing.List`, `typing.Optional`, and Pydantic models for complex structures.
2.  **Async/Await:** All I/O operations (Database, LLM calls) must be asynchronous. Use `asyncio`.
3.  **Error Handling:** Fail fast on logic errors, but log warnings on missing historical data (don't crash the sim if a minor coordinate is missing).
4.  **Docstrings:** Use Google-style docstrings for complex logic. Keep it concise for simple CRUD.
5.  **Path Handling:** Always use `pathlib.Path`, never string concatenation for file paths.

## Domain Rules (The "Soul")
1.  **Agent Psychology (ISTP):**
    - When simulating `Yan Zhitui`, strictly adhere to **ISTP (The Virtuoso)** traits:
    - **Ti (Introverted Thinking):** Logical, detached analysis of systems.
    - **Se (Extroverted Sensing):** Hyper-aware of immediate physical surroundings (terrain, weapons, weather).
    - **Stress Response:** Under high stress (>80), output becomes fragmented, tactical, and purely survival-focused. Ignore social niceties.
2.  **Historical Geography:**
    - Unless specified, assume the year is **548 AD**.
    - Use ancient names (e.g., "Jiankang" not "Nanjing") in internal logic, but map to modern coordinates for GIS tools.

## Development Workflow
1.  **Step-by-Step:** Do not generate massive code blocks at once. Implement one module, verify it runs, then move to the next.
2.  **Context Check:** Before starting a task, read `ROADMAP.md` to see where we are.
3.  **Update Roadmap:** After completing a milestone, mark it as `[x]` in `ROADMAP.md`.