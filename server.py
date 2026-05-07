from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("IAG Knowledge Server")

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")

@mcp.tool()
def list_documents() -> str:
    """List all available knowledge base documents."""
    files = os.listdir(KNOWLEDGE_DIR)
    return "\n".join(files)

@mcp.tool()
def search_knowledge(query: str) -> str:
    """Search the knowledge base for information matching the query."""
    results = []
    query_lower = query.lower()
    
    for filename in os.listdir(KNOWLEDGE_DIR):
        filepath = os.path.join(KNOWLEDGE_DIR, filename)
        with open(filepath, "r") as f:
            content = f.read()
            if query_lower in content.lower():
                results.append(f"--- {filename} ---\n{content}")
    
    if results:
        return "\n\n".join(results)
    return "No results found for: " + query

@mcp.tool()
def get_document(filename: str) -> str:
    """Get the full contents of a specific knowledge base document."""
    filepath = os.path.join(KNOWLEDGE_DIR, filename)
    if not os.path.exists(filepath):
        return f"Document '{filename}' not found."
    with open(filepath, "r") as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()
