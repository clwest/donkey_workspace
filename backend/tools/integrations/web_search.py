from tools.utils.decorators import tool

@tool(name="Web Search", slug="web_search", description="Perform a simple web search")
def search(query: str) -> dict:
    """Mock search tool."""
    return {"query": query, "results": ["result1", "result2"]}
