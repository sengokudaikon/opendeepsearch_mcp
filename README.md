# OpenDeepSearch MCP Server

This is a Model Context Protocol (MCP) server for OpenDeepSearch that allows LLM applications to interact with OpenDeepSearch's search capabilities.

## Features

- Exposes OpenDeepSearch's search functionality as MCP tools
- Integrates with Claude Desktop and other MCP-compatible clients
- Provides a standardized interface for LLM applications to access web search capabilities

## Setup

This project uses `uv` for dependency management.

1.  **Install `uv`**: Follow the instructions [here](https://docs.astral.sh/uv/install/).
2.  **Sync Dependencies**: Navigate to the `mcp_server` directory and run:
    ```bash
    uv sync
    ```
    This will install dependencies based on `pyproject.toml` and `uv.lock`.

## Configuration

The server requires certain environment variables to function correctly, especially API keys for the underlying services. These can be set directly in your environment or passed via the MCP client configuration (e.g., using Smithery CLI).

| Variable               | Description                                                                      | Required | Default | Notes                                                                                         |
|:-----------------------|:---------------------------------------------------------------------------------|:---------|:--------|:----------------------------------------------------------------------------------------------|
| **LLM Providers**      | **(Provide at least one)**                                                       |          |         |                                                                                               |
| `OPENAI_API_KEY`       | API key for OpenAI LLM.                                                          | Optional | None    | Needed if using OpenAI models.                                                                |
| `OPENAI_BASE_URL`      | Custom base URL for OpenAI compatible endpoints.                                 | Optional | None    |                                                                                               |
| `ANTHROPIC_API_KEY`    | API key for Anthropic LLM.                                                       | Optional | None    | Needed if using Anthropic models.                                                             |
| `OPENROUTER_API_KEY`   | API key for OpenRouter.                                                          | Optional | None    | Needed if using OpenRouter models.                                                            |
| `FIREWORKS_API_KEY`    | API key for Fireworks AI.                                                        | Optional | None    | Needed if using Fireworks models.                                                             |
| `GEMINI_API_KEY`       | API key for Google Gemini.                                                       | Optional | None    | Needed if using Gemini models.                                                                |
| `AZURE_API_KEY`        | API key for Azure OpenAI Service.                                                | Optional | None    | Needed if using Azure OpenAI models.                                                          |
| `AZURE_API_BASE`       | API base URL for Azure OpenAI Service.                                           | Optional | None    | Needed if using Azure OpenAI models.                                                          |
| `AZURE_API_VERSION`    | API version for Azure OpenAI Service.                                            | Optional | None    | Needed if using Azure OpenAI models.                                                          |
| `AZURE_DEPLOYMENT_ID`  | Deployment ID for Azure OpenAI Service.                                          | Optional | None    | Needed if using Azure OpenAI models.                                                          |
| `DEEPSEEK_API_KEY`     | API key for DeepSeek.                                                            | Optional | None    | Needed if using DeepSeek models.                                                              |
| **Search Providers**   |                                                                                  |          |         |                                                                                               |
| `SERPER_API_KEY`       | API key for Serper search provider.                                              | Optional | None    | Required if `search_provider` is set to `'serper'` (either by default or via tool argument).  |
| `SEARXNG_INSTANCE_URL` | URL of your SearXNG instance.                                                    | Optional | None    | Required if `search_provider` is set to `'searxng'` (either by default or via tool argument). |
| `SEARXNG_API_KEY`      | API key for your SearXNG instance (if required by the instance).                 | Optional | None    | Used if `search_provider` is set to `'searxng'`.                                              |
| **Rerankers**          |                                                                                  |          |         |                                                                                               |
| `JINA_API_KEY`         | API key for Jina AI Reranker.                                                    | Optional | None    | Required if `reranker` is set to `'jina'` (either by default or via tool argument).           |
| **Other Tools**        |                                                                                  |          |         |                                                                                               |
| `WOLFRAM_ALPHA_APP_ID` | App ID for WolframAlpha tool integration (if enabled in the agent).              | Optional | None    |                                                                                               |
| **Server Behavior**    |                                                                                  |          |         |                                                                                               |
| `LOG_LEVEL`            | Controls the server's logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL). | Optional | INFO    | Can also be set via the `--log-level` CLI argument passed by `smithery.yaml`.                 |

**Note:** API keys passed directly as arguments to the `perform_search` tool (`serper_api_key`, `searxng_api_key`, `jina_api_key`) will temporarily override the environment variables for that specific call.

## Usage with Smithery CLI

You can run this server using the Smithery CLI and the provided `smithery.yaml` configuration file. This allows you to easily manage the required environment variables.

```bash
# Example: Run with OpenRouter key and Serper key
npx -y @smithery/cli@latest run . --config '{"openrouterApiKey":"sk-or-...", "serperApiKey":"your-serper-key"}'

# Example: Run with OpenAI key and SearXNG
npx -y @smithery/cli@latest run . --config '{"openaiApiKey":"sk-...", "searxngInstanceUrl":"https://your-searxng-instance.com"}'

# Example: Run with Gemini key
npx -y @smithery/cli@latest run . --config '{"geminiApiKey":"..."}'

# Example: Run with Azure keys
npx -y @smithery/cli@latest run . --config '{"azureApiKey":"...", "azureApiBase":"https://your-azure.openai.azure.com/", "azureApiVersion":"2024-02-01", "azureDeploymentId":"your-deployment"}'
```

The `smithery.yaml` file defines the necessary configuration schema. Refer to it for all available options.

## Development

This package follows the MCP specification and provides tools for search functionality through OpenDeepSearch.
