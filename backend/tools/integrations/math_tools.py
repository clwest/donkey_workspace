from tools.utils.decorators import tool

@tool(name="Add Numbers", slug="math_add", description="Add two numbers")
def add(a: int, b: int) -> dict:
    """Return the sum of a and b."""
    return {"result": a + b}
