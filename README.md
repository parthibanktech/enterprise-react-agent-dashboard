# 🧠 Enterprise ReAct Agent Dashboard

A production-ready, highly modular, consolidated AI Agent Dashboard built with **LangChain ReAct Agent**, **ChatDeepSeek**, and **Gradio Blocks**. This application consolidates multiple utility tools (calculations, database queries, and geocoded weather lookups) under a single, highly resilient, self-correcting agent interface with a real-time visual reasoning trace terminal.

---

## 🚀 Key Features

* **Resilient ReAct Reasoning Loop**: Built on Parthiban's unified `create_agent` framework that catches tool exceptions (like division by zero or SQLite column spelling errors), self-corrects at runtime, and completes tasks without crashing.
* **Unified Capstone Tool Suite**: Exposes 7 operational tools to the agent:
  * **Math & Estimators**: Safe `divide`, safe generic algebraic `calculate`, tax `calculate_gst`, discount `calculate_discount`, and bulk invoice calculator `calculate_product_pricing`.
  * **API Travel Warnings**: City search geocoding (`geocode_location`), forecast parser (`get_weather_forecast`), and web search (`google_search`).
  * **Secure Databases**: SQL-injection hardened, read-only SELECT querying (`query_products_database`).
* **Sleek UI Dashboard**: Built with Gradio Blocks and glassmorphism styling, showing the user conversational chat side-by-side with a real-time **Reasoning Trace Terminal** displaying the agent's internal thought cycles.
* **Enterprise CI/CD & Infrastructure**: Docker containerization, GitHub Actions tests pipeline, and IaC deployment configurations for Render Cloud.

---

## 📂 Project Structure

```text
enterprise-react-agent-dashboard/
├── .github/
│   └── workflows/
│       └── deploy.yml              # GitHub Actions CI/CD Pipeline
├── app/
│   ├── core/
│   │   ├── agent.py                # ReAct graph & agent engine
│   │   ├── config.py               # Settings, validation, relative paths
│   │   └── tracer.py               # Trace parser for Gradio markdown
│   ├── tools/
│   │   ├── api_tools.py            # Search & Weather API tools
│   │   ├── db_tools.py             # Read-hardened SQLite DB tool
│   │   └── math_tools.py           # Calculations & pricing invoice tools
│   └── ui/
│       └── dashboard.py            # Gradio Blocks UI layout & styling
├── data/
│   ├── seed.py                     # Initial database seeding script
│   └── products.sqlite             # Local SQLite database
├── lessons/                        # Archived study scripts & lessons
├── tests/                          # Pytest suite
├── Dockerfile                      # Production packaging script
├── pyproject.toml                  # Dependencies & project settings
└── render.yaml                     # Infrastructure-as-Code for Render
```

---

## ⚙️ Quick Start

### 1. Prerequisites
Ensure you have the Astral `uv` package manager installed (or use `pip`):
```bash
# If using uv
uv sync
```

### 2. Environment Setup
Create a `.env` file in the root folder and add your API keys:
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```
*Note: If no API keys are present, the dashboard automatically starts in **Interactive Simulator Mode** allowing keyless scenario tests.*

### 3. Run Seeding & UI locally
Seed the products database:
```bash
uv run python data/seed.py
```

Launch the consolidated Gradio web app:
```bash
uv run python -m app.ui.dashboard
```
Open **`http://127.0.0.1:7860`** in your browser!

---

## 🧪 Running Automated Tests

To run the full suite of mathematical validation and pricing tool unit tests:
```bash
uv run python -m pytest tests/
```

---

## ☁️ Deployment on Render Cloud

This app is configured for seamless deployment on **Render Cloud**:
1. Connect your GitHub repository to Render.
2. Select **Web Service** and choose **Docker** as the environment (Render will automatically detect the `Dockerfile`).
3. Add a **Persistent Disk** mounted at `/app/data` to persist your SQLite database changes between deployments.
4. Set up your secrets (`DEEPSEEK_API_KEY`, `SERPER_API_KEY`) as environment variables.
5. Pings Render's deploy hook from your GitHub Actions secret key to activate the CI/CD pipeline!
