from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Core imports
from app.core.config import is_live_mode_available
from app.core.agent import initialize_agent
from app.core.tracer import parse_agent_trace

# Tools imports
from app.tools.math_tools import calculate, divide, calculate_discount, calculate_gst, calculate_product_pricing
from app.tools.api_tools import geocode_location, get_weather_forecast, google_search
from app.tools.db_tools import query_products_database

# LangChain message structures
from langchain_core.messages import HumanMessage, AIMessage

# Define all Capstone Tools
CAPSTONE_TOOLS = [
    calculate,
    divide,
    calculate_discount,
    calculate_gst,
    calculate_product_pricing,
    geocode_location,
    get_weather_forecast,
    google_search,
    query_products_database
]

# Initialize LangChain ReAct Agent
LIVE_AGENT = initialize_agent(CAPSTONE_TOOLS) if is_live_mode_available() else None

# Router Setup
router = APIRouter(prefix="/api", tags=["Conversational Agent"])

# Pydantic schemas
class ChatMessage(BaseModel):
    message: str
    history: List[List[str]] = []
    live: bool = False

# Hardcoded high-fidelity simulator databases
SIMULATED_PRESETS = {
    "which products in the database have a price greater than $200?": {
        "final_response": "Here are the premium items in stock costing more than $200:\n\n1. **Bamboo Standing Desk** - $599.00 (15 in stock)\n2. **UltraWide 34-inch Monitor** - $499.00 (20 in stock)\n3. **Noise-Cancelling Headphones** - $299.99 (35 in stock)\n4. **Ergonomic Desk Chair** - $249.99 (45 in stock)",
        "steps": [
            {
                "thought": "The user is asking for product details from our SQLite database where price is greater than $200. I will construct a secure, read-only SQL query to retrieve these items.",
                "tool_name": "query_products_database",
                "args": {"sql_query": "SELECT name, price, stock FROM products WHERE price > 200 ORDER BY price DESC"},
                "observation": '[{"name": "Bamboo Standing Desk", "price": 599.0, "stock": 15}, {"name": "UltraWide 34-inch Monitor", "price": 499.0, "stock": 20}, {"name": "Noise-Cancelling Headphones", "price": 299.99, "stock": 35}, {"name": "Ergonomic Desk Chair", "price": 249.99, "stock": 45}]'
            }
        ]
    },
    "i am traveling to tokyo. check if it's raining and tell me what to bring!": {
        "final_response": "Current conditions in **Tokyo** report a temperature of **16.8°C** with **Slight Rain**.\nSince it is raining, you should definitely carry an **umbrella** today!",
        "steps": [
            {
                "thought": "The user wants weather recommendations for Tokyo. First, I need to look up Tokyo's latitude and longitude using coordinates.",
                "tool_name": "geocode_location",
                "args": {"city_name": "Tokyo"},
                "observation": '{"latitude": 35.6895, "longitude": 139.6917, "city": "Tokyo", "country": "Japan"}'
            },
            {
                "thought": "Now that I have Tokyo's coordinates (35.6895, 139.6917), I can request the current weather forecast details.",
                "tool_name": "get_weather_forecast",
                "args": {"latitude": 35.6895, "longitude": 139.6917},
                "observation": '{"temperature": "16.8\u00b0C", "windspeed": "12.4 km/h", "weather_code": 61, "description": "Slight Rain", "is_raining": true}'
            }
        ]
    },
    "what is the final invoice for 12 desk chairs at $249.99 each with a 15% discount and 8% tax?": {
        "final_response": "Here is the invoice breakdown for **12 Ergonomic Desk Chairs** at **$249.99** each:\n\n*   **Raw Subtotal**: $2,999.88\n*   **15% Bulk Discount**: -$449.98\n*   **Taxable Subtotal**: $2,549.90\n*   **Sales Tax (8%)**: +$203.99\n*   **Final Invoice Total**: **$2,753.89**",
        "steps": [
            {
                "thought": "The user wants an invoice breakdown with discount and sales tax. I should use the product pricing calculator.",
                "tool_name": "calculate_product_pricing",
                "args": {"base_price": 249.99, "quantity": 12, "discount_percentage": 15.0, "tax_percentage": 8.0},
                "observation": '{\n  "unit_price": "$249.99",\n  "quantity": 12,\n  "raw_subtotal": "$2,999.88",\n  "applied_discount_rate": "15.0%",\n  "discount_savings": "$449.98",\n  "taxable_amount": "$2,549.90",\n  "tax_rate": "8.0%",\n  "tax_amount": "$203.99",\n  "final_invoice_total": "$2,753.89"\n}'
            }
        ]
    }
}

@router.get("/db-schema")
def get_db_schema():
    """Retrieve standard SQLite database schema definitions for products catalog."""
    schema = (
        "Table: products\n"
        "Columns:\n"
        "  - id: INTEGER (Primary Key)\n"
        "  - name: TEXT (Product Name)\n"
        "  - category: TEXT (Category e.g. Furniture, Electronics)\n"
        "  - price: REAL (Retail Price in USD)\n"
        "  - stock: INTEGER (Available inventory)"
    )
    columns = ["id", "name", "category", "price", "stock"]
    return {"schema": schema, "columns": columns}

@router.post("/chat")
async def chat_interaction(payload: ChatMessage):
    """Invoke the ReAct agent graph or return simulation loops."""
    query = payload.message.strip()
    
    # ── CASE A: Interactive Simulator ──
    if not payload.live or not LIVE_AGENT:
        lookup_key = query.lower().rstrip("?")
        
        matched_preset = None
        for key in SIMULATED_PRESETS:
            if key in lookup_key:
                matched_preset = SIMULATED_PRESETS[key]
                break
                
        if matched_preset:
            return {
                "steps": matched_preset["steps"],
                "final_response": matched_preset["final_response"],
                "simulated": True
            }
        else:
            no_match_text = (
                "Hi! I am currently running in **Simulation Demo Mode**.\n\n"
                "Please ask one of these three pre-coded scenarios to see the full ReAct loop in action:\n"
                "1. *'Which products in the database have a price greater than $200?'* (SQLite tool)\n"
                "2. *'I am traveling to Tokyo. Check if it's raining and tell me what to bring!'* (API tool chaining)\n"
                "3. *'What is the final invoice for 12 desk chairs at $249.99 each with a 15% discount and 8% tax?'* (Pricing tool)"
            )
            sim_steps = [
                {
                    "thought": "User query did not match a pre-coded scenario. Formatting educational fallback message.",
                    "tool_name": "system_fallback_formatter",
                    "args": {"message": query},
                    "observation": "System fallback triggered."
                }
            ]
            return {
                "steps": sim_steps,
                "final_response": no_match_text,
                "simulated": True
            }

    # ── CASE B: Live DeepSeek Agent ──
    else:
        try:
            formatted_history = []
            for h in payload.history:
                if len(h) >= 2:
                    formatted_history.append(HumanMessage(content=h[0]))
                    formatted_history.append(AIMessage(content=h[1]))
            
            result = LIVE_AGENT.invoke({
                "messages": formatted_history + [HumanMessage(content=query)]
            })
            
            trace_info = parse_agent_trace(result.get("messages", []))
            
            return {
                "steps": trace_info["steps"],
                "final_response": trace_info["final_response"] or "No conversational response returned by agent.",
                "simulated": False
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"DeepSeek Agent Invocation Error: {e}")
