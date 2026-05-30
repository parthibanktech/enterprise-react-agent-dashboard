"""
01_why_llms_need_tools.py
==========================================
Concept: The Limitations of Raw LLMs

Large Language Models (LLMs) are incredibly powerful, but they have major limitations:
1. They cannot perform complex mathematical calculations reliably (they predict the next token instead of calculating).
2. They do not have access to real-time information (e.g., today's date, live weather, or current news) beyond their training cutoff.
3. They cannot interact with external systems (e.g., databases, local file systems, or Web APIs) on their own.

This script demonstrates these limitations by asking DeepSeek to solve a math problem and retrieve today's date.
Then, it shows how simple Python functions act as "Tools" that solve these problems.
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

from utils import get_llm, print_banner
from datetime import date

def run_live_challenges(llm):
    # ────────────────────────────────────────────────────────────────────────
    # CHALLENGE 1: Precise Math Calculation
    # ────────────────────────────────────────────────────────────────────────
    math_prompt = "What is 347 * 86 * 19?"
    print("\n--- Challenge 1: Precise Math Calculation ---")
    print(f"User Question: '{math_prompt}'")
    print("Calling raw LLM (no tools)...")
    
    response_math = llm.invoke(math_prompt)
    print(f"LLM Answer: {response_math.content.strip()}")
    
    # Let's see what the correct answer is
    correct_math = 347 * 86 * 19
    print(f"Correct Answer (via Python calculation): {correct_math}")
    print("--> Note how the LLM may get close or completely guess, but it cannot guarantee 100% precision.")

    # ────────────────────────────────────────────────────────────────────────
    # CHALLENGE 2: Real-time Information (Today's Date)
    # ────────────────────────────────────────────────────────────────────────
    date_prompt = "What is today's date?"
    print("\n--- Challenge 2: Real-time Information ---")
    print(f"User Question: '{date_prompt}'")
    print("Calling raw LLM (no tools)...")
    
    response_date = llm.invoke(date_prompt)
    print(f"LLM Answer: {response_date.content.strip()}")
    
    # Let's see what the correct date is
    correct_date = date.today().strftime("%B %d, %Y")
    print(f"Correct Answer (via System Clock): {correct_date}")
    print("--> Note how the LLM cannot know today's date because it has no clock or system access.")

def run_simulated_challenges():
    print("\n\033[93m⚠️ DEEPSEEK_API_KEY not configured or empty. Running simulation mode...\033[0m")
    
    # ────────────────────────────────────────────────────────────────────────
    # CHALLENGE 1: Precise Math Calculation (Simulated)
    # ────────────────────────────────────────────────────────────────────────
    math_prompt = "What is 347 * 86 * 19?"
    print("\n--- Challenge 1: Precise Math Calculation ---")
    print(f"User Question: '{math_prompt}'")
    print("Calling raw LLM (no tools)...")
    
    # Simulated next-token-prediction guess (an LLM often predicts close but wrong)
    simulated_guess = "567,143"  # Real calculation: 347 * 86 * 19 = 567002
    print(f"LLM Answer: 347 * 86 * 19 is equal to {simulated_guess}.")
    
    # Let's see what the correct answer is
    correct_math = 347 * 86 * 19
    print(f"Correct Answer (via Python calculation): {correct_math}")
    print("--> Note how the LLM may get close or completely guess, but it cannot guarantee 100% precision.")

    # ────────────────────────────────────────────────────────────────────────
    # CHALLENGE 2: Real-time Information (Today's Date) (Simulated)
    # ────────────────────────────────────────────────────────────────────────
    date_prompt = "What is today's date?"
    print("\n--- Challenge 2: Real-time Information ---")
    print(f"User Question: '{date_prompt}'")
    print("Calling raw LLM (no tools)...")
    
    simulated_date_response = (
        "I do not have access to real-time information or today's date. "
        "My knowledge is limited to my training cutoff."
    )
    print(f"LLM Answer: {simulated_date_response}")
    
    # Let's see what the correct date is
    correct_date = date.today().strftime("%B %d, %Y")
    print(f"Correct Answer (via System Clock): {correct_date}")
    print("--> Note how the LLM cannot know today's date because it has no clock or system access.")

def main():
    print_banner("01 — WHY LLMS NEED TOOLS")
    
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or "your_deepseek" in api_key.lower():
        run_simulated_challenges()
    else:
        try:
            print("Initializing ChatDeepSeek...")
            llm = get_llm(temperature=0.0)
            run_live_challenges(llm)
        except Exception as e:
            print(f"\nError running live challenges: {e}")
            run_simulated_challenges()

    # ────────────────────────────────────────────────────────────────────────
    # THE SOLUTION: Python Functions as Tools
    # ────────────────────────────────────────────────────────────────────────
    print("\n--- The Solution: Python Functions ---")
    print("By giving the LLM the ability to invoke Python functions, we extend its power!")
    print("Python functions can calculate exactly, read the system clock, query a DB, or hit an API.")
    print("In the next script, we will see how the LLM decides WHEN to use these functions using the ReAct loop.")
    print("=" * 72)

if __name__ == "__main__":
    main()
