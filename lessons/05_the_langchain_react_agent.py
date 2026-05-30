"""
05_the_langchain_react_agent.py
==================================================
Concept: Transitioning to LangChain's Unified create_agent

In Lesson 04, we wrote a raw Python `while` loop to coordinate our ReAct agent.
While hand-writing loops demystifies the loop under the hood, managing history,
message mapping, and multi-turn execution becomes complex in larger applications.

To solve this, our custom `langchain` educational library provides a unified abstraction:
- **`create_agent`**: Sets up the agent graph, compiles system instructions,
  and handles the entire ReAct loop execution in one line.

In this lesson, we will transition our calculator agent to use the simplified `create_agent`
framework.

*Note: If no valid DeepSeek API key is present in .env, this script will run a 
high-fidelity simulation to demonstrate the exact trace of the agent execution.*
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

import time
from dotenv import load_dotenv
from utils import print_banner
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent

# ── 1. Define Our Tool ────────────────────────────────────────────────────────

@tool
def calculate(expression: str) -> str:
    """Evaluate any mathematical expression precisely. Use this for ALL arithmetic queries.
    Never guess numbers.
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@tool
def get_current_date() -> str:
    """Get today's date from the system clock.
    Use this whenever the user asks about the current date or day.
    """
    from datetime import date
    return f"Today is {date.today().strftime('%A, %d %B %Y')}"

@tool
def calculate_discount(original_price: float, discount_percent: float) -> str:
    """Calculate the final price after applying a percentage discount.

    Args:
        original_price: The original price in rupees
        discount_percent: The discount percentage e.g. 35 for 35%
    """
    saving = original_price * (discount_percent / 100)
    final  = original_price - saving
    return f"Original: ₹{original_price:,.0f} | Saving: ₹{saving:,.0f} | You pay: ₹{final:,.0f}"

@tool
def calculate_gst(base_price: float, gst_percent: float) -> str:
    """Calculate the GST amount and total price after GST.

    Args:
        base_price: The price before GST in rupees
        gst_percent: The GST rate e.g. 18 for 18%
    """
    gst_amount = base_price * (gst_percent / 100)
    total      = base_price + gst_amount
    return f"Base: ₹{base_price:,.0f} | GST ({gst_percent}%): ₹{gst_amount:,.0f} | Total: ₹{total:,.0f}"

tools = [calculate, get_current_date, calculate_discount, calculate_gst]

# ── 2. Run the Live LangChain Agent ───────────────────────────────────────────

def run_live_agent():
    print("Constructing live agent using create_agent()...")

    # Unified create_agent automatically sets up the state graph and loops under the hood
    agent = create_agent(
        model="deepseek:deepseek-chat",
        tools=tools,
        system_prompt=(
            "You are a helpful and precise assistant. "
            "Always use the available tools instead of guessing — "
            "use calculate for arithmetic, get_current_date for today's date, "
            "calculate_discount for price-after-discount questions, "
            "and calculate_gst for GST and tax calculations. Never guess numbers."
        )
    )

    print("\n\033[92m✓ Live ReAct Agent is ready!\033[0m")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 72)
    print("\nTry queries like:")
    print("  → What is 347 multiplied by 86, and then divide that result by 5?")
    print("  → What is today's date?")
    print("  → A kurta costs ₹1800 and is 35% off. What do I pay?")
    print("  → A laptop costs ₹65000. GST is 18%. What is the total?\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "What is 347 multiplied by 86, and then divide that result by 5?"
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
                if role == "HumanMessage":
                    continue
                elif role == "AIMessage":
                    if getattr(msg, "tool_calls", None):
                        for tc in msg.tool_calls:
                            print(f"  🧠 \033[93m[THINK/ACT]\033[0m → calling {tc['name']}({tc['args']})")
                    elif msg.content:
                        print(f"  🏁 \033[92m[FINAL RESPONSE]\033[0m → {msg.content}")
                elif role == "ToolMessage":
                    print(f"  👁️ \033[96m[OBSERVE]\033[0m → {msg.content}")
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
    print("\n\033[92m✓ Simulated ReAct Agent is ready!\033[0m")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 72)
    print("\nTry queries like:")
    print("  → What is 347 multiplied by 86, and then divide that result by 5?\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "What is 347 multiplied by 86, and then divide that result by 5?"
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
        
        if "347" in user_input and "86" in user_input:
            # Phase 1
            print("  🧠 \033[93m[THINK/ACT]\033[0m → calling calculate({'expression': '347 * 86'})")
            time.sleep(0.5)
            ans1 = "29842"
            print(f"  👁️ \033[96m[OBSERVE]\033[0m → {ans1}")
            time.sleep(0.8)
            
            # Phase 2
            print("  🧠 \033[93m[THINK/ACT]\033[0m → calling calculate({'expression': '29842 / 5'})")
            time.sleep(0.5)
            ans2 = "5968.4"
            print(f"  👁️ \033[96m[OBSERVE]\033[0m → {ans2}")
            time.sleep(0.8)
            
            # Final Response
            print(f"  🏁 \033[92m[FINAL RESPONSE]\033[0m → The result of multiplying 347 by 86 is 29,842. Dividing that result by 5 gives 5,968.4.\n")
        else:
            print("  🧠 \033[93m[THINK/ACT]\033[0m → (Simulated thought: The user query is processed step-by-step using tools.)")
            time.sleep(0.5)
            print("  🏁 \033[92m[FINAL RESPONSE]\033[0m → [Simulation Mode] This is a mock response. Please add a valid DEEPSEEK_API_KEY to your .env file to enable live execution for all queries.\n")
            
        if is_non_interactive:
            break

# ── 4. Main Entry Point ───────────────────────────────────────────────────────

def main():
    print_banner("05 — THE LANGCHAIN REACT AGENT EXECUTOR")
    
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
