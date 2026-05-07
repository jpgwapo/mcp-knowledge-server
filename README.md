# MCP Knowledge Server

A Model Context Protocol (MCP) server that connects an internal knowledge base to AI assistants like Claude.

## Tools
- `list_documents` — List all available knowledge base documents
- `search_knowledge` — Search across all documents by keyword
- `get_document` — Retrieve a specific document by filename

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install mcp
python3 server.py
```

## Use Case
Built as a portfolio project demonstrating MCP server development for AI automation roles.
