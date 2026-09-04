from mcp_client import run_mcp_tool


print("=" * 60)
print("BUVVAS MCP CONNECTION TEST")
print("=" * 60)


try:

    result = run_mcp_tool(

        "search_products",

        {
            "query": "barcode scanner"
        }

    )


    print()
    print("=" * 60)
    print("SUCCESS")
    print("=" * 60)

    print(result)


except Exception as e:

    print()
    print("=" * 60)
    print("ERROR")
    print("=" * 60)

    print(
        repr(e)
    )

    import traceback

    traceback.print_exc()