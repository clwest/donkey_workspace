from tools.utils.decorators import tool


@tool(name="Echo Tool", slug="echo_test", description="Returns text", tags=["test"])
def echo(text: str) -> dict:
    """Simple echo tool for testing."""
    return {"echo": text}
