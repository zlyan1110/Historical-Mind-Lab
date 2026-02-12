# 🗺️ Historical Mind-Lab: Engineering Roadmap

**核心目标：** 构建一个基于 Multi-Agent 的时空心智实验室，首个剧本为“颜之推在侯景之乱中的生存抉择”。
**当前阶段：** Phase 1 (MVP)

---

## Phase 1: The "Walking Skeleton" (单机核心逻辑)
**目标：** 不涉及 Web、数据库或前端。纯 Python 脚本，跑通“环境刺激 -> Agent 思考 -> 决策 -> 状态更新”的闭环。

### Milestone 1.1: Domain Modeling (数据结构定义)
* [x] **任务：** 定义核心 Pydantic 模型。
* **具体文件：** `src/domain/schemas.py`
* **具体代码要求：**
    * `GeoPoint`: `lat: float`, `lon: float`, `place_name: str`
    * `PsychState`: `stress: int (0-100)`, `focus: str (e.g., "Survival")`, `mbti: str ("ISTP")`
    * `AgentProfile`: `name: str`, `birth_year: int`, `traits: List[str]`
    * `SimulationFrame`: `timestamp: datetime`, `agent_state: AgentProfile`, `action: str`, `thought_process: str`

### Milestone 1.2: The "Brain" (Prompt Engineering)
* [x] **任务：** 编写系统提示词模板，能够根据当前状态生成下一步行动。
* **具体文件：** `src/agents/prompts.py`
* **具体代码要求：**
    * 创建一个 Jinja2 模板 `ISTP_DECISION_PROMPT`。
    * **输入变量：** `{current_location}`, `{external_threats}`, `{inventory}`, `{stress_level}`.
    * **输出约束：** 必须返回严格的 JSON 格式，包含 `reasoning` (思考链) 和 `next_action` (移动/等待/交互)。

### Milestone 1.3: The Simulation Loop (核心循环)
* [x] **任务：** 编写主循环脚本。
* **具体文件：** `src/main_cli.py`
* **具体逻辑：**
    1.  初始化颜之推 (Yan Zhitui) 在建康 (Jiankang)。
    2.  `while not is_safe:`
    3.  注入事件 (Mock): "公元 548 年 12 月，台城失守，火光冲天。"
    4.  调用 LLM (PydanticAI Agent) 获取决策。
    5.  更新 Agent 坐标和心理状态。
    6.  打印：`[Time] [Location] [Stress: 85] Thought: ...`

---

## Phase 2: The "Eyes & Ears" (数据与工具接入)
**目标：** 让 Agent 不再瞎编，而是基于史实和地理数据。

### Milestone 2.1: Tool - Historical Search (RAG Lite)
* [x] **任务：** 让 Agent 能查阅简单的本地知识库。
* **具体文件：** `src/tools/archive.py`
* **具体代码要求：**
    * 实现 `search_historical_context(year, location)`。
    * (MVP阶段) 先用一个 JSON 文件 `data/history_facts.json` 模拟数据库，存入关键事件（如侯景之乱的时间线）。

### Milestone 2.2: Tool - Geocoding (空间感知)
* [x] **任务：** 计算移动距离和方向。
* **具体文件：** `src/tools/gis.py`
* **具体代码要求：**
    * 实现 `calculate_distance(point_a, point_b)`。
    * 实现 `get_coordinates(ancient_name)` (MVP阶段返回硬编码坐标，后续接 Mapbox API)。

---

## Phase 3: The "Nervous System" (服务化与流式传输)
**目标：** 将 CLI 脚本改造为 Web 服务。

### Milestone 3.1: FastAPI Wrapper
* [x] **任务：** 暴露 HTTP 接口。
* **具体文件：** `src/api/server.py`
* **具体接口：**
    * `POST /simulations`: 创建新模拟。
    * `GET /simulations/{id}/state`: 获取当前状态。

### Milestone 3.2: WebSocket Streaming
* [x] **任务：** 实时推送 Agent 的思考过程。
* **具体文件：** `src/api/websocket.py`
* **具体逻辑：**
    * 将 `src/main_cli.py` 的打印语句替换为 `await websocket.send_json(frame)`。

---

## Phase 4: The "Face" (可视化前端)
**目标：** 在浏览器中看到地图和点。

### Milestone 4.1: Map Scaffolding
* [ ] **任务：** 初始化 Next.js + Mapbox。
* **具体文件：** `frontend/components/Map.tsx`
* **具体效果：** 加载一张底图，中心定位在南京。

### Milestone 4.2: Real-time Rendering
* [ ] **任务：** 连接 WebSocket 并渲染。
* **具体逻辑：**
    * 前端收到 JSON -> 更新 React State -> Mapbox Marker 移动。