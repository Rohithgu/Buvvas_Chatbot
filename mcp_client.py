import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# server.py is in the SAME folder as mcp_client.py
SERVER_PATH = BASE_DIR / "server.py"


# ============================================================
# LOGGING
# ============================================================

def log(message):
    print(
        message,
        file=sys.stderr,
        flush=True
    )


# ============================================================
# CHECK SERVER
# ============================================================

def check_server():

    log(
        f"[MCP CLIENT] Looking for server: {SERVER_PATH}"
    )

    if not SERVER_PATH.exists():

        log(
            "[MCP CLIENT] ERROR: server.py not found!"
        )

        return False

    log(
        "[MCP CLIENT] server.py found successfully"
    )

    return True


# ============================================================
# EXTRACT MCP RESULT
# ============================================================

def extract_mcp_result(result):

    # If the result is already a Python dictionary,
    # simply return it.
    if isinstance(result, dict):

        return result


    if result is None:

        return {
            "success": False,
            "count": 0,
            "products": [],
            "error": "Empty MCP response"
        }


    # --------------------------------------------------------
    # Structured content
    # --------------------------------------------------------

    structured = getattr(
        result,
        "structuredContent",
        None
    )

    if structured is None:

        structured = getattr(
            result,
            "structured_content",
            None
        )


    if structured:

        if isinstance(
            structured,
            dict
        ):

            return structured


    # --------------------------------------------------------
    # Normal MCP content
    # --------------------------------------------------------

    content = getattr(
        result,
        "content",
        []
    )


    text_parts = []


    for item in content:

        text_value = getattr(
            item,
            "text",
            None
        )

        if text_value:

            text_parts.append(
                text_value
            )


    if not text_parts:

        return {
            "success": False,
            "count": 0,
            "products": [],
            "error": "MCP returned no content"
        }


    combined_text = "\n".join(
        text_parts
    ).strip()


    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:

        parsed = json.loads(
            combined_text
        )

        if isinstance(
            parsed,
            dict
        ):

            return parsed

        return {
            "success": True,
            "count": 0,
            "products": parsed
        }

    except json.JSONDecodeError:

        pass


    # --------------------------------------------------------
    # JSON embedded inside text
    # --------------------------------------------------------

    start = combined_text.find("{")
    end = combined_text.rfind("}")


    if start != -1 and end != -1:

        possible_json = combined_text[
            start:end + 1
        ]

        try:

            parsed = json.loads(
                possible_json
            )

            if isinstance(
                parsed,
                dict
            ):

                return parsed

        except json.JSONDecodeError:

            pass


    # --------------------------------------------------------
    # Raw text
    # --------------------------------------------------------

    return {

        "success": True,

        "count": 0,

        "products": [],

        "text": combined_text

    }


# ============================================================
# IMPORTANT COMPATIBILITY FUNCTION
# ============================================================

def extract_mcp_json(result):

    """
    Compatibility function used by app.py.

    app.py imports:

        from mcp_client import run_mcp_tool, extract_mcp_json

    Therefore this function must exist.
    """

    # run_mcp_tool() already returns a dictionary.
    if isinstance(result, dict):

        return result

    return extract_mcp_result(result)


# ============================================================
# ASYNC MCP TOOL CALL
# ============================================================

async def _run_mcp_tool(
    tool_name,
    arguments=None
):

    if arguments is None:

        arguments = {}


    # --------------------------------------------------------
    # CHECK SERVER
    # --------------------------------------------------------

    if not check_server():

        return {

            "success": False,

            "count": 0,

            "products": [],

            "error":
                f"MCP server not found: {SERVER_PATH}"

        }


    log(
        "=================================================="
    )

    log(
        "[MCP CLIENT] STARTING"
    )

    log(
        f"[MCP CLIENT] Python: {sys.executable}"
    )

    log(
        f"[MCP CLIENT] Server: {SERVER_PATH}"
    )

    log(
        f"[MCP CLIENT] Tool: {tool_name}"
    )

    log(
        f"[MCP CLIENT] Arguments: {arguments}"
    )

    log(
        "=================================================="
    )


    # --------------------------------------------------------
    # SERVER PARAMETERS
    # --------------------------------------------------------

    server_params = StdioServerParameters(

        command=sys.executable,

        args=[
            str(SERVER_PATH)
        ]

    )


    try:

        log(
            "[MCP CLIENT] Connecting to server..."
        )


        # ----------------------------------------------------
        # CONNECT TO SERVER
        # ----------------------------------------------------

        async with stdio_client(
            server_params
        ) as (
            read_stream,
            write_stream
        ):

            log(
                "[MCP CLIENT] STDIO CONNECTED"
            )


            # ------------------------------------------------
            # CREATE SESSION
            # ------------------------------------------------

            async with ClientSession(
                read_stream,
                write_stream
            ) as session:


                log(
                    "[MCP CLIENT] INITIALIZING SESSION"
                )


                # --------------------------------------------
                # INITIALIZE
                # --------------------------------------------

                await session.initialize()


                log(
                    "[MCP CLIENT] SESSION INITIALIZED"
                )


                # --------------------------------------------
                # CALL MCP TOOL
                # --------------------------------------------

                result = await session.call_tool(

                    tool_name,

                    arguments=arguments

                )


                log(
                    "[MCP CLIENT] TOOL EXECUTED"
                )


                # --------------------------------------------
                # CONVERT RESULT
                # --------------------------------------------

                data = extract_mcp_result(
                    result
                )


                log(
                    "[MCP CLIENT] RESULT RECEIVED"
                )

                log(
                    f"[MCP CLIENT] RESULT TYPE: {type(data)}"
                )


                return data


    except Exception as e:

        log(
            f"[MCP CLIENT] ERROR: {repr(e)}"
        )


        return {

            "success": False,

            "count": 0,

            "products": [],

            "error": str(e)

        }


# ============================================================
# SYNCHRONOUS WRAPPER
# ============================================================

def run_mcp_tool(
    tool_name,
    arguments=None
):

    """
    Synchronous function used by Streamlit app.py.
    """

    try:

        return asyncio.run(

            _run_mcp_tool(

                tool_name,

                arguments

            )

        )


    except Exception as e:

        log(
            f"[MCP CLIENT] RUN ERROR: {repr(e)}"
        )


        return {

            "success": False,

            "count": 0,

            "products": [],

            "error": str(e)

        }


# ============================================================
# COMPATIBILITY ALIAS
# ============================================================

def call_mcp_tool(
    tool_name,
    arguments=None
):

    return run_mcp_tool(
        tool_name,
        arguments
    )


# ============================================================
# SEARCH PRODUCTS
# ============================================================

def search_products(
    query
):

    return run_mcp_tool(

        "search_products",

        {
            "query": query
        }

    )


# ============================================================
# PRODUCT DETAILS
# ============================================================

def get_product_details(
    product_id
):

    return run_mcp_tool(

        "get_product_details",

        {
            "product_id": product_id
        }

    )


# ============================================================
# LIST CATEGORIES
# ============================================================

def list_categories():

    return run_mcp_tool(

        "list_categories",

        {}

    )


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    log(
        "=========================================="
    )

    log(
        "BUVVAS MCP CLIENT TEST"
    )

    log(
        "=========================================="
    )


    result = search_products(
        "barcode scanner"
    )


    print(

        json.dumps(

            result,

            indent=2,

            ensure_ascii=False

        )

    )
