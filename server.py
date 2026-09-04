try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("BUVVAS Product Server")
except ModuleNotFoundError:
    from mcp.server.mcpserver import MCPServer
    mcp = MCPServer("BUVVAS Product Server")

import requests
import re
import sys


# ============================================================
# MCP SERVER
# ============================================================

PRODUCTS_URL = "https://buvvas.com/products.json?limit=250"


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
# GET PRODUCTS
# ============================================================

def get_products():

    response = requests.get(
        PRODUCTS_URL,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "products",
        []
    )


# ============================================================
# FORMAT PRODUCT
# ============================================================

def format_product(product):

    variants = product.get(
        "variants",
        []
    )

    if variants:

        price = variants[0].get(
            "price",
            "0"
        )

        available = any(
            v.get(
                "available",
                False
            )
            for v in variants
        )

    else:

        price = "0"
        available = False


    images = product.get(
        "images",
        []
    )

    image = ""

    if images:

        image = images[0].get(
            "src",
            ""
        )


    handle = product.get(
        "handle",
        ""
    )


    description = product.get(
        "body_html",
        ""
    )

    description = re.sub(
        r"<[^>]+>",
        " ",
        description
    )

    description = re.sub(
        r"\s+",
        " ",
        description
    ).strip()


    return {

        "id":
            product.get(
                "id"
            ),

        "name":
            product.get(
                "title",
                "BUVVAS Product"
            ),

        "price":
            price,

        "available":
            available,

        "category":
            product.get(
                "product_type",
                ""
            ),

        "vendor":
            product.get(
                "vendor",
                "BUVVAS"
            ),

        "description":
            description,

        "image":
            image,

        "url":
            "https://buvvas.com/products/"
            + handle
    }


# ============================================================
# SEARCH PRODUCTS
# ============================================================

@mcp.tool()
def search_products(
    query: str
) -> dict:

    log(
        f"Searching BUVVAS: {query}"
    )

    try:

        products = get_products()

    except Exception as e:

        log(
            f"Shopify error: {repr(e)}"
        )

        return {
            "success": False,
            "count": 0,
            "products": [],
            "error": str(e)
        }


    query = str(
        query
    ).lower().strip()


    words = [
        w

        for w in re.findall(
            r"[a-zA-Z0-9]+",
            query
        )

        if len(w) > 2
    ]


    results = []


    for product in products:

        title = str(
            product.get(
                "title",
                ""
            )
        ).lower()


        product_type = str(
            product.get(
                "product_type",
                ""
            )
        ).lower()


        description = str(
            product.get(
                "body_html",
                ""
            )
        ).lower()


        score = 0


        if query in title:

            score += 20


        if query in product_type:

            score += 15


        for word in words:

            if word in title:

                score += 10


            if word in product_type:

                score += 8


            if word in description:

                score += 2


        if score > 0:

            results.append(
                (
                    score,
                    product
                )
            )


    results.sort(
        key=lambda x: x[0],
        reverse=True
    )


    formatted = [

        format_product(product)

        for score, product
        in results[:10]

    ]


    log(
        f"Returning {len(formatted)} products"
    )


    return {

        "success": True,

        "count":
            len(formatted),

        "products":
            formatted
    }


# ============================================================
# PRODUCT DETAILS
# ============================================================

@mcp.tool()
def get_product_details(
    product_id: int
) -> dict:

    products = get_products()


    for product in products:

        if str(
            product.get("id")
        ) == str(product_id):

            return format_product(
                product
            )


    return {

        "success": False,

        "error":
            "Product not found"
    }


# ============================================================
# CATEGORIES
# ============================================================

@mcp.tool()
def list_categories() -> dict:

    products = get_products()


    categories = set()


    for product in products:

        category = product.get(
            "product_type",
            ""
        )


        if category:

            categories.add(
                category
            )


    return {

        "success": True,

        "categories":
            sorted(
                list(categories)
            )
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    log(
        "BUVVAS MCP SERVER STARTING"
    )

    mcp.run()