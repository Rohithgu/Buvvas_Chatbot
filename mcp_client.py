import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# PATH CONFIGURATION
# ============================================================

# Get the folder where this mcp_client.py file exists
BASE_DIR = Path(__file__).resolve().parent

# Your server.py is in the SAME folder as mcp_client.py
SERVER_PATH = BASE_DIR / "server.py"


# ============================================================
# LOGGING
# ============================================================

def log(message):
    """
    Print logs to stderr so they appear in Streamlit logs
    without interfering with MCP communication.
    """

    print(
        message,
        file=sys.stderr,
        flush=True
    )


# ============================================================
# CHECK SERVER FILE
# ============================================================

def check_server():

    log(
        f"[MCP CLIENT] Looking for server: {SERVER_PATH}"
    )

    if not SERVER_PATH.exists():

        log(
            f"[MCP CLIENT] ERROR: server.py not found!"
        )

        return False

    log(
        "[MCP CLIENT] server.py found successfully"
    )

    return True


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
            "error": (
                f"MCP server not found: {SERVER_PATH}"
            )
        }


    log(
        "[MCP CLIENT] STARTING"
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


    # --------------------------------------------------------
    # START MCP SERVER
    # --------------------------------------------------------

    server_params = StdioServerParameters(

        command=sys.executable,

        args=[
            str(SERVER_PATH)
        ]

    )


    try:

        # ----------------------------------------------------
        # CONNECT TO MCP SERVER
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
            # CREATE MCP SESSION
            # ------------------------------------------------

            async with ClientSession(
                read_stream,
                write_stream
            ) as session:


                log(
                    "[MCP CLIENT] Initializing session..."
                )


                # --------------------------------------------
                # INITIALIZE MCP
                # --------------------------------------------

                await session.initialize()


                log(
                    "[MCP CLIENT] MCP SESSION INITIALIZED"
                )


                # --------------------------------------------
                # CALL TOOL
                # --------------------------------------------

                result = await session.call_tool(

                    tool_name,

                    arguments=arguments

                )


                log(
                    "[MCP CLIENT] TOOL EXECUTED"
                )


                # --------------------------------------------
                # EXTRACT RESULT
                # --------------------------------------------

                return extract_mcp_result(
                    result
                )


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
# EXTRACT MCP RESULT
# ============================================================

def extract_mcp_result(result):

    """
    Convert MCP CallToolResult into normal Python data.
    """

    if result is None:

        return {
            "success": False,
            "count": 0,
            "products": [],
            "error": "Empty MCP response"
        }


    # --------------------------------------------------------
    # Check structured content
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
    # Extract normal MCP content
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


    # --------------------------------------------------------
    # Nothing returned
    # --------------------------------------------------------

    if not text_parts:

        return {

            "success": False,

            "count": 0,

            "products": [],

            "error": "MCP returned no content"

        }


    # --------------------------------------------------------
    # Combine text
    # --------------------------------------------------------

    combined_text = "\n".join(
        text_parts
    ).strip()


    # --------------------------------------------------------
    # Try JSON
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
    # Try extracting JSON from text
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
    # Return raw text
    # --------------------------------------------------------

    return {

        "success": True,

        "count": 0,

        "products": [],

        "text": combined_text

    }


# ============================================================
# SYNCHRONOUS MCP TOOL FUNCTION
# ============================================================

def run_mcp_tool(
    tool_name,
    arguments=None
):

    """
    Synchronous wrapper used by Streamlit.
    """

    try:

        return asyncio.run(
            _run_mcp_tool(
                tool_name,
                arguments
            )
        )

    except RuntimeError as e:

        # ----------------------------------------------------
        # Handle an already running asyncio event loop
        # ----------------------------------------------------

        log(
            f"[MCP CLIENT] Runtime error: {repr(e)}"
        )

        return {

            "success": False,

            "count": 0,

            "products": [],

            "error": str(e)

        }


# ============================================================
# ALIAS
# ============================================================

def call_mcp_tool(
    tool_name,
    arguments=None
):

    """
    Alias in case app.py uses call_mcp_tool().
    """

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
# GET PRODUCT DETAILS
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
# TEST
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
