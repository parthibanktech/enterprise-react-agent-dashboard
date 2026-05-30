import sys
import os

# Ensure UTF-8 encoding on Windows to prevent UnicodeEncodeError with emojis
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

import json
import time
from dotenv import load_dotenv
import gradio as gr
from langchain_core.messages import HumanMessage, AIMessage

# Production Core imports
from app.core.config import is_live_mode_available, get_deepseek_api_key
from app.core.agent import initialize_agent
from app.core.tracer import parse_agent_trace

# Production Tools imports
from app.tools.math_tools import calculate, divide, calculate_discount, calculate_gst, calculate_product_pricing
from app.tools.api_tools import geocode_location, get_weather_forecast, google_search
from app.tools.db_tools import query_products_database

# Load environment & setup
load_dotenv()
api_key = get_deepseek_api_key()

# Load Academy metadata
try:
    from app.services.academy import get_lessons_metadata, get_lesson_code, run_lesson
    LESSONS_METADATA = get_lessons_metadata()
    LESSON_CHOICES = [(l["title"], l["id"]) for l in LESSONS_METADATA]
except Exception as e:
    LESSONS_METADATA = []
    LESSON_CHOICES = []

# Production CAPSTONE_TOOLS
CAPSTONE_TOOLS = [
    calculate,
    divide,
    calculate_discount,
    calculate_gst,
    calculate_product_pricing,
    geocode_location,
    get_weather_forecast,
    google_search,
    query_products_database
]

# Initialize live agent graph
LIVE_AGENT = initialize_agent(CAPSTONE_TOOLS) if is_live_mode_available() else None

# Preset Simulated Prompts & Trace Files (for simulation mode)
SIMULATED_DATABASE = {
    "which products in the database have a price greater than $200?": {
        "final_answer": "Here are the premium items in stock costing more than $200:\n\n1. **Bamboo Standing Desk** - $599.00 (15 in stock)\n2. **UltraWide 34-inch Monitor** - $499.00 (20 in stock)\n3. **Noise-Cancelling Headphones** - $299.99 (35 in stock)\n4. **Ergonomic Desk Chair** - $249.99 (45 in stock)",
        "trace": """### 🧠 THINK (Cycle 1)
The user is asking for product details from our SQLite database where price is greater than $200.
I will construct a secure, read-only SQL query to retrieve these items.

### 🎬 ACT (Call Tool)
Calling `query_products_database` with arguments:
```json
{
  "sql_query": "SELECT name, price, stock FROM products WHERE price > 200 ORDER BY price DESC"
}
```

### 👁️ OBSERVE (Tool Output)
```json
[
  {
    "name": "Bamboo Standing Desk",
    "price": 599.0,
    "stock": 15
  },
  {
    "name": "UltraWide 34-inch Monitor",
    "price": 499.0,
    "stock": 20
  },
  {
    "name": "Noise-Cancelling Headphones",
    "price": 299.99,
    "stock": 35
  },
  {
    "name": "Ergonomic Desk Chair",
    "price": 249.99,
    "stock": 45
  }
]
```

### 🏁 THINK (Cycle 2)
The database returned four products. I have successfully gathered the required name, price, and stock levels. I will format this into a clean, structured reply for the user."""
    },
    "i am traveling to tokyo. check if it's raining and tell me what to bring!": {
        "final_answer": "Current conditions in **Tokyo** report a temperature of **16.8°C** with **Slight Rain**.\nSince it is raining, you should definitely carry an **umbrella** today!",
        "trace": """### 🧠 THINK (Cycle 1)
The user wants weather recommendations for Tokyo.
First, I need to look up Tokyo's latitude and longitude using coordinates.

### 🎬 ACT (Call Tool)
Calling `geocode_location` with arguments:
```json
{
  "city_name": "Tokyo"
}
```

### 👁️ OBSERVE (Tool Output)
```json
{
  "latitude": 35.6895,
  "longitude": 139.6917,
  "city": "Tokyo",
  "country": "Japan"
}
```

### 🧠 THINK (Cycle 2)
Now that I have Tokyo's coordinates (35.6895, 139.6917), I can request the current weather metrics.

### 🎬 ACT (Call Tool)
Calling `get_weather_forecast` with arguments:
```json
{
  "latitude": 35.6895,
  "longitude": 139.6917
}
```

### 👁️ OBSERVE (Tool Output)
```json
{
  "temperature": "16.8°C",
  "windspeed": "12.4 km/h",
  "weather_code": 61,
  "description": "Slight Rain",
  "is_raining": true
}
```

### 🏁 THINK (Cycle 3)
The weather forecast indicates active rain (Slight Rain). According to the traveler instruction, I should advise carrying an umbrella."""
    },
    "what is the final invoice for 12 desk chairs at $249.99 each with a 15% discount and 8% tax?": {
        "final_answer": "Here is the invoice breakdown for **12 Ergonomic Desk Chairs** at **$249.99** each:\n\n*   **Raw Subtotal**: $2,999.88\n*   **15% Bulk Discount**: -$449.98\n*   **Taxable Subtotal**: $2,549.90\n*   **Sales Tax (8%)**: +$203.99\n*   **Final Invoice Total**: **$2,753.89**",
        "trace": """### 🧠 THINK (Cycle 1)
The user wants an invoice breakdown with discount and sales tax.
I should use the product pricing calculator.

### 🎬 ACT (Call Tool)
Calling `calculate_product_pricing` with arguments:
```json
{
  "base_price": 249.99,
  "quantity": 12,
  "discount_percentage": 15.0,
  "tax_percentage": 8.0
}
```

### 👁️ OBSERVE (Tool Output)
```json
{
  "unit_price": "$249.99",
  "quantity": 12,
  "raw_subtotal": "$2,999.88",
  "applied_discount_rate": "15.0%",
  "discount_savings": "$449.98",
  "taxable_amount": "$2,549.90",
  "tax_rate": "8.0%",
  "tax_amount": "$203.99",
  "final_invoice_total": "$2,753.89"
}
```

### 🏁 THINK (Cycle 2)
The calculator returned the complete breakdown. I will summarize these lines in a clean invoice table for the user."""
    }
}

def format_trace_to_markdown(steps: list) -> str:
    """Format the list of parsed trace steps into beautiful Gradio markdown blocks."""
    if not steps:
        return "### 🧠 THINK (Cycle 1)\nNo tool calls were needed. Answering prompt directly."
    
    trace_builder = []
    for idx, step in enumerate(steps):
        step_idx = idx + 1
        thought = step.get("thought", "Analyzing request and selecting tool...")
        if "<think>" in thought:
            thought = thought.replace("<think>", "").replace("</think>", "").strip()
            
        trace_builder.append(f"### 🧠 THINK (Cycle {step_idx})\n{thought}\n")
        
        tool_name = step.get("tool_name")
        if tool_name:
            args = step.get("args", {})
            trace_builder.append(f"### 🎬 ACT (Call Tool)\nCalling `{tool_name}` with parameters:\n```json\n{json.dumps(args, indent=2)}\n```\n")
            
        obs = step.get("observation")
        if obs:
            try:
                parsed_obs = json.loads(obs)
                formatted_obs = json.dumps(parsed_obs, indent=2)
            except Exception:
                formatted_obs = str(obs)
            trace_builder.append(f"### 👁️ OBSERVE (Tool Output)\n```json\n{formatted_obs}\n```\n")
            
    return "\n".join(trace_builder)

def run_agent_turn(user_message, history, engine_mode):
    """Processes one turn of chat, returning updated chat history and the markdown trace."""
    history = history or []
    query = user_message.strip()
    
    # ── CASE A: Interactive Simulator ──
    if engine_mode == "Interactive Simulator" or not LIVE_AGENT:
        lookup_key = query.lower().rstrip("?")
        
        matched_preset = None
        for key in SIMULATED_DATABASE:
            if key in lookup_key:
                matched_preset = SIMULATED_DATABASE[key]
                break
                
        if matched_preset:
            trace_output = ""
            for block in matched_preset["trace"].split("\n\n"):
                trace_output += block + "\n\n"
                yield history + [[query, "⏳ Reasoning... Please check the right pane."]], trace_output
                time.sleep(1.0)
            
            final_ans = matched_preset["final_answer"]
            yield history + [[query, final_ans]], matched_preset["trace"]
        else:
            no_match_text = (
                "Hi! I am currently running in **Simulation Demo Mode**.\n\n"
                "Please ask one of these three pre-coded scenarios to see the full ReAct loop in action:\n"
                "1. *'Which products in the database have a price greater than $200?'*\n"
                "2. *'I am traveling to Tokyo. Check if it's raining and tell me what to bring!'*\n"
                "3. *'What is the final invoice for 12 desk chairs at $249.99 each with a 15% discount and 8% tax?'*"
            )
            sim_trace = "### 🧠 THINK (Cycle 1)\nUser prompt did not match a pre-coded scenario. Explaining simulation mode limits to user."
            yield history + [[query, no_match_text]], sim_trace

    # ── CASE B: Live DeepSeek Agent ──
    else:
        try:
            yield history + [[query, "⏳ Activating ReAct loop in DeepSeek..."]], "### 🧠 THINK (Cycle 1)\nConnecting to Live ChatDeepSeek LLM..."
            
            # Format chat history for LangChain
            formatted_history = []
            for h in history:
                if len(h) >= 2:
                    formatted_history.append(HumanMessage(content=h[0]))
                    formatted_history.append(AIMessage(content=h[1]))
            
            # Invoke agent
            result = LIVE_AGENT.invoke({
                "messages": formatted_history + [HumanMessage(content=query)]
            })
            
            # Parse traces using production parser
            trace_info = parse_agent_trace(result.get("messages", []))
            full_trace = format_trace_to_markdown(trace_info["steps"])
            final_response = trace_info["final_response"] or "No conversational response returned by agent."
            
            yield history + [[query, final_response]], full_trace
            
        except Exception as e:
            err_msg = f"Error during live invocation: {e}"
            yield history + [[query, f"❌ Request failed. {err_msg}"]], f"### ⚠️ ERROR\n{err_msg}"

# Build Gradio Blocks Interface
custom_css = """
body, .gradio-container {
    background-color: #0f172a !important;
    font-family: 'Inter', 'Outfit', sans-serif !important;
    color: #e2e8f0 !important;
}
.glass-header {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
.sidebar-panel {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    height: 600px;
    overflow-y: auto;
}
.chatbot-panel {
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    background-color: #0f172a !important;
}
.footer-text {
    text-align: center;
    color: #64748b;
    margin-top: 20px;
    font-size: 0.9em;
}
.console-terminal {
    background-color: #020617 !important;
    color: #38bdf8 !important;
    font-family: 'Courier New', Courier, monospace !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
}
.academy-sidebar {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
.academy-code {
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}
"""

with gr.Blocks(css=custom_css, title="Capstone Agent Dashboard") as demo:
    
    # HEADER
    with gr.Row(elem_classes="glass-header"):
        with gr.Column():
            gr.Markdown(
                "# 🧠 SENTRY AI: PARTHIBAN'S CONSOLIDATED ENTERPRISE REACT DASHBOARD\n"
                "Welcome to Parthiban's ultimate Capstone! This interactive interface exposes the "
                "**ReAct Reasoning Loop** in action. Ask questions about SQLite product catalogs, "
                "pricing calculations, or geocoded weather warnings to see the agent chain intermediate tools."
            )
            
            with gr.Row():
                mode_selector = gr.Radio(
                    choices=["Interactive Simulator", "Live DeepSeek Agent"],
                    value="Live DeepSeek Agent" if is_live_mode_available() else "Interactive Simulator",
                    label="Active Execution Engine",
                    interactive=True,
                    info="Choose 'Interactive Simulator' to run keyless demonstrations instantly."
                )

    with gr.Tabs():
        with gr.Tab("💬 Agent Sandbox"):
            # MAIN LAYOUT
            with gr.Row():
                # Left Panel: Conversation Interface
                with gr.Column(scale=5):
                    gr.Markdown("### 💬 Conversational Chat Interface")
                    chatbot = gr.Chatbot(
                        elem_classes="chatbot-panel",
                        height=450
                    )
                    
                    with gr.Row():
                        user_input = gr.Textbox(
                            placeholder="Type your agent query here... (e.g. 'Which products in the database have a price greater than $200?')",
                            show_label=False,
                            scale=8
                        )
                        submit_btn = gr.Button("Submit Query", variant="primary", scale=2)
                        
                    with gr.Row():
                        gr.Markdown("**💡 Preset Prompts (1-5):**", scale=2)
                        scenario1_btn = gr.Button("Scenario 1", variant="secondary", size="sm", scale=1)
                        scenario2_btn = gr.Button("Scenario 2", variant="secondary", size="sm", scale=1)
                        scenario3_btn = gr.Button("Scenario 3", variant="secondary", size="sm", scale=1)
                        scenario4_btn = gr.Button("Scenario 4", variant="secondary", size="sm", scale=1)
                        scenario5_btn = gr.Button("Scenario 5", variant="secondary", size="sm", scale=1)
                    with gr.Row():
                        gr.Markdown("**💡 Preset Prompts (6-10):**", scale=2)
                        scenario6_btn = gr.Button("Scenario 6", variant="secondary", size="sm", scale=1)
                        scenario7_btn = gr.Button("Scenario 7", variant="secondary", size="sm", scale=1)
                        scenario8_btn = gr.Button("Scenario 8", variant="secondary", size="sm", scale=1)
                        scenario9_btn = gr.Button("Scenario 9", variant="secondary", size="sm", scale=1)
                        scenario10_btn = gr.Button("Scenario 10", variant="secondary", size="sm", scale=1)

                # Right Panel: System Reasoning Trace Terminal
                with gr.Column(scale=5):
                    gr.Markdown("### 🧠 Real-Time Agent Reasoning Trace (THINK-ACT-OBSERVE)")
                    trace_pane = gr.Markdown(
                        "### ⏳ Waiting for Agent Execution...\n"
                        "When you submit a query, the step-by-step thinking processes, tool arguments, "
                        "and raw outputs of each ReAct cycle will stream here in real time.",
                        elem_classes="sidebar-panel"
                    )

        with gr.Tab("🎓 Syllabus Reference"):
            with gr.Row():
                # Left Panel: Syllabus selection
                with gr.Column(scale=4, elem_classes="academy-sidebar"):
                    gr.Markdown("### 📚 Agent Syllabus Modules")
                    lesson_dropdown = gr.Dropdown(
                        choices=LESSON_CHOICES,
                        value=LESSON_CHOICES[0][1] if LESSON_CHOICES else None,
                        label="Select Lesson",
                        interactive=True
                    )
                    lesson_meta = gr.Markdown(
                        value="### 💡 **Concept**: Loading..." if LESSON_CHOICES else "No lessons loaded."
                    )
                    run_btn = gr.Button("▶ Run Lesson Code", variant="primary")
                    
                # Right Panel: Source Code & Console Logs
                with gr.Column(scale=8):
                    gr.Markdown("### 📝 Module Source Code")
                    code_viewer = gr.Code(
                        label="Python Code",
                        language="python",
                        value="",
                        interactive=False,
                        elem_classes="academy-code"
                    )
                    gr.Markdown("### 💻 Console Output Terminal")
                    console_output = gr.Textbox(
                        label="",
                        value="",
                        interactive=False,
                        lines=12,
                        elem_classes="console-terminal",
                        show_label=False
                    )

    # FOOTER
    gr.Markdown(
        "AI Agentathon 4.0 • Designed for Tech Leaders Hub • Powered by LangChain & Gradio Blocks",
        elem_classes="footer-text"
    )

    # INTERACTIVE LOGIC
    def process_chat(message, history, mode):
        for hist_update, trace_update in run_agent_turn(message, history, mode):
            yield hist_update, trace_update

    submit_btn.click(
        fn=process_chat,
        inputs=[user_input, chatbot, mode_selector],
        outputs=[chatbot, trace_pane]
    )
    user_input.submit(
        fn=process_chat,
        inputs=[user_input, chatbot, mode_selector],
        outputs=[chatbot, trace_pane]
    )

    # Preset scenarios click mapping
    scenario1_btn.click(
        fn=lambda: "Which products in the database have a price greater than $200?",
        inputs=None,
        outputs=[user_input]
    )
    scenario2_btn.click(
        fn=lambda: "I am traveling to Tokyo. Check if it's raining and tell me what to bring!",
        inputs=None,
        outputs=[user_input]
    )
    scenario3_btn.click(
        fn=lambda: "What is the final invoice for 12 desk chairs at $249.99 each with a 15% discount and 8% tax?",
        inputs=None,
        outputs=[user_input]
    )
    scenario4_btn.click(
        fn=lambda: "What is 347 multiplied by 86, and then divide that result by 5?",
        inputs=None,
        outputs=[user_input]
    )
    scenario5_btn.click(
        fn=lambda: "What is today's date? Check the system clock and tell me what day of the week it is.",
        inputs=None,
        outputs=[user_input]
    )
    scenario6_btn.click(
        fn=lambda: "Search Google for top tourist spots and news in Noida, India.",
        inputs=None,
        outputs=[user_input]
    )
    scenario7_btn.click(
        fn=lambda: "A professional laptop costs ₹65000 before tax. GST is 18%. Calculate the GST amount and total price.",
        inputs=None,
        outputs=[user_input]
    )
    scenario8_btn.click(
        fn=lambda: "An designer Kurta costs ₹1800 and is currently on a 35% discount. What are my savings and final pay amount?",
        inputs=None,
        outputs=[user_input]
    )
    scenario9_btn.click(
        fn=lambda: "What is the category and pric of the Ergonomic Desk Chair in the database?",
        inputs=None,
        outputs=[user_input]
    )
    scenario10_btn.click(
        fn=lambda: "What is 50 divided by 0? Can you compute this mathematically?",
        inputs=None,
        outputs=[user_input]
    )

    # ACADEMY INTERACTIVE LOGIC
    def load_lesson_details(lesson_id):
        if not lesson_id:
            return "", "", ""
        metas = [l for l in LESSONS_METADATA if l["id"] == lesson_id]
        meta = metas[0] if metas else {"concept": "", "description": ""}
        
        try:
            code_data = get_lesson_code(lesson_id)
            code_content = code_data["code"]
            filename = code_data["filename"]
        except Exception as e:
            code_content = f"# Error loading lesson code: {e}"
            filename = ""
            
        meta_md = f"### 💡 **Concept**:\n{meta['concept']}\n\n**Description**:\n{meta['description']}"
        initial_log = f"[SYSTEM] Loaded Syllabus Module: {filename}\n[SYSTEM] Ready to execute. Click the 'Run Lesson Code' button above."
        
        return meta_md, code_content, initial_log

    def execute_lesson(lesson_id):
        if not lesson_id:
            yield "No lesson selected."
            return
        
        yield "⏳ Executing script inside workspace environment..."
        try:
            res = run_lesson(lesson_id)
            out = ""
            if res.get("stdout"):
                out += res["stdout"]
            if res.get("stderr"):
                out += "\n" + res["stderr"]
            if res.get("exit_code") == 0:
                out += "\n\n[SUCCESS] Script finished successfully (exit code 0)."
            else:
                out += f"\n\n[ERROR] Script exited with non-zero exit code: {res.get('exit_code')}."
            yield out
        except Exception as e:
            yield f"[FATAL] Subprocess execution failed: {e}"

    if LESSON_CHOICES:
        # Load initial values
        demo.load(
            fn=load_lesson_details,
            inputs=[lesson_dropdown],
            outputs=[lesson_meta, code_viewer, console_output]
        )
        
        # When changing selection
        lesson_dropdown.change(
            fn=load_lesson_details,
            inputs=[lesson_dropdown],
            outputs=[lesson_meta, code_viewer, console_output]
        )
        
        # When clicking run button
        run_btn.click(
            fn=execute_lesson,
            inputs=[lesson_dropdown],
            outputs=[console_output]
        )

if __name__ == "__main__":
    if not is_live_mode_available():
        print("\033[93m")
        print("=" * 72)
        print("💡 CAPSTONE NOTICE: DEEPSEEK_API_KEY is not set.")
        print("   The UI will launch in 'Interactive Simulator' mode by default.")
        print("   Configure your key in .env to unlock real-time live model agent execution!")
        print("=" * 72)
        print("\033[0m")
        
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
