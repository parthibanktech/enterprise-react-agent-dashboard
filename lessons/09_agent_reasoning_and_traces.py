"""
09_agent_reasoning_and_traces.py
==================================================
Concept: Introspecting Agent Reasoning & Visual Tracing

In production systems, we cannot just treat agents as a "black box" where we 
provide a query and wait for an answer. When an agent fails or takes a wrong turn, 
we must be able to inspect its intermediate steps programmatically.

In our unified `create_agent` framework, the entire history of intermediate steps
(actions and observations) is cleanly returned inside the "messages" state. 

We can loop over the returned list of messages to extract:
1. **THINK / ACT Steps**: Represented by `AIMessage` containing `.tool_calls`.
2. **OBSERVE Steps**: Represented by `ToolMessage` containing the tool's return `.content`.
3. **FINAL RESPONSE**: Represented by the final `AIMessage` with conversational `.content`.

In this lesson, we will:
1. Run a ReAct agent that queries our seeded product database.
2. Intercept the list of messages programmatically.
3. Parse and print a premium, color-coded, structured execution trace in the CLI.

*Note: If no valid DeepSeek API key is present in .env, this script runs in 
Simulation Mode, rendering the exact colorful step-by-step trace extraction.*
"""

import sys
import os

# Ensure UTF-8 encoding on Windows to prevent UnicodeEncodeError with emojis
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Add lessons directory to sys.path to resolve relative imports from anywhere
lessons_dir = os.path.dirname(os.path.abspath(__file__))
if lessons_dir not in sys.path:
    sys.path.append(lessons_dir)

import json
import time
import importlib
from dotenv import load_dotenv
from utils import print_banner
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent

db_tool_module = importlib.import_module("08_database_sql_tool")
seed_database = db_tool_module.seed_database
query_products_database = db_tool_module.query_products_database
get_database_schema = db_tool_module.get_database_schema

# ── 1. Color Helper Functions for Premium Visual Logs ────────────────────────

def print_section(title, color_code):
    print(f"\n{color_code}{'=' * 72}\033[0m")
    print(f"{color_code}✨ {title}\033[0m")
    print(f"{color_code}{'=' * 72}\033[0m")

def print_thought(text):
    print(f"🧠 \033[1;93m[THINKING LOG]:\033[0m")
    for line in text.split("\n"):
        if line.strip():
            print(f"   \033[93m{line.strip()}\033[0m")

def print_action(tool_name, tool_input):
    print(f"🎬 \033[1;92m[ACTION]: Calling tool '{tool_name}'\033[0m")
    print(f"   \033[92mArguments: {json.dumps(tool_input, indent=2)}\033[0m")

def print_observation(content):
    print(f"👁️ \033[1;96m[OBSERVATION]: Tool returned output:\033[0m")
    for line in content.split("\n")[:10]: # Print first 10 lines
        print(f"   \033[96m{line}\033[0m")
    if len(content.split("\n")) > 10:
        print("   \033[96m... [truncated for readability]\033[0m")

# ── 2. Live Trace Extraction Loop ─────────────────────────────────────────────

def run_live_tracing():
    schema = get_database_schema()
    
    # Construct unified agent
    agent = create_agent(
        model="deepseek:deepseek-chat",
        tools=[query_products_database],
        system_prompt=(
            f"You are a database business analyst agent. You have access to a products database.\n"
            f"Here is the database schema:\n{schema}\n"
            f"Write valid, secure SELECT queries using the 'query_products_database' tool. "
            f"Always think step-by-step."
        )
    )
    
    print("\n\033[92m✓ Live ReAct Tracing Agent is ready!\033[0m")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 72)
    print("\nTry queries like:")
    print("  → How many items of 'Wireless Ergonomic Mouse' are left in stock?\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "How many items of 'Wireless Ergonomic Mouse' are left in stock?"
            print(f"You: {user_input}")
        else:
            try:
                user_input = input("You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit"):
                print("\nGoodbye!")
                break

        print("\n--- Starting ReAct Execution Loop ---\n")
        try:
            result = agent.invoke({
                "messages": [HumanMessage(content=user_input)]
            })
            
            print_section("PROGRAMMATIC INTERMEDIATE TRACE", "\033[95m")
            
            messages = result.get("messages", [])
            step_idx = 1
            
            for msg in messages:
                role = msg.__class__.__name__
                
                if role == "AIMessage" and getattr(msg, "tool_calls", None):
                    print(f"\n\033[1;34m--- Reasoning Step {step_idx} ---\033[0m")
                    if msg.content:
                        print_thought(msg.content)
                    
                    for tc in msg.tool_calls:
                        print_action(tc["name"], tc["args"])
                    
                    step_idx += 1
                    
                elif role == "ToolMessage":
                    print_observation(msg.content)
                    
                elif role == "AIMessage" and msg.content and not getattr(msg, "tool_calls", None):
                    print_section("FINAL CONVERSATIONAL ANSWER", "\033[92m")
                    print(msg.content)
                    print("\033[95m=" * 72 + "\033[0m")
            print()
        except Exception as e:
            print(f"\033[91mError during execution: {e}\033[0m\n")
            
        if is_non_interactive:
            break

# ── 3. High-Fidelity Simulation Mode ──────────────────────────────────────────

def run_simulated_tracing():
    print("\n\033[93m⚠️ DEEPSEEK_API_KEY not configured or empty. Running simulation mode...\033[0m")
    print("Constructing agent using create_agent()...")
    time.sleep(0.5)
    print("\n\033[92m✓ Simulated ReAct Tracing Agent is ready!\033[0m")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 72)
    print("\nTry queries like:")
    print("  → How many items of 'Wireless Ergonomic Mouse' are left in stock?\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "How many items of 'Wireless Ergonomic Mouse' are left in stock?"
            print(f"You: {user_input}")
        else:
            try:
                user_input = input("You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit"):
                print("\nGoodbye!")
                break

        print("\n--- Starting ReAct Execution (Simulated) ---\n")
        
        if "mouse" in user_input.lower():
            print_section("PROGRAMMATIC INTERMEDIATE TRACE", "\033[95m")
            print("Total reasoning cycles executed: 1")
            time.sleep(0.5)
            
            print("\n\033[1;34m--- Reasoning Step 1 ---\033[0m")
            thought_log = (
                "The user wants to find out how many items of 'Wireless Ergonomic Mouse' are left in stock.\n"
                "I need to query the products database.\n"
                "I'll write a SELECT statement searching for name = 'Wireless Ergonomic Mouse'."
            )
            print_thought(thought_log)
            time.sleep(0.6)
            
            print_action("query_products_database", {"sql_query": "SELECT stock FROM products WHERE name = 'Wireless Ergonomic Mouse'"})
            time.sleep(0.5)
            
            observation = query_products_database.invoke({"sql_query": "SELECT stock FROM products WHERE name = 'Wireless Ergonomic Mouse'"})
            print_observation(observation)
            time.sleep(0.6)
            
            print_section("FINAL CONVERSATIONAL ANSWER", "\033[92m")
            final_ans = "There are currently 110 units of the 'Wireless Ergonomic Mouse' available in stock."
            print(final_ans)
            print("\033[95m=" * 72 + "\033[0m\n")
        else:
            print("  🧠 \033[93m[THINK/ACT]\033[0m → (Simulated thought: The user query is processed using visual tracing helpers.)")
            time.sleep(0.5)
            print("  🏁 \033[92m[FINAL RESPONSE]\033[0m → [Simulation Mode] This is a mock response. Please add a valid DEEPSEEK_API_KEY to your .env file to enable live execution for all queries.\n")
            
        if is_non_interactive:
            break

# ── 4. Main Entry Point ───────────────────────────────────────────────────────

def main():
    print_banner("09 — PROGRAMMATIC REASONING TRACES & VISUAL PRINTING")
    
    # Seeding database
    seed_database()
    
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    
    if not api_key or "your_deepseek" in api_key.lower():
        run_simulated_tracing()
    else:
        try:
            run_live_tracing()
        except Exception as e:
            print(f"\nError running live agent: {e}")
            run_simulated_tracing()

if __name__ == "__main__":
    main()
