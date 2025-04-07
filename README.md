# OpenDeepSearch MCP Server

This is a Model Context Protocol (MCP) server for OpenDeepSearch that allows LLM applications to interact with OpenDeepSearch's search capabilities.

## Features

- Exposes OpenDeepSearch's search functionality as MCP tools
- Integrates with Claude Desktop and other MCP-compatible clients
- Provides a standardized interface for LLM applications to access web search capabilities

## Installation

```bash
# Install the package in development mode
pip install -e .
```

## Usage

### Running the server directly

```bash
# Run the MCP server
opendeepsearch-mcp
```

### Using with MCP Inspector

```bash
# Run with MCP Inspector
npx @modelcontextprotocol/inspector uv run --python ../.venv/bin/python opendeepsearch-mcp --active
```

### Using with Claude Desktop

Install the server in Claude Desktop:

```bash
mcp install opendeepsearch-mcp
```

## Development

This package follows the MCP specification and provides tools for search functionality through OpenDeepSearch.
