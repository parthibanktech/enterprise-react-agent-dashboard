import json
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def parse_agent_trace(messages: list) -> dict:
    """
    Parse a list of LangChain messages into structured trace steps and a final answer.
    
    Args:
        messages: A list of message objects returned in the agent result.
        
    Returns:
        A dictionary containing:
        - "steps": List of dicts representing each reasoning/tool execution step:
             { "thought": str, "tool_name": str, "args": dict, "observation": str }
        - "final_response": The final text answer produced by the agent.
    """
    parsed_steps = []
    final_response = ""
    
    current_step = {}
    
    for msg in messages:
        role = msg.__class__.__name__
        
        # 1. Thought / Tool Call Action
        if role == "AIMessage":
            # If the model is calling a tool
            if getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    # Clear out the current step's accumulated data to start fresh
                    current_step = {
                        "thought": msg.content or "Analyzing request and selecting tool...",
                        "tool_name": tc.get("name", "unknown_tool"),
                        "args": tc.get("args", {}),
                        "observation": None
                    }
            else:
                # This is the final response if there are no tool calls
                if msg.content:
                    final_response = msg.content
                    
        # 2. Tool Observation Result
        elif role == "ToolMessage":
            if current_step:
                current_step["observation"] = msg.content
                parsed_steps.append(current_step)
                current_step = {}  # Reset
            else:
                # Fallback if a tool message somehow appears without a preceding AIMessage tool call
                parsed_steps.append({
                    "thought": "Direct tool response received.",
                    "tool_name": getattr(msg, "name", "tool"),
                    "args": {},
                    "observation": msg.content
                })
                
    return {
        "steps": parsed_steps,
        "final_response": final_response
    }
