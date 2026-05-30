"""
06_custom_tool_design.py
==================================================
Concept: Custom Tool Design, Argument Schema & Validation

In previous lessons, we used simple mathematical calculators. But in real-world 
applications, agents require custom tools with multiple parameters, default values, 
and strong input validation.

How does the LLM know how to call your custom tool?
LangChain parses three components of your Python function using the `@tool` decorator:
1. **The Function Name**: Becomes the tool name.
2. **The Docstring**: Becomes the tool's natural language description (what it does, when to use it).
3. **Python Type Hints**: Tells the LLM what data types to generate (e.g., `int`, `float`, `str`).

In this lesson, we will:
1. Create a premium multi-parameter `calculate_product_pricing` tool.
2. Inspect the generated JSON Schema (`.args` property) to see exactly what the LLM sees.
3. Run this custom tool *directly inside* our ReAct `create_agent()` framework to solve a pricing query!

*Note: If no valid DeepSeek API key is present in .env, this script will run a 
high-fidelity simulation to demonstrate the exact trace of the ReAct pricing execution.*
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
from dotenv import load_dotenv
from utils import print_banner
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent

# ── 1. Create a Premium Multi-Parameter Custom Tool ───────────────────────────

@tool
def calculate_product_pricing(
    base_price: float,
    quantity: int,
    discount_percentage: float = 0.0,
    tax_percentage: float = 5.0
) -> str:
    """
    Calculate the precise bulk order invoice pricing including discount and sales tax.
    
    Parameters:
    - base_price: The retail unit price of a single product item. Must be a positive decimal float.
    - quantity: The total number of items ordered. Must be a positive integer.
    - discount_percentage: Percentage discount to apply (e.g. 12.0 for 12%). Defaults to 0.0.
    - tax_percentage: Sales tax rate to apply to the discounted total (e.g. 6.0 for 6%). Defaults to 5.0.
    
    Returns:
    A detailed JSON string breaking down the subtotal, applied discount, tax, and final net total.
    """
    # Defensive programming/validation inside the tool
    if base_price <= 0:
        return "Error: base_price must be a positive number greater than zero."
    if quantity <= 0:
        return "Error: quantity must be a positive integer greater than zero."
    
    subtotal = base_price * quantity
    discount_amount = subtotal * (discount_percentage / 100.0)
    discounted_subtotal = subtotal - discount_amount
    tax_amount = discounted_subtotal * (tax_percentage / 100.0)
    final_total = discounted_subtotal + tax_amount
    
    breakdown = {
        "unit_price": f"${base_price:,.2f}",
        "quantity": quantity,
        "raw_subtotal": f"${subtotal:,.2f}",
        "applied_discount_rate": f"{discount_percentage}%",
        "discount_savings": f"${discount_amount:,.2f}",
        "taxable_amount": f"${discounted_subtotal:,.2f}",
        "tax_rate": f"{tax_percentage}%",
        "tax_amount": f"${tax_amount:,.2f}",
        "final_invoice_total": f"${final_total:,.2f}"
    }
    
    return json.dumps(breakdown, indent=2)

# List of tools
tools = [calculate_product_pricing]

# ── 2. Run the Live Agent ─────────────────────────────────────────────────────

def run_live_agent():
    print("Constructing live agent using create_agent()...")
    
    agent = create_agent(
        model="deepseek:deepseek-chat",
        tools=tools,
        system_prompt="You are an invoice and pricing agent. Calculate accurate invoice totals for users using the tools provided. Never guess numbers."
    )
    
    print("\n\033[92m✓ Live ReAct Agent is ready!\033[0m")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 72)
    print("\nTry queries like:")
    print("  → Calculate the final price for a bulk order of 15 laptop stands. The base price is $45 each. Since they are buying in bulk, give them a 12% discount. The sales tax is 6%.\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "Calculate the final price for a bulk order of 15 laptop stands. The base price is $45 each. Since they are buying in bulk, give them a 12% discount. The sales tax is 6%."
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
                        print(f"  🏁 \033[92m[FINAL RESPONSE]\033[0m →\n{msg.content}")
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
    print("  → Calculate the final price for a bulk order of 15 laptop stands. The base price is $45 each. Since they are buying in bulk, give them a 12% discount. The sales tax is 6%.\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "Calculate the final price for a bulk order of 15 laptop stands. The base price is $45 each. Since they are buying in bulk, give them a 12% discount. The sales tax is 6%."
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
        
        if "15" in user_input and "45" in user_input:
            args = {
                "base_price": 45.0,
                "quantity": 15,
                "discount_percentage": 12.0,
                "tax_percentage": 6.0
            }
            
            print(f"  🧠 \033[93m[THINK/ACT]\033[0m → calling calculate_product_pricing({args})")
            time.sleep(0.6)
            
            observation = calculate_product_pricing.invoke(args)
            print(f"  👁️ \033[96m[OBSERVE]\033[0m → {observation}")
            time.sleep(0.8)
            
            final_output = (
                "The bulk order pricing breakdown for 15 laptop stands at $45 each is as follows:\n\n"
                "- **Subtotal**: $675.00\n"
                "- **Discount (12% off)**: -$81.00\n"
                "- **Taxable Total**: $594.00\n"
                "- **Sales Tax (6%)**: $35.64\n"
                "- **Final Net Total**: **$629.64**"
            )
            
            print(f"  🏁 \033[92m[FINAL RESPONSE]\033[0m →\n{final_output}\n")
        else:
            print("  🧠 \033[93m[THINK/ACT]\033[0m → (Simulated thought: The user query is processed using calculate_product_pricing.)")
            time.sleep(0.5)
            print("  🏁 \033[92m[FINAL RESPONSE]\033[0m → [Simulation Mode] This is a mock response. Please add a valid DEEPSEEK_API_KEY to your .env file to enable live execution for all queries.\n")
            
        if is_non_interactive:
            break

# ── 4. Main Entry Point ───────────────────────────────────────────────────────

def main():
    print_banner("06 — CUSTOM TOOL DESIGN & INPUT VALIDATION")
    
    # 🔍 Pedagogy check: Let's inspect the generated argument schema!
    print("Let's look at the parameters schema LangChain compiled from our Python code:")
    print(f"Tool Name        : {calculate_product_pricing.name}")
    print(f"Tool Description : {calculate_product_pricing.description}")
    print("Arguments Schema (derived from type hints):")
    print(json.dumps(calculate_product_pricing.args, indent=2))
    print("=" * 72)
    
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
