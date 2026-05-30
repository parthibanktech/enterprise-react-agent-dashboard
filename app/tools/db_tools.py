import sqlite3
import json
from langchain_core.tools import tool
from app.core.config import DB_PATH

@tool
def query_products_database(sql_query: str) -> str:
    """Execute a read-only SQL SELECT query on the products database and return the rows.
    
    Use this tool whenever a question asks about product listings, inventory, pricing, 
    categories, or counts.
    
    Args:
        sql_query: A valid SQLite SELECT statement (e.g. 'SELECT name FROM products WHERE price > 100').
    """
    print(f"[SQL Tool] Executing SQL Query: '{sql_query.strip()}'...")
    
    # Crucial Security Hardening: Guard against write mutations!
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
