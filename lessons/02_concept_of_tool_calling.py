"""
02_concept_of_tool_calling.py
==================================================
Concept: Tool Selection & JSON Schema Tool Calling

In Lesson 01, we saw that raw LLMs fail at precise arithmetic. We solved it by 
writing a native Python function. But how does an LLM actually interact with Python?

This is called **Tool Calling**. 

Instead of generating a conversational text response, the LLM generates a structured 
JSON request indicating:
1. Which function (tool) it wants to execute.
2. What arguments it wants to pass to that function.

In this lesson, we will:
1. Define a basic math `calculate` tool using LangChain's `@tool` decorator.
2. Bind this tool to ChatDeepSeek using `.bind_tools()`.
3. Submit a math question to the LLM and inspect the model's response.
4. **CRITICAL WARNING:** We will prove that tool calling does NOT execute any Python code! 
   It is purely a JSON selection and argument generator (routing mechanism).
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
from utils import get_llm, print_banner
from langchain_core.tools import tool

# ── 1. Define a basic Python tool ─────────────────────────────────────────────

@tool
def calculate(expression: str) -> str:
    """Evaluate any mathematical expression precisely. Use this for arithmetic queries."""
    # This is a basic mathematical evaluator
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


import os

def run_live_tool_call(llm, query: str):
    # 2. Bind the tool to the LLM
    # Binding compiles our Python `calculate` function's signature, docstring, and type hints
    # into a standard JSON Schema which is injected into the LLM's system environment.
    print("Binding the 'calculate' tool to the model...")
    llm_with_tools = llm.bind_tools([calculate])

    print(f"\nUser Query: '{query}'")
    print("Sending prompt to LLM...")

    # We invoke the LLM with tools bound
    response = llm_with_tools.invoke(query)

    print("\n--- LLM Response Inspection ---")
    
    # 4. Check if LLM requested a Tool Call
    # If tools are bound, the LLM intercepts the prompt and outputs a structured .tool_calls parameter!
    if response.tool_calls:
        print("\033[92mSuccess! The LLM generated a tool call request:\033[0m")
        
        # Access the first tool call requested
        tool_call = response.tool_calls[0]
        
        print(f"  → Name of requested tool : '{tool_call['name']}'")
        print(f"  → Arguments generated    : {tool_call['args']}")
        print(f"  → Unique Tool ID         : '{tool_call['id']}'")
        print("\nRaw .tool_calls JSON returned by LLM:")
        print(json.dumps(response.tool_calls, indent=2))
        
    else:
        print("\nLLM did not request a tool call. Response content:")
        print(response.content)

def run_simulated_tool_call(query: str):
    print("\n\033[93m⚠️ DEEPSEEK_API_KEY not configured or empty. Running simulation mode...\033[0m")
    print("Binding the 'calculate' tool to the model...")
    time.sleep(0.5)
    print("  → Python function 'calculate' converted to JSON Schema tool definition.")
    
    print(f"\nUser Query: '{query}'")
    print("Sending prompt to LLM...")
    time.sleep(0.8)

    print("\n--- LLM Response Inspection ---")
    print("\033[92mSuccess! The LLM generated a tool call request:\033[0m")
    
    simulated_tool_calls = [
        {
            "name": "calculate",
            "args": {
                "expression": "347 * 86"
            },
            "id": "call_abc123xyz789",
            "type": "tool_call"
        }
    ]
    
    tool_call = simulated_tool_calls[0]
    print(f"  → Name of requested tool : '{tool_call['name']}'")
    print(f"  → Arguments generated    : {tool_call['args']}")
    print(f"  → Unique Tool ID         : '{tool_call['id']}'")
    print("\nRaw .tool_calls JSON returned by LLM:")
    print(json.dumps(simulated_tool_calls, indent=2))

def main():
    print_banner("02 — THE CONCEPT OF TOOL CALLING")
    
    query = "What is 347 multiplied by 86?"
    
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or "your_deepseek" in api_key.lower():
        run_simulated_tool_call(query)
    else:
        try:
            # 1. Initialize the LLM
            print("Initializing ChatDeepSeek...")
            llm = get_llm(temperature=0.0)
            run_live_tool_call(llm, query)
        except Exception as e:
            print(f"\nError running live tool call: {e}")
            run_simulated_tool_call(query)

    print("=" * 72)
    print("\n--- ⚠️ CRITICAL LESSON FOR STUDENTS ---")
    print("\033[91;1mDID THE PYTHON FUNCTION EXECUTE? NO!\033[0m")
    print("Look at the terminal. You do not see any calculation output from Python.")
    print("Tool calling is purely **declarative**:")
    print("  - The LLM only says: *'I would like to run the function 'calculate' with args {'expression': '347 * 86'}'.*")
    print("  - It is the **Developer's job (Python Code)** to intercept this JSON request, ")
    print("    execute the actual Python function, and feed the result back to the model.")
    print("\nThis single selection-then-execution is called **Routing**.")
    print("But what happens if a task requires **multiple, dependent steps**?")
    print("That is where we need a **ReAct Loop**! Let's explore why in Lesson 03.")
    print("=" * 72)

if __name__ == "__main__":
    import time
    main()
