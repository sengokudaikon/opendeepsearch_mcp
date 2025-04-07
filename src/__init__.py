from .server import main as server_main

def main():
    """Main entry point for the opendeepsearch-mcp package."""
    import asyncio
    import nest_asyncio

    nest_asyncio.apply()

    asyncio.run(server_main())

if __name__ == "__main__":
    main()