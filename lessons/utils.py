import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
load_dotenv()
def require_env(name):
    v=os.getenv(name)
    if not v: raise RuntimeError(f"Missing {name}. Add it to .env")
    return v
def get_llm(temperature=0.2,max_tokens=800):
    require_env("DEEPSEEK_API_KEY")
    return ChatDeepSeek(model="deepseek-chat",temperature=temperature,max_tokens=max_tokens)
def print_banner(title):
    print("="*72); print(title); print("="*72)
def print_trace(result):
    for m in result.get("messages",[]):
        n=m.__class__.__name__
        if n=="AIMessage" and getattr(m,"tool_calls",None):
            for c in m.tool_calls: print(f"THINK -> {c.get('name')}({c.get('args')})")
        elif n=="AIMessage" and m.content: print("ANSWER ->",m.content)
        elif n=="ToolMessage": print("OBSERVE ->",m.content[:240])
