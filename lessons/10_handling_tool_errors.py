"""
10_handling_tool_errors.py
==================================================
Concept: Resiliency, Self-Correction & Handling Tool Errors

What happens when a tool crashes?
- In a traditional, hardcoded software script, a runtime error (like a database syntax 
  error or division by zero) crashes the entire application.
- In a **ReAct loop**, the error is caught, formatted as a string, and sent back 
  to the LLM as an **Observation**!

The LLM then:
1. **THINKs**: *“Aha, the database returned an error saying column 'pric' does not exist. I must have misspelled it. I should use the column 'price' instead.”*
2. **ACTs**: Generates a corrected SQL query and tries again!

This self-correcting behavior is one of the most powerful features of ReAct agents.

In this lesson, we will demonstrate two types of self-correction inside Parthiban's unified `create_agent()`:
1. **Zero-Division Exception Interception**: The agent tries to perform an undefined 
   math operation and gracefully explains the limit without crashing.
2. **SQL Misspelling Recovery**: The agent generates an invalid SQL query, receives 
   the SQLite error, corrects its syntax, and fetches the right data.

*Note: If no valid DeepSeek API key is present in .env, this script runs a 
high-fidelity simulation showing the exact self-correction reasoning cycles.*
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

# Dynamically import SQLite functions from Lesson 08 to prevent numeric import errors
db_tool_module = importlib.import_module("08_database_sql_tool")
seed_database = db_tool_module.seed_database
query_products_database = db_tool_module.query_products_database
get_database_schema = db_tool_module.get_database_schema

# ── 1. Create a Division Tool that raises an exception ────────────────────────

@tool
def divide(a: float, b: float) -> str:
    """Divide two numbers a and b. Use this for division calculations."""
    print(f"📡 [Division Tool] Executing {a} / {b}...")
    try:
        res = a / b
        return str(res)
    except ZeroDivisionError:
        return "Error: Division by zero is mathematically undefined."

# Register tools
tools = [divide, query_products_database]

# ── 2. Run the Live Resiliency Demos ──────────────────────────────────────────

def run_live_agent():
    print("Constructing live agent using create_agent()...")
    schema = get_database_schema()
    
    agent = create_agent(
        model="deepseek:deepseek-chat",
        tools=tools,
        system_prompt=(
            f"You are a resilient business analyst agent.\n"
            f"Here is the database schema for the products database:\n{schema}\n"
            f"Use query_products_database for DB queries and divide for division.\n"
            f"If you encounter a database column error, read the error message, correct your spelling, "
            f"and try calling the database again. Never crash!"
        )
    )
    
    print("\n\033[92m✓ Live ReAct Resilient Agent is ready!\033[0m")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 72)
    print("\nTry queries like:")
    print("  → What is 50 divided by 0?  (Zero Division error)")
    print("  → What is the category and pric of Ergonomic Desk Chair?  (Spelling recovery)")
    print("  → Which products cost more than $300?\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "What is the category and pric of Ergonomic Desk Chair?"
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
            
            print("\n--- Programmatic Trace Inspection ---")
            for msg in result["messages"]:
                role = msg.__class__.__name__
                if role == "AIMessage" and getattr(msg, "tool_calls", None):
                    for tc in msg.tool_calls:
                        print(f"  🧠 \033[93m[THINK/ACT]\033[0m → calling {tc['name']}({tc['args']})")
                elif role == "ToolMessage":
                    print(f"  👁️ \033[96m[OBSERVE]\033[0m → {msg.content}")
                elif role == "AIMessage" and msg.content and not getattr(msg, "tool_calls", None):
                    print(f"  🏁 \033[92m[FINAL RESPONSE]\033[0m → {msg.content}")
            print()
        except Exception as e:
            print(f"\033[91mError during execution: {e}\033[0m\n")
            
        if is_non_interactive:
            break

# ── 3. High-Fidelity Simulation Mode ──────────────────────────────────────────

def run_simulated_agent():
    print("\n\033[93m⚠️ DEEPSEEK_API_KEY not configured or empty. Running simulation mode...\033[0m")
    print("Constructing agent using create_agent()...")
    time.sleep(0.5)
    print("\n\033[92m✓ Simulated ReAct Resilient Agent is ready!\033[0m")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 72)
    print("\nTry queries like:")
    print("  → What is 50 divided by 0?")
    print("  → What is the category and pric of Ergonomic Desk Chair?\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "What is the category and pric of Ergonomic Desk Chair?"
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

        print("\n--- Starting ReAct Execution Loop (Simulated) ---\n")
        
        if "divided by 0" in user_input.lower() or "/ 0" in user_input:
            print("  🧠 \033[93m[THINK/ACT]\033[0m → calling divide({'a': 50.0, 'b': 0.0})")
            time.sleep(0.5)
            obs1 = divide.invoke({"a": 50.0, "b": 0.0})
            print(f"  👁️ \033[96m[OBSERVE]\033[0m → {obs1}")
            time.sleep(0.8)
            
            ans1 = "Dividing 50 by 0 is mathematically undefined, so I cannot calculate a numerical result."
            print(f"  🏁 \033[92m[FINAL RESPONSE]\033[0m → {ans1}\n")
            
        elif "pric" in user_input.lower():
            bad_sql = "SELECT category, pric FROM products WHERE name = 'Ergonomic Desk Chair'"
            print(f"  🧠 \033[93m[THINK/ACT]\033[0m → calling query_products_database({{'sql_query': \"{bad_sql}\"}})")
            time.sleep(0.5)
            obs2_bad = query_products_database.invoke({"sql_query": bad_sql})
            print(f"  👁️ \033[96m[OBSERVE]\033[0m → {obs2_bad}")
            time.sleep(1.0)
            
            print("  🧠 \033[93m[THINK/ACT]\033[0m → Self-Correcting spelling error: Changing column 'pric' to 'price' based on schema guidelines.")
            time.sleep(0.5)
            
            good_sql = "SELECT category, price FROM products WHERE name = 'Ergonomic Desk Chair'"
            print(f"  🧠 \033[93m[THINK/ACT]\033[0m → calling query_products_database({{'sql_query': \"{good_sql}\"}})")
            time.sleep(0.5)
            obs2_good = query_products_database.invoke({"sql_query": good_sql})
            print(f"  👁️ \033[96m[OBSERVE]\033[0m → {obs2_good}")
            time.sleep(0.8)
            
            ans2 = "The category of the 'Ergonomic Desk Chair' is Furniture, and its price is $249.99."
            print(f"  🏁 \033[92m[FINAL RESPONSE]\033[0m → {ans2}\n")
        else:
            print("  🧠 \033[93m[THINK/ACT]\033[0m → (Simulated thought: The user query is processed step-by-step using resilient handlers.)")
            time.sleep(0.5)
            print("  🏁 \033[92m[FINAL RESPONSE]\033[0m → [Simulation Mode] This is a mock response. Please add a valid DEEPSEEK_API_KEY to your .env file to enable live execution for all queries.\n")
            
        if is_non_interactive:
            break

# ── 4. Main Entry Point ───────────────────────────────────────────────────────

def main():
    print_banner("10 — RESILIENCY: SELF-CORRECTING AGENT EXECUTIONS")
    
    # Seed DB
    seed_database()
    
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    
    if not api_key or "your_deepseek" in api_key.lower():
        run_simulated_agent()
    else:
        try:
            run_live_agent()
        except Exception as e:
            print(f"\nError running live agent: {e}")
            run_simulated_agent()

if __name__ == "__main__":
    main()
