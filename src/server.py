import asyncio
import logging
import argparse
from typing import List, Dict, Any, Optional

import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from opendeepsearch.ods_agent import OpenDeepSearchAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("opendeepsearch_mcp")

mcp = Server("opendeepsearch")

@mcp.list_tools()
async def list_mcp_tools() -> List[types.Tool]:
    """Lists the available tools for the OpenDeepSearch MCP server."""
    logger.info("Listing available tools")
    return [
        types.Tool(
            name="perform_search",
            description="Executes the full OpenDeepSearch workflow: web search, content processing, context building, and LLM query answering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question or search query."
                    },
                    "max_sources": {
                        "type": "integer",
                        "description": "Maximum number of web sources to process.",
                        "default": 2
                    },
                    "pro_mode": {
                        "type": "boolean",
                        "description": "Enable deeper processing.",
                        "default": False
                    },
                    "model": {
                        "type": "string",
                        "description": "Override the default LLM model."
                    },
                    "search_provider": {
                        "type": "string",
                        "description": "Override the default search provider (e.g., 'serper', 'searxng')."
                    },
                    "reranker": {
                        "type": "string",
                        "description": "Override the default reranker (e.g., 'jina', 'infinity', 'none')."
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "Override the default system prompt for the LLM."
                    },
                    "serper_api_key": {
                        "type": "string",
                        "description": "API key for Serper search provider."
                    },
                    "searxng_instance_url": {
                        "type": "string",
                        "description": "URL of the SearXNG instance."
                    },
                    "searxng_api_key": {
                        "type": "string",
                        "description": "API key for SearXNG instance."
                    },
                    "jina_api_key": {
                        "type": "string",
                        "description": "API key for Jina reranker."
                    }
                },
                "required": ["query"]
            }
        )
    ]

async def _perform_search(
    query: str,
    max_sources: int = 2,
    pro_mode: bool = False,
    model: Optional[str] = None,
    search_provider: Optional[str] = None,
    reranker: Optional[str] = None,
    system_prompt: Optional[str] = None,
    serper_api_key: Optional[str] = None,
    searxng_instance_url: Optional[str] = None,
    searxng_api_key: Optional[str] = None,
    jina_api_key: Optional[str] = None,
    **kwargs: Any # Catch any unexpected args passed by MCP client
) -> str:
    """Helper function to perform the actual search using OpenDeepSearchAgent."""
    # Log received arguments, filtering potentially sensitive ones if necessary
    log_args = {
        "query": query,
        "max_sources": max_sources,
        "pro_mode": pro_mode,
        "model": model,
        "search_provider": search_provider,
        "reranker": reranker
    }
    log_args = {k: v for k, v in log_args.items() if v is not None}
    logger.info(f"Performing search with args: {log_args}")


    import io
    from contextlib import redirect_stdout

    captured_output = io.StringIO()

    try:

        import os
        original_env = {}
        env_vars_to_set = {}

        if serper_api_key:
            env_vars_to_set['SERPER_API_KEY'] = serper_api_key
        if searxng_instance_url:
            env_vars_to_set['SEARXNG_INSTANCE_URL'] = searxng_instance_url
        if searxng_api_key:
            env_vars_to_set['SEARXNG_API_KEY'] = searxng_api_key
        if jina_api_key:
            env_vars_to_set['JINA_API_KEY'] = jina_api_key

        for key in env_vars_to_set:
            if key in os.environ:
                original_env[key] = os.environ[key]
        for key, value in env_vars_to_set.items():
            os.environ[key] = value


        agent_config = {}
        if model: agent_config['model'] = model
        if search_provider: agent_config['search_provider'] = search_provider
        if reranker: agent_config['reranker'] = reranker
        if system_prompt: agent_config['system_prompt'] = system_prompt
        if serper_api_key: agent_config['serper_api_key'] = serper_api_key
        if searxng_instance_url: agent_config['searxng_instance_url'] = searxng_instance_url
        if searxng_api_key: agent_config['searxng_api_key'] = searxng_api_key


        with redirect_stdout(captured_output):
            agent = OpenDeepSearchAgent(**agent_config)


            result_dict = await agent.ask(
                query=query,
                max_sources=max_sources,
                pro_mode=pro_mode
            )


        for key in env_vars_to_set:
            if key in original_env:
                os.environ[key] = original_env[key]
            else:
                del os.environ[key]

        logger.info(f"Search completed successfully for query: '{query}'")


        captured_text = captured_output.getvalue()
        if captured_text:
            logger.debug(f"Captured output during search: {captured_text}")


        answer = result_dict.get("answer", "No answer found.")
        sources = result_dict.get("sources", [])

        logger.info(f"Received answer length: {len(answer)} characters")
        logger.info(f"Received {len(sources)} sources.")
        logger.debug(f"Answer preview: {answer[:200]}...")
        logger.debug(f"Sources preview: {sources[:2]}")


        markdown_parts = [answer]
        if sources:
            markdown_parts.append("\n\n---\n**Sources:**")
            for i, source in enumerate(sources):
                title = source.get('title', 'N/A')
                link = source.get('link', 'N/A')
                content = source.get('html') or source.get('snippet', 'N/A')

                markdown_parts.append(
                    f"{i+1}. **Title:** {title}\n"
                    f"   **Link:** {link}\n"
                    f"   **Content:** {content}"
                )
        else:

            markdown_parts.append("\n\n---\n**Sources:**\nNo sources found.")
        formatted_markdown = "\n".join(markdown_parts)

        logger.info(f"Formatted markdown length: {len(formatted_markdown)} characters")
        logger.info(f"Formatted markdown preview: {formatted_markdown[:200]}...")

        return formatted_markdown
    except Exception as e:

        import os
        for key in env_vars_to_set:
            if key in original_env:
                os.environ[key] = original_env[key]
            elif key in os.environ:
                del os.environ[key]

        logger.exception(f"Error during perform_search for query '{query}': {e}")


        captured_text = captured_output.getvalue()
        if captured_text:
            logger.debug(f"Captured output during error: {captured_text}")
            return f"Error performing search: {e}\n\nDebug output: {captured_text}"
        else:
            return f"Error performing search: {e}"


@mcp.call_tool()
async def call_mcp_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handles incoming tool calls."""
    logger.info(f"Received call for tool '{name}' with arguments: {arguments}")
    try:
        if name == "perform_search":
            result_text = await _perform_search(**arguments)
            logger.info(f"Returning result to MCP client. Result type: {type(result_text)}")
            logger.info(f"First 100 chars of result: {result_text[:100]}...")
            return [types.TextContent(type="text", text=result_text)]
        else:
            logger.error(f"Unknown tool called: {name}")
            return [types.TextContent(type="text", text=f"Error: Unknown tool: {name}")]
    except Exception as e:
        logger.exception(f"Error calling tool '{name}': {e}")
        return [types.TextContent(type="text", text=f"Error executing tool '{name}': {e}")]


async def main():
    """
    Main entry point for the MCP server using stdio.
    """
    parser = argparse.ArgumentParser(description="OpenDeepSearch MCP Server (stdio)")
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )
    parser.add_argument(
        "--active",
        action="store_true",
        help="Use the active Python environment",
    )

    args, _ = parser.parse_known_args()

    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
    logger.info(f"Setting log level to {args.log_level.upper()}")

    try:
        from mcp.server.stdio import stdio_server

        logger.info("Starting OpenDeepSearch MCP server via stdio...")

        async with stdio_server() as (read_stream, write_stream):
            await mcp.run(
                read_stream=read_stream,
                write_stream=write_stream,
                initialization_options=InitializationOptions(
                    server_name="opendeepsearch",
                    server_version="0.1.0",
                    capabilities=mcp.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
                raise_exceptions=True,
            )

        logger.info("OpenDeepSearch MCP server started.")
    except Exception as e:
        logger.exception(f"Server failed to start: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user (KeyboardInterrupt).")