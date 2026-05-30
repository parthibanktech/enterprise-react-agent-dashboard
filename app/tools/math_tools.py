from langchain_core.tools import tool

@tool
def divide(a: float, b: float) -> str:
    """Divide two numbers a and b. Use this for division calculations.
    
    Args:
        a: The numerator.
        b: The denominator.
    """
    print(f"[Division Tool] Executing {a} / {b}...")
    try:
        res = a / b
        return str(res)
    except ZeroDivisionError:
        return "Error: Division by zero is mathematically undefined."

@tool
def calculate(expression: str) -> str:
    """Evaluate any mathematical expression precisely. Use this for ALL generic arithmetic queries.
    Never guess numbers.
    
    Args:
        expression: A math expression string to evaluate (e.g. '347 * 86 / 5').
    """
    print(f"[Calculation Tool] Evaluating expression: '{expression}'...")
    try:
        # Evaluate safely in a restricted global scope
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@tool
def calculate_discount(original_price: float, discount_percent: float) -> str:
    """Calculate the final price after applying a percentage discount.

    Args:
        original_price: The original retail price in USD or Rupees.
        discount_percent: The discount percentage (e.g., 35 for 35%).
    """
    print(f"[Discount Tool] Applying {discount_percent}% discount to {original_price}...")
    saving = original_price * (discount_percent / 100)
    final  = original_price - saving
    return f"Original: ${original_price:,.2f} | Saving: ${saving:,.2f} | Final Price: ${final:,.2f}"

@tool
def calculate_gst(base_price: float, gst_percent: float) -> str:
    """Calculate the GST / tax amount and the total price after tax.

    Args:
        base_price: The base price before tax.
        gst_percent: The tax rate percentage (e.g., 18 for 18%).
    """
    print(f"[GST/Tax Tool] Calculating {gst_percent}% tax on {base_price}...")
    gst_amount = base_price * (gst_percent / 100)
    total      = base_price + gst_amount
    return f"Base: ${base_price:,.2f} | Tax ({gst_percent}%): ${gst_amount:,.2f} | Total: ${total:,.2f}"

@tool
def calculate_product_pricing(
    base_price: float,
    quantity: int,
    discount_percentage: float = 0.0,
    tax_percentage: float = 5.0
) -> str:
    """
    Calculate the precise bulk order invoice pricing including discount and sales tax.
    
    Args:
        base_price: The retail unit price of a single product item. Must be a positive decimal float.
        quantity: The total number of items ordered. Must be a positive integer.
        discount_percentage: Percentage discount to apply (e.g. 12.0 for 12%). Defaults to 0.0.
        tax_percentage: Sales tax rate to apply to the discounted total (e.g. 6.0 for 6%). Defaults to 5.0.
    """
    import json
    print(f"[Pricing Tool] Base Price: {base_price}, Qty: {quantity}, Discount: {discount_percentage}%, Tax: {tax_percentage}%")
    
    if base_price <= 0:
        return "Error: base_price must be a positive number greater than zero."
    if quantity <= 0:
        return "Error: quantity must be a positive integer greater than zero."
    
    subtotal = base_price * quantity
    discount_amount = subtotal * (discount_percentage / 100.0)
    discounted_subtotal = subtotal - discount_amount
    tax_amount = discounted_subtotal * (tax_percentage / 100.0)
    final_total = discounted_subtotal + tax_amount
    
    breakdown = {
        "unit_price": f"${base_price:,.2f}",
        "quantity": quantity,
        "raw_subtotal": f"${subtotal:,.2f}",
        "applied_discount_rate": f"{discount_percentage}%",
        "discount_savings": f"${discount_amount:,.2f}",
        "taxable_amount": f"${discounted_subtotal:,.2f}",
        "tax_rate": f"{tax_percentage}%",
        "tax_amount": f"${tax_amount:,.2f}",
        "final_invoice_total": f"${final_total:,.2f}"
    }
    
    return json.dumps(breakdown, indent=2)
