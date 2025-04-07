# OpenDeepSearch MCP Server v0.1.0 Release Notes

## Overview

This is the initial release (v0.1.0) of the OpenDeepSearch MCP Server, which implements the Model Context Protocol to expose OpenDeepSearch's powerful search capabilities to LLM applications.

For a complete overview of the project, including detailed installation and usage instructions, please refer to the [README.md](./README.md).

## What's New

As this is the first release, all features are new:

- **MCP Protocol Implementation**: Full implementation of the Model Context Protocol (v1.5.0)
- **Search Tool**: Exposes the `perform_search` tool that executes the complete OpenDeepSearch workflow
- **Multi-Provider Support**: Compatible with multiple LLM providers (OpenAI, Anthropic, Google Gemini, Azure, OpenRouter, etc.)
- **Flexible Search Backends**: Support for both Serper and SearXNG search providers
- **Advanced Reranking**: Integration with reranking services (Jina, Infinity) to improve search result relevance
- **Pro Search Mode**: Option for deeper, more comprehensive search for complex queries
- **Smithery Integration**: Ready-to-use with Smithery CLI and other MCP-compatible clients

## Technical Highlights

- Built on OpenDeepSearch framework and the MCP specification v1.5.0
- Leverages LiteLLM for unified access to various LLM providers
- Implements stdio-based communication for MCP protocol
- Package entry point for easy installation and execution

## Known Limitations

- Requires at least one LLM provider API key to function
- Search functionality depends on either Serper.dev API key or a SearXNG instance
- Performance may vary depending on the LLM and search provider used

## Acknowledgments

This project builds upon:
- OpenDeepSearch core library
- Model Context Protocol (MCP) specification
- LiteLLM for model provider integration
- Various open-source libraries for search and retrieval
