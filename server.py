"""Read-only MCP tools for a trusted directory of public text documents."""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("IAG Knowledge Server")
KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
ALLOWED_SUFFIXES = {".md", ".txt"}


def _document_path(filename: str) -> Path | None:
    """Accept only ordinary, top-level text files, never links or paths."""
    if (
        not filename
        or filename.startswith(".")
        or any(char in filename for char in ("/", "\\", ":", "\x00"))
        or Path(filename).suffix.lower() not in ALLOWED_SUFFIXES
    ):
        return None
    root = Path(KNOWLEDGE_DIR).resolve()
    candidate = root / filename
    try:
        if candidate.is_symlink() or not candidate.is_file():
            return None
        resolved = candidate.resolve(strict=True)
        return resolved if resolved.parent == root else None
    except (OSError, RuntimeError, ValueError):
        return None


def _documents() -> list[Path]:
    """Use the same access policy for listing, searching, and retrieval."""
    try:
        names = sorted(path.name for path in Path(KNOWLEDGE_DIR).iterdir())
    except OSError:
        return []
    return [path for name in names if (path := _document_path(name)) is not None]


@mcp.tool()
def list_documents() -> str:
    """List available top-level Markdown and text documents alphabetically."""
    return "\n".join(path.name for path in _documents())


@mcp.tool()
def search_knowledge(query: str) -> str:
    """Search readable UTF-8 documents for a nonempty, case-insensitive phrase."""
    if not query.strip():
        return "Please provide a non-empty search query."
    results = []
    for path in _documents():
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if query.casefold() in content.casefold():
            results.append(f"--- {path.name} ---\n{content}")
    return "\n\n".join(results) if results else "No results found for: " + query


@mcp.tool()
def get_document(filename: str) -> str:
    """Read an available document by its exact filename, without directory paths."""
    path = _document_path(filename)
    if path is None:
        return "Document not found or filename not allowed."
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return "Document could not be read as UTF-8 text."


if __name__ == "__main__":
    mcp.run()
