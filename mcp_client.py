import asyncio
import json
import os
import sys
import traceback

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SERVER_PATH = os.path.join(
    BASE_DIR,
    "mcp_server",
    "server.py"
)

PYTHON_EXE = sys.executable


# ============================================================
# PRINT REAL EXCEPTION
# ============================================================

def print_exception_tree(exc, level=0):

    prefix = "  " * level

    print(
        f"{prefix}{type(exc).__name__}: {exc}",
        file=sys.stderr,
        flush=True
    )

    if isinstance(exc, BaseExceptionGroup):

        for child in exc.exceptions:

            print_exception_tree(
                child,
                level + 1
            )


# ============================================================
# MCP CALL
# ============================================================

async def call_mcp_tool(
    tool_name,
    arguments=None
):

    if arguments is None:
        arguments = {}

    print(
        "\n" + "=" * 70,
        file=sys.stderr,
        flush=True
    )

    print(
        "[MCP CLIENT] STARTING",
        file=sys.stderr,
        flush=True
    )

    print(
        f"[MCP CLIENT] Python: {PYTHON_EXE}",
        file=sys.stderr,
        flush=True
    )

    print(
        f"[MCP CLIENT] Server: {SERVER_PATH}",
        file=sys.stderr,
        flush=True
    )

    print(
        f"[MCP CLIENT] Tool: {tool_name}",
        file=sys.stderr,
        flush=True
    )

    print(
        f"[MCP CLIENT] Arguments: {arguments}",
        file=sys.stderr,
        flush=True
    )

    print(
        "=" * 70,
        file=sys.stderr,
        flush=True
    )


    server_params = StdioServerParameters(

        command=PYTHON_EXE,

        args=[
            SERVER_PATH
        ],

        env={
            **os.environ
        }
    )


    try:

        print(
            "[MCP CLIENT] Connecting to server...",
            file=sys.stderr,
            flush=True
        )

        async with stdio_client(
            server_params
        ) as (
            read_stream,
            write_stream
        ):

            print(
                "[MCP CLIENT] STDIO CONNECTED",
                file=sys.stderr,
                flush=True
            )


            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                print(
                    "[MCP CLIENT] INITIALIZING SESSION",
                    file=sys.stderr,
                    flush=True
                )


                await session.initialize()


                print(
                    "[MCP CLIENT] SESSION INITIALIZED",
                    file=sys.stderr,
                    flush=True
                )


                print(
                    "[MCP CLIENT] CALLING TOOL...",
                    file=sys.stderr,
                    flush=True
                )


                result = await session.call_tool(
                    tool_name,
                    arguments
                )


                print(
                    "[MCP CLIENT] TOOL SUCCESS",
                    file=sys.stderr,
                    flush=True
                )


                return result


    except BaseExceptionGroup as eg:

        print(
            "\n[MCP CLIENT] REAL TASKGROUP ERROR:",
            file=sys.stderr,
            flush=True
        )

        print_exception_tree(
            eg
        )

        print(
            "\n[MCP CLIENT] FULL TRACEBACK:",
            file=sys.stderr,
            flush=True
        )

        traceback.print_exception(
            eg,
            file=sys.stderr
        )

        raise


    except Exception as e:

        print(
            "\n[MCP CLIENT] REAL ERROR:",
            file=sys.stderr,
            flush=True
        )

        print(
            f"{type(e).__name__}: {e}",
            file=sys.stderr,
            flush=True
        )

        traceback.print_exc(
            file=sys.stderr
        )

        raise


# ============================================================
# SYNC WRAPPER
# ============================================================

def run_mcp_tool(
    tool_name,
    arguments=None
):

    return asyncio.run(
        call_mcp_tool(
            tool_name,
            arguments
        )
    )


# ============================================================
# EXTRACT TEXT
# ============================================================

def extract_mcp_text(result):

    if not result:
        return ""

    try:

        for item in result.content:

            if hasattr(
                item,
                "text"
            ):

                return item.text

    except Exception:
        pass

    return ""


# ============================================================
# EXTRACT JSON
# ============================================================

def extract_mcp_json(result):

    text = extract_mcp_text(
        result
    )

    if not text:

        return {}

    try:

        return json.loads(
            text
        )

    except json.JSONDecodeError:

        return {
            "success": False,
            "error": text
        }