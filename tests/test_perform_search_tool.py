# mcp_server/tests/test_perform_search_tool.py
import pytest
from mcp.types import TextContent
from src.server import call_mcp_tool

# Note: pytest-asyncio is implicitly used by pytest when it finds async tests
# marked with @pytest.mark.asyncio

@pytest.mark.asyncio
async def test_perform_search_tool_output_format(mocker):
    """
    Tests that the perform_search tool handler returns the expected
    markdown format for a successful search.
    """
    # 1. Mock the underlying agent call
    # Patch the OpenDeepSearchAgent class where it's used in the server module
    mock_agent_class = mocker.patch('src.server.OpenDeepSearchAgent') # Patch based on actual file path
    # Get the mock instance that the class will produce
    mock_agent_instance = mock_agent_class.return_value
    # Ensure the 'ask' method on the instance is an AsyncMock
    mock_agent_instance.ask = mocker.AsyncMock()
    # Assign the mock 'ask' method to the variable used later for configuration/assertion
    mock_ask = mock_agent_instance.ask

    # 2. Configure the mock return value
    mock_result_dict = {
        'answer': 'Test Answer',
        'sources': [
            {
                'title': 'Source 1',
                'link': 'http://example.com/1',
                # Provide 'html' as the server code prefers it
                'html': 'Snippet 1 Content'
            },
            {
                'title': 'Source 2',
                'link': 'http://example.com/2',
                # Provide 'snippet' to test fallback logic in server code
                'snippet': 'Snippet 2 Content'
            }
        ]
    }
    mock_ask.return_value = mock_result_dict

    # 3. Define sample arguments for the tool call
    sample_arguments = {'query': 'test query'}

    # 4. Call the tool handler
    result = await call_mcp_tool(name="perform_search", arguments=sample_arguments)

    # 5. Assertions
    # Assert result structure
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"

    # Assert content format
    output_text = result[0].text
    assert "Test Answer" in output_text
    assert "\n\n---\n**Sources:**" in output_text # Check separator and header

    # Assert source 1 details (using 'html')
    assert "1. **Title:** Source 1" in output_text
    assert "**Link:** http://example.com/1" in output_text
    assert "**Content:** Snippet 1 Content" in output_text # Check the actual content used

    # Assert source 2 details (using 'snippet' fallback)
    assert "2. **Title:** Source 2" in output_text
    assert "**Link:** http://example.com/2" in output_text
    assert "**Content:** Snippet 2 Content" in output_text # Check the actual content used

    # Verify the mock was called correctly with expected default arguments
    mock_ask.assert_awaited_once_with(
        query='test query',
        max_sources=2, # Default value from _perform_search signature
        pro_mode=False # Default value from _perform_search signature
    )


@pytest.mark.asyncio
async def test_perform_search_tool_with_args(mocker):
    """
    Tests that the perform_search tool handler correctly passes
    non-default arguments (max_sources, pro_mode) to the agent.
    """
    mock_agent_class = mocker.patch('src.server.OpenDeepSearchAgent') # Patch based on actual file path
    mock_agent_instance = mock_agent_class.return_value
    mock_agent_instance.ask = mocker.AsyncMock()
    mock_ask = mock_agent_instance.ask

    mock_result_dict = {
        'answer': 'Pro Answer',
        'sources': [{'title': 'Pro Source', 'link': 'http://pro.example.com', 'html': 'Pro Content'}]
    }
    mock_ask.return_value = mock_result_dict

    sample_arguments = {'query': 'pro query', 'max_sources': 5, 'pro_mode': True}

    result = await call_mcp_tool(name="perform_search", arguments=sample_arguments)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    output_text = result[0].text
    assert "Pro Answer" in output_text
    assert "1. **Title:** Pro Source" in output_text

    mock_ask.assert_awaited_once_with(
        query='pro query',
        max_sources=5, # Explicitly passed value
        pro_mode=True  # Explicitly passed value
    )


@pytest.mark.asyncio
async def test_perform_search_tool_no_sources(mocker):
    """
    Tests that the perform_search tool handler correctly formats the output
    when the agent returns an answer but no sources.
    """
    mock_agent_class = mocker.patch('src.server.OpenDeepSearchAgent') # Patch based on actual file path
    mock_agent_instance = mock_agent_class.return_value
    mock_agent_instance.ask = mocker.AsyncMock()
    mock_ask = mock_agent_instance.ask

    # Mock return value with empty sources list
    mock_result_dict = {
        'answer': 'Answer without sources',
        'sources': []
    }
    mock_ask.return_value = mock_result_dict

    sample_arguments = {'query': 'query with no sources'}

    result = await call_mcp_tool(name="perform_search", arguments=sample_arguments)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    output_text = result[0].text

    assert "Answer without sources" in output_text
    # Check that the sources section indicates none were found
    assert "\n\n---\n**Sources:**\nNo sources found." in output_text
    # Ensure no numbered list items appear
    assert "1. **Title:**" not in output_text

    mock_ask.assert_awaited_once_with(
        query='query with no sources',
        max_sources=2,
        pro_mode=False
    )


@pytest.mark.asyncio
async def test_perform_search_tool_agent_error(mocker):
    """
    Tests that the perform_search tool handler raises a RuntimeError
    if the underlying agent call fails.
    """
    mock_agent_class = mocker.patch('src.server.OpenDeepSearchAgent') # Patch based on actual file path
    mock_agent_instance = mock_agent_class.return_value
    mock_agent_instance.ask = mocker.AsyncMock()
    mock_ask = mock_agent_instance.ask

    # Configure the mock to raise an exception
    mock_ask.side_effect = Exception("Agent failed")

    sample_arguments = {'query': 'query causing error'}

    # Call the tool handler and expect an error message in the result
    result = await call_mcp_tool(name="perform_search", arguments=sample_arguments)

    # Assertions for error handling within the tool call function
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    # Check that the returned text contains the expected error message format
    assert "Error performing search: Agent failed" in result[0].text # Match the error from _perform_search

    mock_ask.assert_awaited_once_with(
        query='query causing error',
        max_sources=2,
        pro_mode=False
    )


@pytest.mark.asyncio
async def test_perform_search_tool_missing_content(mocker):
    """
    Tests source formatting when a source dictionary lacks both 'html' and 'snippet'.
    """
    mock_agent_class = mocker.patch('src.server.OpenDeepSearchAgent') # Patch based on actual file path
    mock_agent_instance = mock_agent_class.return_value
    mock_agent_instance.ask = mocker.AsyncMock()
    mock_ask = mock_agent_instance.ask

    mock_result_dict = {
        'answer': 'Answer with missing content',
        'sources': [
            {'title': 'Source Missing Content', 'link': 'http://missing.com'} # No 'html' or 'snippet'
        ]
    }
    mock_ask.return_value = mock_result_dict

    sample_arguments = {'query': 'missing content query'}

    result = await call_mcp_tool(name="perform_search", arguments=sample_arguments)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    output_text = result[0].text

    assert "Answer with missing content" in output_text
    assert "1. **Title:** Source Missing Content" in output_text
    assert "**Link:** http://missing.com" in output_text
    # Check that the content line indicates missing content
    assert "**Content:** N/A" in output_text # Check the actual fallback content

    mock_ask.assert_awaited_once_with(
        query='missing content query',
        max_sources=2,
        pro_mode=False
    )