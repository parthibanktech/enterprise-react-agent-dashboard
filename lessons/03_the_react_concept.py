"""
03_the_react_concept.py
==================================================
Concept: Why Routing is Not Enough & The ReAct Paradigm

In Lesson 02, we saw how an LLM makes a Tool Call by outputting a JSON schema 
request (e.g. `calculate(expression="347 * 86")`).

This simple selection and argument formatting is called **Routing**. 
Routing is perfect for single-step lookups. But what happens when you ask:
> "What is 347 multiplied by 86, and what is that result divided by 5?"

A single-turn router hits a wall because the LLM cannot write the arguments 
for the division tool until it knows the outcome of the multiplication!

This is where the **ReAct (Reasoning & Acting)** paradigm comes in.
It enables sequential, multi-turn reasoning loops.

This runnable script provides a clear, conceptual visualization of the ReAct flow.
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
from utils import print_banner

def print_slow(text: str, delay: float = 0.02):
    """Print text with a slight delay for a nice interactive reading experience."""
    for line in text.splitlines():
        print(line)
        time.sleep(delay)

def display_concept():
    print_slow("\n\033[1;36m💡 1. THE LIMIT OF SINGLE-TURN ROUTING\033[0m")
    print_slow(
        "If we only use simple routing, the agent immediately hits a wall:\n"
        "  - The LLM knows it needs to multiply 347 by 86.\n"
        "  - The LLM also knows it needs to divide that result by 5.\n"
        "  - \033[91mThe Problem:\033[0m The LLM cannot write the arguments for the division tool\n"
        "    because it does not yet know the outcome of the multiplication!\n"
        "  - An LLM is not a compiler or calculator; it cannot guess the intermediate result\n"
        "    (29842) inside its own static weights.\n\n"
        "Therefore, we cannot solve this in a single turn. The LLM must:\n"
        "  1. Call the multiplication tool first.\n"
        "  2. Wait for Python to execute it.\n"
        "  3. Read the resulting observation (29842).\n"
        "  4. Use that observation to formulate the division query (29842 / 5).\n"
        "  5. Execute the division tool.\n"
        "  6. Formulate the final answer."
    )
    time.sleep(1.0)

    print_slow("\n\033[1;36m🔄 2. THE ReAct PARADIGM (Reasoning and Acting)\033[0m")
    print_slow(
        "Introduced by Yao et al. (2022), ReAct describes how an agent uses a loop to\n"
        "interleave reasoning traces (thoughts) and task-specific actions (tool calls).\n"
    )

    diagram = """
                       ┌──────────────────────┐
                       │      User Query      │
                       └──────────┬───────────┘
                                  │
                                  ▼
                     ┌──────────────────────────┐
                 ┌──>│  THINK (Reasoning Step)  │
                 │   └────────────┬─────────────┘
                 │                │
                 │                ▼
                 │   ┌──────────────────────────┐
                 │   │    ACT (Call Python/API) │
                 │   └────────────┬─────────────┘
                 │                │
                 │                ▼
                 │   ┌──────────────────────────┐
                 │   │  OBSERVE (Tool Output)   │
                 │   └────────────┬─────────────┘
                 │                │
                 └────────────────┘ (Repeat until done)
                                  │
                                  ▼
                     ┌──────────────────────────┐
                     │      FINAL RESPONSE      │
                     └──────────────────────────┘
    """
    print_slow(diagram, delay=0.01)
    time.sleep(1.0)

def simulate_react_loop():
    print_slow("\n\033[1;35m🎬 INTERACTIVE SIMULATION: Watch the ReAct Loop in Action!\033[0m")
    print_slow("Query: 'What is 347 multiplied by 86, and what is that result divided by 5?'\n")
    time.sleep(1.0)

    # Cycle 1
    print("\033[1;34m--- ReAct Cycle 1 ---\033[0m")
    time.sleep(0.5)
    print("🧠 \033[93m[THINK] Thoughts:\033[0m")
    print("  \"The user wants to multiply 347 by 86, and then divide that result by 5.")
    print("   First, I need to compute the multiplication. I should call the 'calculate' tool.\"")
    time.sleep(1.0)
    print("🎬 \033[92m[ACT] Action:\033[0m")
    print("  Call tool 'calculate' with argument: {\"expression\": \"347 * 86\"}")
    time.sleep(1.0)
    print("👁️ \033[96m[OBSERVE] Observation:\033[0m")
    print("  Tool returned: \"29842\"")
    print("-" * 50)
    time.sleep(1.5)

    # Cycle 2
    print("\033[1;34m--- ReAct Cycle 2 ---\033[0m")
    time.sleep(0.5)
    print("🧠 \033[93m[THINK] Thoughts:\033[0m")
    print("  \"The multiplication result is 29842. Now I must divide this number by 5.")
    print("   I will call the 'calculate' tool again with this expression.\"")
    time.sleep(1.0)
    print("🎬 \033[92m[ACT] Action:\033[0m")
    print("  Call tool 'calculate' with argument: {\"expression\": \"29842 / 5\"}")
    time.sleep(1.0)
    print("👁️ \033[96m[OBSERVE] Observation:\033[0m")
    print("  Tool returned: \"5968.4\"")
    print("-" * 50)
    time.sleep(1.5)

    # Cycle 3
    print("\033[1;34m--- ReAct Cycle 3 ---\033[0m")
    time.sleep(0.5)
    print("🧠 \033[93m[THINK] Thoughts:\033[0m")
    print("  \"I have successfully multiplied 347 by 86 to get 29842, and divided it by 5 to get 5968.4.")
    print("   I have all the information required. I can now answer the user.\"")
    time.sleep(1.0)
    print("\n🏁 \033[92m[FINAL RESPONSE] Final Answer:\033[0m")
    print("  \"The result of multiplying 347 by 86 is 29,842. Dividing that result by 5 gives 5,968.4.\"")
    print("=" * 72)
    time.sleep(1.0)

    print_slow(
        "\n\033[1;32m🎉 Up Next! \033[0m\n"
        "In \033[1mLesson 04\033[0m, we will write a raw Python `while` loop that does exactly this!\n"
        "We'll manage message memory and handle actual/simulated tool calling step-by-step.\n"
    )

def main():
    print_banner("03 — THE REACT CONCEPT (WHY ROUTING IS NOT ENOUGH)")
    display_concept()
    simulate_react_loop()

if __name__ == "__main__":
    main()
