        raise ValueError(f"Unknown tool: {name}")


# Server initialization
@app.init_context()
async def initialize_context():
    return {"dataset": DATASET}


# Main entry point
if __name__ == "__main__":
    import asyncio
    
    async def main():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="chembl-server",
                    server_version="1.0.0",
                    capabilities=app.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )
    
    asyncio.run(main())