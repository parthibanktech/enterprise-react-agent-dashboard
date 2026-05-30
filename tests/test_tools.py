import json
from app.tools.math_tools import divide, calculate_product_pricing

def test_divide_success():
    """Test successful division execution."""
    res = divide.invoke({"a": 10.0, "b": 2.0})
    assert res == "5.0"

def test_divide_zero_division():
    """Test that zero division returns a safe error string instead of raising an exception."""
    res = divide.invoke({"a": 50.0, "b": 0.0})
    assert "Error" in res or "undefined" in res

def test_calculate_product_pricing_success():
    """Test successful product pricing invoice breakdown."""
    res_str = calculate_product_pricing.invoke({
        "base_price": 100.0,
        "quantity": 5,
        "discount_percentage": 10.0,
        "tax_percentage": 5.0
    })
    res = json.loads(res_str)
    assert res["unit_price"] == "$100.00"
    assert res["quantity"] == 5
    assert res["raw_subtotal"] == "$500.00"
    assert res["discount_savings"] == "$50.00"
    assert res["final_invoice_total"] == "$472.50"

def test_calculate_product_pricing_validation():
    """Test that invalid negative parameters raise validation errors."""
    res_err1 = calculate_product_pricing.invoke({
        "base_price": -10.0,
        "quantity": 5
    })
    assert "Error" in res_err1
    
    res_err2 = calculate_product_pricing.invoke({
        "base_price": 10.0,
        "quantity": -5
    })
    assert "Error" in res_err2
