# ☁️ Deploying to Render Cloud

This guide provides step-by-step instructions to deploy the **Enterprise ReAct Agent Dashboard** to [Render Cloud](https://render.com). 

The repository is fully optimized for Render using a custom `Dockerfile` and Infrastructure-as-Code `render.yaml` blueprint. It includes a **Persistent Disk** mount to ensure your SQLite product database survives restarts and redeployments.

---

## 🏗️ Pre-requisites

Before deploying, make sure you have:
1. A **Render Account** (Free tier works perfectly).
2. Your **GitHub Repository** URL (where you pushed this code).
3. API Keys for your tools:
   * `DEEPSEEK_API_KEY` (Required for ReAct Agent reasoning)
   * `SERPER_API_KEY` (Required for Google Search tool integration)
   * `OPENWEATHER_API_KEY` (Optional, for geocoded weather forecast tool)

---

## ⚡ Method 1: The Blueprints Way (Recommended & Easiest)

Render Blueprints read the `render.yaml` file in the root of your repository to automatically configure the service, container, ports, and persistent storage disk in one click.

### Step-by-Step Instructions:

1. Log in to the **[Render Dashboard](https://dashboard.render.com)**.
2. Click the **New +** button in the top-right corner and select **Blueprint**.
3. Select and connect your repository: `enterprise-react-agent-dashboard`.
4. Render will parse the `render.yaml` file and show a plan:
   * **Service Name**: `capstone-react-agent`
   * **Service Type**: `Web Service`
   * **Environment**: `Docker`
   * **Persistent Disk**: `sqlite-data` (1 GB mounted to `/app/data`)
5. You will see a list of **Environment Variables** requiring your input. Provide your secrets:
   * `DEEPSEEK_API_KEY`
   * `SERPER_API_KEY`
   * `OPENWEATHER_API_KEY` (Optional)
6. Click **Apply**.
7. Render will automatically spin up the build pipeline, build the Docker container, run database seeds, mount your database volume, and deploy your live dashboard!

---

## 🛠️ Method 2: Manual Web Service Setup

If you prefer to configure your deployment step-by-step via the Render web interface:

### Step 1: Create the Web Service
1. Log in to your **[Render Dashboard](https://dashboard.render.com)**.
2. Click **New +** and select **Web Service**.
3. Connect your repository: `enterprise-react-agent-dashboard`.

### Step 2: Configure Core Settings
Fill in the following fields in the creation form:
* **Name**: `enterprise-react-agent-dashboard`
* **Region**: Select a region close to you (e.g., `Oregon (US West)`)
* **Branch**: `main`
* **Language**: `Docker` (Render automatically detects the root `Dockerfile`)
* **Instance Type**: `Free` or `Starter`

### Step 3: Configure Advanced Settings
Click **Advanced** near the bottom of the page and configure:

#### 📁 Persistent Storage Disk
To prevent your SQLite database (`products.sqlite`) from resetting every time the service restarts:
1. Click **Add Disk**.
2. **Name**: `sqlite-data`
3. **Mount Path**: `/app/data`
4. **Size**: `1 GiB`

#### 🔑 Environment Variables
Add the following keys and values:
| Key | Value | Purpose |
| :--- | :--- | :--- |
| `DEEPSEEK_API_KEY` | `your_deepseek_key` | Authenticate deepseek model queries |
| `SERPER_API_KEY` | `your_serper_key` | Google search results tool integration |
| `PYTHON_ENV` | `production` | Configure application environment |
| `OPENWEATHER_API_KEY` | `your_weather_key` | (Optional) Geocoded weather lookup |

### Step 4: Deploy
Click **Create Web Service**. Render will start building the Docker image and deploy it.

---

## 🔍 How It Works Under the Hood

### Docker Build Phase
When you commit code or trigger a deploy, Render runs your custom [Dockerfile](file:///d:/AI_AGENT_HACKTHON/4.0/mission2%20(1)/Dockerfile):
1. Downloads a slim, secure `python:3.11` base image.
2. Leverages Docker caches to restore and install dependencies defined in [pyproject.toml](file:///d:/AI_AGENT_HACKTHON/4.0/mission2%20(1)/pyproject.toml).
3. Automatically runs the database seeding script (`python -c "from data.seed import seed_database; seed_database()"`) to set up initial product lists and SQLite database.
4. Exposes and binds the Gradio web UI to port `7860`.

### Persistent Storage
Any updates or changes written to `/app/data/products.sqlite` are safely written to Render's persistent disk, making sure changes survive app updates, daily sleep cycles (on free tiers), or crashes.
