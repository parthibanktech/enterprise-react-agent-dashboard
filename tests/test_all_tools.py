import json
import sqlite3
from app.tools.math_tools import calculate, divide, calculate_discount, calculate_gst, calculate_product_pricing
from app.tools.api_tools import geocode_location, get_weather_forecast, google_search
from app.tools.db_tools import query_products_database

# ── Math Tools Tests ──────────────────────────────────────────────────────────

def test_math_calculate():
    """Test generic math expression evaluator tool."""
    res1 = calculate.invoke({"expression": "25 * 4"})
    assert res1 == "100"
    
    res2 = calculate.invoke({"expression": "100 / 5"})
    assert res2 == "20.0"
    
    res_err = calculate.invoke({"expression": "invalid_expression"})
    assert "Error" in res_err

def test_math_divide():
    """Test division tool."""
    res = divide.invoke({"a": 15.0, "b": 3.0})
    assert res == "5.0"
    
    res_zero = divide.invoke({"a": 10.0, "b": 0.0})
    assert "undefined" in res_zero or "Error" in res_zero

def test_math_calculate_discount():
    """Test standard discount estimator tool."""
    res = calculate_discount.invoke({"original_price": 200.0, "discount_percent": 25.0})
    assert "Original: $200.00" in res
    assert "Saving: $50.00" in res
    assert "Final Price: $150.00" in res

def test_math_calculate_gst():
    """Test tax estimator tool."""
    res = calculate_gst.invoke({"base_price": 500.0, "gst_percent": 18.0})
    assert "Base: $500.00" in res
    assert "Tax (18.0%): $90.00" in res
    assert "Total: $590.00" in res

# ── API Tools Tests ───────────────────────────────────────────────────────────

def test_api_geocode_location():
    """Test geocode city coords tool."""
    # Test valid cached city
    res_tokyo = json.loads(geocode_location.invoke({"city_name": "Tokyo"}))
    assert round(res_tokyo["latitude"], 4) == 35.6895
    assert round(res_tokyo["longitude"], 4) == 139.6917
    assert res_tokyo["city"] == "Tokyo"
    
    # Test fallback default city
    res_fallback = json.loads(geocode_location.invoke({"city_name": "UnknownCityTest"}))
    assert "UnknownCityTest" in res_fallback["city"]

def test_api_get_weather_forecast():
    """Test weather metrics lookup tool."""
    res = json.loads(get_weather_forecast.invoke({"latitude": 35.6895, "longitude": 139.6917}))
    assert "temperature" in res
    assert "windspeed" in res
    assert "description" in res

def test_api_google_search():
    """Test live search tool."""
    res = google_search.invoke({"query": "tokyo events"})
    assert len(res) > 0

# ── DB Tool Tests ──────────────────────────────────────────────────────────────

def test_db_query_products_database_success():
    """Test database selection query."""
    res_str = query_products_database.invoke({"sql_query": "SELECT name, category, price FROM products WHERE price < 100 ORDER BY price ASC"})
    res = json.loads(res_str)
    assert len(res) > 0
    assert "USB-C Hub Multiport" in [r["name"] for r in res]

def test_db_query_products_database_no_rows():
    """Test database query with no matched rows."""
    res = query_products_database.invoke({"sql_query": "SELECT name FROM products WHERE price > 9999.0"})
    assert "No matching rows found" in res

def test_db_query_products_database_security_keyword():
    """Test database read-only restriction guards."""
    res = query_products_database.invoke({"sql_query": "DROP TABLE products"})
    assert "Security Error" in res
    assert "forbidden" in res

def test_db_query_products_database_invalid_syntax():
    """Test database runtime SQL error capture."""
    res = query_products_database.invoke({"sql_query": "SELECT name FROM invalid_table_name"})
    assert "Database SQLite Error" in res
