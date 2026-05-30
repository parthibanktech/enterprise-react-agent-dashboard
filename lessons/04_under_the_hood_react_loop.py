"""
04_under_the_hood_react_loop.py
==================================================
Concept: Under the Hood of a ReAct Reasoning Loop

In Lesson 03, we learned the theory behind the ReAct paradigm (THINK ➔ ACT ➔ OBSERVE).
Now, we will write a raw, framework-free Python `while` loop to see exactly how 
ReAct is orchestrated under the hood.

We will:
1. Maintain a list of `messages` (the agent's short-term memory).
2. Invoke the LLM inside a `while` loop to get the next action (THINK).
3. If the LLM generates a tool call request, we parse the JSON payload (ACT).
4. We execute the local Python function and capture the output (OBSERVE).
5. We wrap the result in a `ToolMessage` and append it to our message history.
6. We loop back to the LLM. It sees the history, reflects, and decides the next step!

*Note: If no valid DeepSeek API key is present in .env, this script will run a 
high-fidelity simulation to demonstrate the exact trace of the ReAct memory structure.*
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
from langchain_deepseek import ChatDeepSeek

# ── 1. Define Our Math Tool ───────────────────────────────────────────────────

@tool
def calculate(expression: str) -> str:
    """Evaluate any mathematical expression precisely. Use this for arithmetic queries."""
    try:
        # Safe mathematical evaluation
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

# Tool registry to map tool names to Python functions
TOOL_MAP = {
    "calculate": calculate
}

# ── 2. Run the Live ReAct Loop ─────────────────────────────────────────────────

def run_live_react_loop(llm, prompt: str):
    print(f"\n[USER PROMPT] : {prompt}")
    print("=" * 72)
    
    # Bind tools to the model
    llm_with_tools = llm.bind_tools([calculate])
    
    # 1. Short-term Memory: List of messages in the chat history
    messages = [HumanMessage(content=prompt)]
    
    step = 1
    max_steps = 5  # Infinite loop prevention
    
    while step <= max_steps:
        print(f"\n\033[1;34m--- ReAct Cycle {step} ---\033[0m")
        print("🧠 \033[93m[THINK] LLM is reasoning over the history...\033[0m")
        
        # Invoke the model with the entire history of actions & observations
        response = llm_with_tools.invoke(messages)
        
        # Append LLM's thought/action response to history
        messages.append(response)
        
        # Print LLM's internal thinking content if any
        if response.content:
            print(f"  → Thoughts: {response.content.strip()}")
            
        # Check if the LLM wants to perform an ACTION (Tool Call)
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                print(f"🎬 \033[92m[ACT] LLM requests tool call:\033[0m")
                print(f"  → Tool     : {tool_name}")
                print(f"  → Arguments: {tool_args}")
                print(f"  → Tool ID  : {tool_id}")
                
                # Execute the corresponding Python function
                if tool_name in TOOL_MAP:
                    print(f"⚡ Running local Python function '{tool_name}'...")
                    observation = TOOL_MAP[tool_name].invoke(tool_args)
                else:
                    observation = f"Error: Tool '{tool_name}' not found."
                
                print(f"👁️ \033[96m[OBSERVE] Tool output returned to Python:\033[0m")
                print(f"  → Observation: {observation}")
                
                # Create a ToolMessage containing the output and link it using tool_call_id
                tool_message = ToolMessage(
                    content=str(observation),
                    tool_call_id=tool_id,
                    name=tool_name
                )
                
                # Append the observation back to the agent's memory
                messages.append(tool_message)
        else:
            # No tool calls requested! This means the agent has reached a conclusion.
            print("\n🏁 \033[92m[FINAL RESPONSE] Agent is done!\033[0m")
            print(f"Result: {response.content.strip()}")
            break
            
        step += 1
        time.sleep(1.0)
    else:
        print("\n⚠️ Agent terminated because it exceeded the maximum ReAct step limit.")

# ── 3. High-Fidelity Simulation Mode ──────────────────────────────────────────

def run_simulated_react_loop(prompt: str):
    print("\n\033[93m⚠️ DEEPSEEK_API_KEY not configured or empty. Running simulation mode...\033[0m")
    print(f"\n[USER PROMPT] : {prompt}")
    print("=" * 72)
    
    # Mimic the list of messages in short term memory
    messages = []
    
    # Step 1: User Prompt
    messages.append(HumanMessage(content=prompt))
    print("\n\033[1;34m--- ReAct Cycle 1 ---\033[0m")
    print("🧠 \033[93m[THINK] LLM is reasoning over history...\033[0m")
    time.sleep(0.5)
    print("  → Thoughts: The user wants to multiply 347 by 86, and then divide the result by 5. I should first calculate 347 * 86.")
    
    # Model generates Tool Call
    tool_call_1_id = "call_abc123"
    ai_response_1 = AIMessage(
        content="I will first calculate 347 * 86 to get the intermediate result.",
        tool_calls=[{
            "name": "calculate",
            "args": {"expression": "347 * 86"},
            "id": tool_call_1_id
        }]
    )
    messages.append(ai_response_1)
    
    print("🎬 \033[92m[ACT] LLM requests tool call:\033[0m")
    print(f"  → Tool     : calculate")
    print(f"  → Arguments: {{'expression': '347 * 86'}}")
    print(f"  → Tool ID  : {tool_call_1_id}")
    time.sleep(0.5)
    
    # Execute Python function
    observation_1 = calculate.invoke({"expression": "347 * 86"})
    print("⚡ Running local Python function 'calculate'...")
    print(f"👁️ \033[96m[OBSERVE] Tool output returned to Python:\033[0m")
    print(f"  → Observation: {observation_1}")
    
    # Add observation to messages
    tool_msg_1 = ToolMessage(content=observation_1, tool_call_id=tool_call_1_id, name="calculate")
    messages.append(tool_msg_1)
    
    # Cycle 2
    time.sleep(0.8)
    print("\n\033[1;34m--- ReAct Cycle 2 ---\033[0m")
    print("🧠 \033[93m[THINK] LLM is reasoning over history...\033[0m")
    print(f"  → Messages in History: {len(messages)} messages (1 user, 1 AI thought/action, 1 tool observation)")
    time.sleep(0.5)
    print(f"  → Thoughts: The result of 347 * 86 is {observation_1}. Now I need to divide this result by 5.")
    
    tool_call_2_id = "call_xyz789"
    ai_response_2 = AIMessage(
        content=f"The result is {observation_1}. Now I will divide {observation_1} by 5.",
        tool_calls=[{
            "name": "calculate",
            "args": {"expression": f"{observation_1} / 5"},
            "id": tool_call_2_id
        }]
    )
    messages.append(ai_response_2)
    
    print("🎬 \033[92m[ACT] LLM requests tool call:\033[0m")
    print(f"  → Tool     : calculate")
    print(f"  → Arguments: {{'expression': '{observation_1} / 5'}}")
    print(f"  → Tool ID  : {tool_call_2_id}")
    time.sleep(0.5)
    
    # Execute Python function
    observation_2 = calculate.invoke({"expression": f"{observation_1} / 5"})
    print("⚡ Running local Python function 'calculate'...")
    print(f"👁️ \033[96m[OBSERVE] Tool output returned to Python:\033[0m")
    print(f"  → Observation: {observation_2}")
    
    # Add observation to messages
    tool_msg_2 = ToolMessage(content=observation_2, tool_call_id=tool_call_2_id, name="calculate")
    messages.append(tool_msg_2)
    
    # Cycle 3
    time.sleep(0.8)
    print("\n\033[1;34m--- ReAct Cycle 3 ---\033[0m")
    print("🧠 \033[93m[THINK] LLM is reasoning over history...\033[0m")
    time.sleep(0.5)
    print("  → Thoughts: I have successfully calculated the result. 347 * 86 = 29842, and 29842 / 5 = 5968.4. I can now formulate my final response.")
    
    final_response = AIMessage(
        content=f"The result of multiplying 347 by 86 is 29,842. Dividing that result by 5 gives 5,968.4."
    )
    messages.append(final_response)
    
    print("\n🏁 \033[92m[FINAL RESPONSE] Agent is done!\033[0m")
    print(f"Result: {final_response.content}")
    print("=" * 72)
    
    # Dump the message chain so students can inspect the structure
    print("\n🔍 --- Short-term Memory Inspection ---")
    print("Here is the exact message sequence that was compiled in memory during this run:")
    for idx, msg in enumerate(messages, 1):
        print(f"\nMessage {idx}: {msg.__class__.__name__}")
        if isinstance(msg, AIMessage) and msg.tool_calls:
            print(f"  -> Content: {msg.content}")
            print(f"  -> Tool Calls: {json.dumps(msg.tool_calls, indent=2)}")
        elif isinstance(msg, ToolMessage):
            print(f"  -> Tool Call ID: {msg.tool_call_id}")
            print(f"  -> Content: {msg.content}")
        else:
            print(f"  -> Content: {msg.content}")
    print("=" * 72)

# ── 4. Main Entry Point ───────────────────────────────────────────────────────

def main():
    print_banner("04 — UNDER THE HOOD: THE REACT LOOP")
    
    prompt = "What is 347 multiplied by 86, and then divide that result by 5?"
    
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    
    if not api_key or "your_deepseek" in api_key.lower():
        run_simulated_react_loop(prompt)
    else:
        try:
            llm = ChatDeepSeek(model="deepseek-chat", temperature=0.0)
            run_live_react_loop(llm, prompt)
        except Exception as e:
            print(f"\nError running live loop: {e}")
            run_simulated_react_loop(prompt)

if __name__ == "__main__":
    main()
