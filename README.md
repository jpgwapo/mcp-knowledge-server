# MCP Knowledge Server

[![Tests](https://github.com/jpgwapo/mcp-knowledge-server/actions/workflows/tests.yml/badge.svg)](https://github.com/jpgwapo/mcp-knowledge-server/actions/workflows/tests.yml)

A read-only Model Context Protocol (MCP) server that makes a small local knowledge base available to an AI assistant over stdio. The repository includes public sample documents for a reproducible demo.

## Setup

Use Python 3.11–3.13 on Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

The server waits for an MCP client on stdin; it is not an interactive terminal prompt or an HTTP service. Configure your MCP client to launch the absolute path to `.venv/bin/python` with the absolute path to `server.py` as its argument. Document paths are relative to the server file, so the client's working directory does not matter.

`requirements.txt` pins the compatible MCP 1.x SDK. Transitive dependencies are resolved by pip; this is not a complete dependency lockfile.

## Tools

| Tool | Input | Result |
| --- | --- | --- |
| `list_documents` | None | Allowed filenames, sorted alphabetically |
| `search_knowledge` | `query`, e.g. `irrigation` | Matching document contents with filename headings; matching ignores case |
| `get_document` | `filename`, e.g. `equipment.md` | UTF-8 document contents or a safe error message |

## Document access policy

Only ordinary, non-hidden `.md` and `.txt` files directly inside `knowledge/` are available. Nested paths, absolute paths, traversal, symbolic links, directories, and other file types are rejected. Listing, search, and retrieval use the same policy. Empty searches are rejected; search skips unreadable or invalid UTF-8 files.

Keep this directory trusted and writable only by the server operator. These checks restrict tool-supplied filenames; they are not an operating-system sandbox against another process concurrently replacing files. All allowed documents can be read by the connected client: there is no per-user authorization. Use synthetic/public documents for demos, and do not commit credentials or private company material.

## Tests

```bash
python -m unittest discover -v
python -m pip check
```

Tests use temporary synthetic documents, covering valid reads, search, traversal, absolute paths, symlink escapes, non-regular files, invalid UTF-8, unreadable files, and missing directories. A stdio integration test also verifies tool discovery and calls from an MCP client launched in a different working directory. CI runs the suite on Python 3.11, 3.12, and 3.13 for pull requests and pushes to `main`.

## Portfolio scope

This project demonstrates MCP tool development, restricted file access, regression tests, and continuous integration. It is a local demo, not a multi-tenant document service.
