"""
07_api_driven_tools.py
==================================================
Concept: Multi-Step Web API Tool Integration inside ReAct

Real-world agents don't just solve mathematical questions. They fetch 
live information from external Web APIs. 

Often, a user query requires **sequential API chaining**:
*   *Prompt*: "I am traveling to Tokyo. Check the current weather and tell me if I need an umbrella or sunglasses."
*   *Step 1*: Get the latitude and longitude of "Tokyo" using a Geocoding API.
*   *Step 2*: Fetch the weather forecast for those coordinates using a Weather API.
*   *Step 3*: Analyze the weather state and make the final recommendation.

In this lesson, we will:
1. Define a `geocode_location` tool using the public, keyless Open-Meteo Geocoding API.
2. Define a `get_weather_forecast` tool using the public, keyless Open-Meteo Weather API.
3. Configure **offline mock fallbacks** so the code runs seamlessly even without an internet connection.
4. Execute both tools inside our unified ReAct `create_agent()` framework to solve the travel decision prompt!

*Note: If no valid DeepSeek API key is present in .env, this script will run a 
high-fidelity simulation of the multi-step API reasoning chain.*
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
import urllib.request
import urllib.parse
from dotenv import load_dotenv
from utils import print_banner
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent

# ── 1. Geocoding Tool with Offline Fallback ───────────────────────────────────

@tool
def geocode_location(city_name: str) -> str:
    """
    Look up the exact coordinates (latitude and longitude) for any city name.
    
    Parameters:
    - city_name: Name of the city (e.g. 'Tokyo', 'London', 'Paris').
    """
    clean_city = city_name.strip()
    print(f"📡 [Geocoding Tool] Searching for location: '{clean_city}'...")
    
    # Offline coordinates cache for resilience
    offline_db = {
        "tokyo": {"latitude": 35.6895, "longitude": 139.6917, "city": "Tokyo", "country": "Japan"},
        "london": {"latitude": 51.5074, "longitude": -0.1278, "city": "London", "country": "United Kingdom"},
        "paris": {"latitude": 48.8566, "longitude": 2.3522, "city": "Paris", "country": "France"},
        "new york": {"latitude": 40.7128, "longitude": -74.0060, "city": "New York", "country": "United States"}
    }
    
    # Attempt live API call
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(clean_city)}&count=1&language=en&format=json"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                output = {
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "city": result["name"],
                    "country": result.get("country", "Unknown")
                }
                return json.dumps(output)
    except Exception as e:
        print(f"⚠️ Geocoding API request failed ({e}). Using offline mock lookup...")
        
    # Offline fallback lookup
    lookup_key = clean_city.lower()
    if lookup_key in offline_db:
        return json.dumps(offline_db[lookup_key])
    
    # Generic default fallback
    return json.dumps({
        "latitude": 35.6895, 
        "longitude": 139.6917, 
        "city": clean_city, 
        "country": "Mock Country (Fallback)"
    })


# ── 2. Weather Tool with Offline Fallback ──────────────────────────────────────

# Open-Meteo Weather Codes:
# 0: Clear, 1-3: Partly Cloudy, 51-67: Drizzle/Rain, 71-82: Snow, 95-99: Thunderstorm
WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing Rime Fog",
    51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
    61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
    71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
    80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
    95: "Slight Thunderstorm", 96: "Thunderstorm with Slight Hail"
}

@tool
def get_weather_forecast(latitude: float, longitude: float) -> str:
    """
    Retrieve real-time current weather metrics using latitude and longitude coordinates.
    
    Parameters:
    - latitude: Latitude coordinate of the location.
    - longitude: Longitude coordinate of the location.
    """
    print(f"📡 [Weather Tool] Querying Open-Meteo API for coordinates ({latitude}, {longitude})...")
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            if "current_weather" in data:
                current = data["current_weather"]
                code = int(current.get("weathercode", 0))
                desc = WEATHER_CODES.get(code, "Unspecified Weather")
                
                output = {
                    "temperature": f"{current.get('temperature')}°C",
                    "windspeed": f"{current.get('windspeed')} km/h",
                    "weather_code": code,
                    "description": desc,
                    "is_raining": code >= 51
                }
                return json.dumps(output)
    except Exception as e:
        print(f"⚠️ Weather API request failed ({e}). Using offline mock forecast...")
        
    # Offline fallback (mocking an active rain condition to trigger the umbrella choice)
    return json.dumps({
        "temperature": "16.8°C",
        "windspeed": "12.4 km/h",
        "weather_code": 61,
        "description": "Slight Rain",
        "is_raining": True
    })

# ── 2b. Google Serper Search Tool ─────────────────────────────────────────────

@tool
def google_search(query: str) -> str:
    """
    Search Google for live real-time web results, today's events, tourist spots, or general news.
    
    Parameters:
    - query: The query to search Google for.
    """
    api_key = os.getenv("SERPER_API_KEY", "")
    if not api_key or "your_serper" in api_key.lower():
        print("⚠️ [Search Tool] SERPER_API_KEY missing or placeholder. Running in mock offline mode...")
        # Mock responses based on queries
        if "tokyo" in query.lower():
            return "Tokyo Tourism Update 2026: Highlights include the newly opened green pathways in Shibuya, teamLab's immersive art dome, and various cultural festivals."
        return f"Mock search result for '{query}': Found recent discussions and standard Wikipedia articles."
        
    print(f"📡 [Search Tool] Querying Google Serper API for: '{query}'...")
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        req = urllib.request.Request(url, data=payload.encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            snippets = []
            if "organic" in res_data:
                for item in res_data["organic"][:4]:
                    snippets.append(f"• {item.get('title')}: {item.get('snippet')}")
                return "\n".join(snippets)
            return str(res_data)
    except Exception as e:
        return f"Error executing web search: {e}"

# Register our tools
tools = [geocode_location, get_weather_forecast, google_search]

# ── 3. Run the Live Agent ─────────────────────────────────────────────────────

def run_live_agent():
    print("Constructing live agent using create_agent()...")
    
    agent = create_agent(
        model="deepseek:deepseek-chat",
        tools=tools,
        system_prompt=(
            "You are a helpful travel advisor. First, look up the latitude and longitude "
            "of the city using 'geocode_location'. Then, fetch the weather metrics using "
            "'get_weather_forecast' to recommend an umbrella or sunglasses. "
            "You can also use 'google_search' to answer general traveler questions about news, "
            "tourist spots, or local advice. Keep your response brief, structured, and informative."
        )
    )
    
    print("\n\033[92m✓ Live ReAct Travel Advisor Agent is ready!\033[0m")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 72)
    print("\nTry queries like:")
    print("  → I am planning a trip to Tokyo. Check the current weather in Tokyo and tell me if I should bring an umbrella or sunglasses.\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "I am planning a trip to Tokyo. Check the current weather in Tokyo and tell me if I should bring an umbrella or sunglasses."
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

        print("\n--- Starting ReAct Execution Loop ---\n")
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
    print("  → I am planning a trip to Tokyo. Check the current weather in Tokyo and tell me if I should bring an umbrella or sunglasses.\n")

    is_non_interactive = os.getenv("NON_INTERACTIVE", "false").lower() == "true" or not sys.stdin.isatty()

    while True:
        if is_non_interactive:
            user_input = "I am planning a trip to Tokyo. Check the current weather in Tokyo and tell me if I should bring an umbrella or sunglasses."
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

        print("\n--- Starting ReAct Weather Advisor (Simulated) ---\n")
        
        if "tokyo" in user_input.lower():
            # Step 1: Geocoding call
            print("  🧠 \033[93m[THINK/ACT]\033[0m → calling geocode_location({'city_name': 'Tokyo'})")
            time.sleep(0.5)
            geo_out = geocode_location.invoke({"city_name": "Tokyo"})
            print(f"  👁️ \033[96m[OBSERVE]\033[0m → {geo_out}")
            time.sleep(0.8)
            
            # Step 2: Weather forecast call
            print("  🧠 \033[93m[THINK/ACT]\033[0m → calling get_weather_forecast({'latitude': 35.6895, 'longitude': 139.6917})")
            time.sleep(0.5)
            weather_out = get_weather_forecast.invoke({"latitude": 35.6895, "longitude": 139.6917})
            print(f"  👁️ \033[96m[OBSERVE]\033[0m → {weather_out}")
            time.sleep(0.8)
            
            # Final Response
            final_output = (
                "According to current weather forecasts in Tokyo, the temperature is 16.8°C with Slight Rain.\n"
                "Since it is currently raining (or drizzle), you should definitely carry an **umbrella** today!"
            )
            
            print(f"  🏁 \033[92m[FINAL RESPONSE]\033[0m →\n{final_output}\n")
        else:
            print("  🧠 \033[93m[THINK/ACT]\033[0m → (Simulated thought: The user query is processed using travel and geocoding APIs.)")
            time.sleep(0.5)
            print("  🏁 \033[92m[FINAL RESPONSE]\033[0m → [Simulation Mode] This is a mock response. Please add a valid DEEPSEEK_API_KEY to your .env file to enable live execution for all queries.\n")
            
        if is_non_interactive:
            break

# ── 5. Main Entry Point ───────────────────────────────────────────────────────

def main():
    print_banner("07 — MULTI-STEP API DRIVEN WEATHER AGENT")
    
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
