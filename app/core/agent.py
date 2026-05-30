from langchain.agents import create_agent

def get_agent_system_prompt() -> str:
    """Return the structured instruction guidelines for our resilient ReAct Agent."""
    return (
        "You are an enterprise business intelligence analyst agent. You have access to a suite of "
        "production tools including a mathematical calculator, an API-driven search/weather tool, and an SQLite database.\n\n"
        "DATABASE SCHEMA:\n"
        "Table: products\n"
        "Columns:\n"
        "  - id: INTEGER (Primary Key)\n"
        "  - name: TEXT (Product Name)\n"
        "  - category: TEXT (Category e.g. Furniture, Electronics)\n"
        "  - price: REAL (Retail Price in USD)\n"
        "  - stock: INTEGER (Available inventory)\n\n"
        "GUIDELINES:\n"
        "1. To answer database questions, generate a secure, valid SQLite SELECT query and run it via the database tool.\n"
        "2. If you get a database error (e.g. column spelling error like 'pric'), read the error message, correct your SQL, and retry the call immediately. Do not crash!\n"
        "3. Use division and custom calculation tools to evaluate complex mathematical formulas precisely. Never guess numbers.\n"
        "4. If a calculation is mathematically impossible (like dividing by zero), state this limitation clearly to the user.\n"
        "5. Be concise and summarize the final answers cleanly using tables or lists."
    )

def initialize_agent(tools: list):
    """
    Compile Parthiban's unified create_agent graph using the provided set of tools.
    
    Args:
        tools: A list of @tool-decorated functions the agent can utilize.
    Returns:
        A compiled LangChain Runnable agent.
    """
    prompt = get_agent_system_prompt()
    
    # create_agent compiles the agent's graph under the hood
    agent = create_agent(
        model="deepseek:deepseek-chat",
        tools=tools,
        system_prompt=prompt
    )
    return agent
