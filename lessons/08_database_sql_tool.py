"""
08_database_sql_tool.py
==================================================
Concept: Natural-Language-to-SQL (NL-to-SQL) & Database Tools

Enterprise AI agents are frequently asked to query databases to answer questions 
about inventory, users, or metrics. Instead of hardcoding API endpoints for every 
possible combination of questions, we can expose a **Database Query Tool**.

The ReAct loop operates like this:
1. **User asks**: "What products cost more than $200 and what is their inventory?"
2. **THINK**: The agent knows it needs to query the database. It reviews the schema.
3. **ACT**: Formulates a SQL query (`SELECT name, price, stock FROM products...`) 
   and calls the database tool.
4. **OBSERVE**: Receives the query results.
5. **THINK**: Summarizes the row metrics into a human-readable markdown response.

⚠️ **CRITICAL SECURITY NOTE FOR STUDENTS:**
Exposing a raw SQL execution database to an LLM is a major security risk. 
To prevent destructive SQL Injection or accidental write operations, your database 
tools must be **read-only** (SELECT-only) and perform validation on incoming strings!

In this lesson, we will:
1. Initialize and seed a local SQLite database (`mission2_products.sqlite`).
2. Build a read-hardened `query_products_database` tool that filters out mutation keywords.
3. Run the SQLite SQL-Agent inside Parthiban's unified ReAct `create_agent()` framework.

*Note: If no valid DeepSeek API key is present in .env, this script runs in 
Simulation Mode while still seeding the database locally so you can inspect it.*
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

import sqlite3
import json
import time
from dotenv import load_dotenv
from utils import print_banner
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent

DB_PATH = os.path.join(lessons_dir, "mission2_products.sqlite")

# ── 1. Database Seeding & Schema Lookup Helper ─────────────────────────────────

def seed_database():
    """Seed a local SQLite database with product information for consistent lessons."""
    print("📦 Initializing local SQLite database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL
    )
    """)
    
    # Check if table is already seeded
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        print("🌱 Seeding product catalog rows...")
        products = [
            ("Ergonomic Desk Chair", "Furniture", 249.99, 45),
            ("Mechanical Keyboard", "Electronics", 129.50, 80),
            ("UltraWide 34-inch Monitor", "Electronics", 499.00, 20),
            ("USB-C Hub Multiport", "Electronics", 39.99, 150),
            ("Noise-Cancelling Headphones", "Electronics", 299.99, 35),
            ("Bamboo Standing Desk", "Furniture", 599.00, 15),
            ("Wireless Ergonomic Mouse", "Electronics", 79.99, 110)
        ]
        cursor.executemany("INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)", products)
        conn.commit()
    conn.close()
    print("✅ Database ready.")

def get_database_schema() -> str:
    """Return the schema of the products table so the LLM knows how to write queries."""
    return """
    Table: products
    Columns:
      - id: INTEGER (Primary Key)
      - name: TEXT (Product Name)
      - category: TEXT (Category e.g. Furniture, Electronics)
      - price: REAL (Retail Price in USD)
      - stock: INTEGER (Available inventory)
    """

# ── 2. Read-Hardened Database Tool ─────────────────────────────────────────────

@tool
def query_products_database(sql_query: str) -> str:
    """
    Execute a read-only SQL SELECT query on the products database and return the rows.
    
    Use this tool whenever a question asks about product listings, inventory, pricing, 
    categories, or counts.
    
    Parameters:
    - sql_query: A valid SQLite SELECT statement (e.g. 'SELECT name FROM products WHERE price > 100').
    """
    print(f"📡 [SQL Tool] Executing SQL Query: '{sql_query.strip()}'...")
    
    # 🚨 Crucial Security Hardening: Guard against write mutations!
    forbidden_keywords = ["insert", "update", "delete", "drop", "create", "alter", "replace", "truncate"]
    query_lower = sql_query.lower()
    
    for kw in forbidden_keywords:
        if kw in query_lower:
            return f"Security Error: The keyword '{kw.upper()}' is forbidden. This tool is read-only (SELECT queries only)."
            
    # Connect and run query
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        # Capture column names for clean table formatting
        colnames = [desc[0] for desc in cursor.description]
        conn.close()
        
        if not rows:
            return "No matching rows found in the database."
            
        # Format results as structured JSON
        results = [dict(zip(colnames, row)) for row in rows]
        return json.dumps(results, indent=2)
        
    except sqlite3.Error as e:
        return f"Database SQLite Error: {e}"

# Register our tool
tools = [query_products_database]

# ── 3. Run the Live Agent ─────────────────────────────────────────────────────

def run_live_agent():
    print("Constructing live agent using create_agent()...")
    
    schema = get_database_schema()
    
    agent = create_agent(
        model="deepseek:deepseek-chat",
        tools=tools,
        system_prompt=(
            f"You are a database business analyst agent. You have access to a products database.\n"
            f"Here is the database schema:\n{schema}\n"
            f"Answer the user's questions by generating a valid, secure SELECT query "
            f"and executing it via the 'query_products_database' tool. Summarize the output in a nice table."
        )
    )
    
    print("\n\033[92m✓ Live ReAct NL-to-SQL Agent is ready!\033[0m")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 72)
    print("\nTry queries like:")
    print("  → Which products in the database have a price greater than $200? List their names, prices, and available quantities.\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "Which products in the database have a price greater than $200? List their names, prices, and available quantities."
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

        print("\n--- Starting ReAct NL-to-SQL Agent Loop ---\n")
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

# ── 4. High-Fidelity Simulation Mode ──────────────────────────────────────────

def run_simulated_agent():
    print("\n\033[93m⚠️ DEEPSEEK_API_KEY not configured or empty. Running simulation mode...\033[0m")
    print("Constructing agent using create_agent()...")
    time.sleep(0.5)
    print("\n\033[92m✓ Simulated ReAct Agent is ready!\033[0m")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 72)
    print("\nTry queries like:")
    print("  → Which products in the database have a price greater than $200? List their names, prices, and available quantities.\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "Which products in the database have a price greater than $200? List their names, prices, and available quantities."
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

        print("\n--- Starting ReAct NL-to-SQL Agent (Simulated) ---\n")
        
        if "200" in user_input:
            sql = "SELECT name, price, stock FROM products WHERE price > 200"
            print(f"  🧠 \033[93m[THINK/ACT]\033[0m → calling query_products_database({{'sql_query': '{sql}'}})")
            time.sleep(0.5)
            
            observation = query_products_database.invoke({"sql_query": sql})
            print(f"  👁️ \033[96m[OBSERVE]\033[0m → {observation}")
            time.sleep(0.8)
            
            final_output = (
                "Here are the products in the database with a price greater than $200:\n\n"
                "| Product Name | Price | Stock |\n"
                "|---|---|---|\n"
                "| Ergonomic Desk Chair | $249.99 | 45 |\n"
                "| UltraWide 34-inch Monitor | $499.00 | 20 |\n"
                "| Noise-Cancelling Headphones | $299.99 | 35 |\n"
                "| Bamboo Standing Desk | $599.00 | 15 |\n\n"
                "These four items are currently in stock and retail above $200."
            )
            
            print(f"  🏁 \033[92m[FINAL RESPONSE]\033[0m →\n{final_output}\n")
        else:
            print("  🧠 \033[93m[THINK/ACT]\033[0m → (Simulated thought: The user query is processed using SQL SELECT generation.)")
            time.sleep(0.5)
            print("  🏁 \033[92m[FINAL RESPONSE]\033[0m → [Simulation Mode] This is a mock response. Please add a valid DEEPSEEK_API_KEY to your .env file to enable live execution for all queries.\n")
            
        if is_non_interactive:
            break

# ── 5. Main Entry Point ───────────────────────────────────────────────────────

def main():
    print_banner("08 — DATABASE INTEGRATION & NATURAL-LANGUAGE-TO-SQL")
    
    # 1. Setup DB
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
