import streamlit as st
import re
import html

from mcp_client import run_mcp_tool, extract_mcp_json


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="BUVVAS AI Shopping Assistant",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_products" not in st.session_state:
    st.session_state.last_products = []

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All"

if "comparison_products" not in st.session_state:
    st.session_state.comparison_products = []

if "show_comparison" not in st.session_state:
    st.session_state.show_comparison = False

if "cheaper_results" not in st.session_state:
    st.session_state.cheaper_results = []

if "cheaper_for" not in st.session_state:
    st.session_state.cheaper_for = ""


# ============================================================
# CSS
# ============================================================

st.html("""
<style>

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, #15112c 0%, #090a18 38%, #050611 100%);
    color: white;
}

[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
}

[data-testid="stToolbar"] {
    visibility: hidden;
}

.block-container {
    padding-top: 70px !important;
    padding-bottom: 40px !important;
    max-width: 1250px !important;
}

/* ================= NAVBAR ================= */

.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px;
    margin-bottom: 35px;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    background: rgba(18,20,36,0.82);
    backdrop-filter: blur(14px);
}

.nav-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo {
    font-size: 23px;
    font-weight: 800;
    color: white;
}

.logo-icon {
    font-size: 26px;
}

.nav-right {
    display: flex;
    gap: 28px;
    color: #c8c9d7;
    font-size: 14px;
}

.nav-right span:hover {
    color: white;
}

/* ================= HERO ================= */

.hero {
    text-align: center;
    padding: 30px 20px 20px 20px;
}

.badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 30px;
    background: rgba(123,76,255,0.14);
    border: 1px solid rgba(150,110,255,0.35);
    color: #c7b5ff;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.hero h1 {
    font-size: 48px;
    line-height: 1.1;
    margin: 18px 0 12px 0;
    font-weight: 850;
    background: linear-gradient(90deg, #ffffff, #bba4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    font-size: 18px;
    color: #aaaabd;
    margin-bottom: 25px;
}

/* ================= CATEGORY ================= */

.category-title {
    font-size: 14px;
    color: #a7a8b8;
    font-weight: 700;
    margin-bottom: 8px;
}

.category-active {
    color: #ffffff !important;
}

/* ================= CHAT ================= */

.chat-user {
    background: rgba(22,24,43,0.92);
    border: 1px solid rgba(130,100,255,0.22);
    border-radius: 18px;
    padding: 22px 26px;
    margin: 25px 0;
    font-size: 17px;
    font-weight: 700;
}

.chat-user-icon {
    font-size: 22px;
    margin-right: 12px;
}

.chat-answer {
    font-size: 18px;
    font-weight: 600;
    color: white;
    margin: 20px 0;
}

/* ================= PRODUCT CARD ================= */

.product-card {
    background:
        linear-gradient(
            145deg,
            rgba(17,19,35,0.98),
            rgba(8,9,23,0.98)
        );
    border: 1px solid rgba(160,160,190,0.28);
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 20px;
    min-height: 420px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.28);
}

.product-image-box {
    width: 100%;
    height: 300px;
    border-radius: 12px;
    overflow: hidden;
    background: #eeeeee;
    display: flex;
    align-items: center;
    justify-content: center;
}

.product-image-box img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.product-name {
    font-size: 20px;
    line-height: 1.35;
    font-weight: 800;
    color: #ffffff;
    margin: 12px 0;
}

.product-price {
    font-size: 28px;
    font-weight: 900;
    color: #9f78ff;
    margin: 10px 0;
}

.stock-in {
    color: #35df7a;
    font-weight: 700;
    font-size: 14px;
}

.stock-out {
    color: #ff6868;
    font-weight: 700;
    font-size: 14px;
}

.product-category {
    color: #c5c6d5;
    font-size: 14px;
    margin: 14px 0;
}

.info-box {
    background: rgba(26,28,45,0.75);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 15px;
    margin-top: 12px;
    color: #e4e4ed;
    line-height: 1.5;
}

/* ================= BUTTONS ================= */

div.stButton > button {
    width: 100%;
    min-height: 42px;
    border-radius: 11px;
    border: 1px solid rgba(160,160,190,0.28);
    background: #141622;
    color: white;
    font-weight: 700;
    transition: 0.2s;
}

div.stButton > button:hover {
    border-color: #9570ff;
    background: #1b1c2b;
    color: white;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #7146dc, #9369ff);
    border: none;
    color: white;
}

/* ================= SEARCH ================= */

.search-box {
    margin-top: 25px;
    margin-bottom: 10px;
}

/* ================= COMPARISON ================= */

.compare-box {
    background: rgba(18,20,37,0.95);
    border: 1px solid rgba(140,110,255,0.35);
    border-radius: 18px;
    padding: 22px;
    margin-top: 25px;
}

.compare-title {
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 18px;
}

/* ================= CHEAPER ================= */

.cheaper-section {
    background: rgba(18,20,37,0.95);
    border: 1px solid rgba(53,223,122,0.25);
    border-radius: 18px;
    padding: 22px;
    margin: 30px 0;
}

.cheaper-subtitle {
    color: #a5a6b7;
    font-size: 14px;
    margin-bottom: 18px;
}

/* ================= EMPTY ================= */

.empty-box {
    text-align: center;
    padding: 50px 20px;
    color: #a5a6b7;
    border: 1px dashed rgba(255,255,255,0.15);
    border-radius: 16px;
}

/* ================= FOOTER ================= */

.footer {
    text-align: center;
    color: #77798b;
    font-size: 13px;
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.07);
}

</style>
""")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_product_price(product):
    """Convert product price safely to float."""

    try:
        price = product.get("price", 0)

        if isinstance(price, str):
            price = (
                price
                .replace("₹", "")
                .replace(",", "")
                .replace("INR", "")
                .strip()
            )

        return float(price)

    except Exception:
        return 0.0


def format_price(price):
    """Format price as Indian rupee."""

    try:
        return f"₹{float(price):,.0f}"
    except Exception:
        return "₹0"


def is_available(product):
    """Safely determine product availability."""

    value = product.get("available", False)

    if isinstance(value, bool):
        return value

    return str(value).lower() in [
        "true",
        "yes",
        "1",
        "available",
        "in stock"
    ]


def extract_budget(query):
    """
    Detect budgets from natural language.

    Examples:
    under 2000
    below 5000
    less than 3000
    within 1500
    upto 2000
    up to 2000
    maximum 3000
    max 3000
    """

    query_lower = query.lower()

    query_lower = query_lower.replace(",", "")
    query_lower = query_lower.replace("₹", "")
    query_lower = query_lower.replace("rs.", "")
    query_lower = query_lower.replace("rs", "")
    query_lower = query_lower.replace("inr", "")

    patterns = [
        r"under\s*(\d+(?:\.\d+)?)",
        r"below\s*(\d+(?:\.\d+)?)",
        r"less\s+than\s*(\d+(?:\.\d+)?)",
        r"within\s*(\d+(?:\.\d+)?)",
        r"upto\s*(\d+(?:\.\d+)?)",
        r"up\s+to\s*(\d+(?:\.\d+)?)",
        r"maximum\s*(\d+(?:\.\d+)?)",
        r"max\s*(\d+(?:\.\d+)?)",
        r"budget\s*(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, query_lower)

        if match:
            return float(match.group(1))

    return None


def extract_category(query):
    """Detect product category from user query."""

    q = query.lower()

    # Printer
    if (
        "printer" in q
        or "printing" in q
        or "label printer" in q
        or "receipt printer" in q
        or "thermal printer" in q
    ):
        return "Printer"

    # Barcode
    if (
        "barcode" in q
        or "scanner" in q
        or "barcode scanner" in q
    ):
        return "Barcode"

    # Cash drawer
    if (
        "cash drawer" in q
        or "cashdraw" in q
        or "cash box" in q
    ):
        return "Cash Drawer"

    # POS
    if (
        re.search(r"\bpos\b", q)
        or "point of sale" in q
        or "pos system" in q
        or "touch pos" in q
    ):
        return "POS"

    return "All"


def strict_category_match(product, category):
    """
    Strict category filtering.

    IMPORTANT:
    Description is NOT used here because a barcode printer
    can contain the word 'barcode' in its description.
    """

    if category == "All":
        return True

    name = str(product.get("name", "")).lower()
    product_type = str(product.get("category", "")).lower()

    text = f"{name} {product_type}"

    if category == "Printer":

        return (
            "printer" in name
            or "printer" in product_type
            or "printer" in text
        )

    if category == "Barcode":

        # Barcode scanners should not be mixed with printers.
        if "printer" in name:
            return False

        if "printer" in product_type:
            return False

        return (
            "barcode scanner" in name
            or "barcode scanner" in product_type
            or "scanner" in name
            or "scanner" in product_type
        )

    if category == "Cash Drawer":

        return (
            "cash drawer" in name
            or "cash drawer" in product_type
        )

    if category == "POS":

        return (
            "pos" in name
            or "point of sale" in name
            or "pos" in product_type
            or "point of sale" in product_type
        )

    return True


def filter_products(products, category="All", max_price=None, stock_only=False):
    """Apply category, budget and stock filters."""

    result = []

    for product in products:

        # Category
        if not strict_category_match(product, category):
            continue

        # Price
        if max_price is not None:

            price = get_product_price(product)

            if price <= 0:
                continue

            if price > max_price:
                continue

        # Stock
        if stock_only and not is_available(product):
            continue

        result.append(product)

    return result


def sort_products(products, sort_option):
    """Sort product list."""

    if sort_option == "Price: Low to High":
        return sorted(
            products,
            key=lambda p: get_product_price(p)
        )

    if sort_option == "Price: High to Low":
        return sorted(
            products,
            key=lambda p: get_product_price(p),
            reverse=True
        )

    if sort_option == "Name: A-Z":
        return sorted(
            products,
            key=lambda p: str(p.get("name", "")).lower()
        )

    return products


def clean_text(text):
    """Escape text for HTML."""

    if text is None:
        return ""

    return html.escape(str(text))


def get_description(product):
    """Get a clean product description."""

    description = product.get("description", "")

    if not description:
        return "BUVVAS product."

    # Remove remaining HTML
    description = re.sub(r"<[^>]+>", " ", str(description))

    # Clean spaces
    description = re.sub(r"\s+", " ", description).strip()

    # Keep cards readable
    if len(description) > 350:
        description = description[:350] + "..."

    return description


def call_search(query):
    """Call MCP search_products."""

    try:

        result = run_mcp_tool(
            "search_products",
            {
                "query": query
            }
        )

        data = extract_mcp_json(result)

        if not isinstance(data, dict):
            return []

        return data.get("products", [])

    except Exception as e:

        st.error(f"MCP Error: {e}")

        return []


def get_search_products(query):
    """
    Search MCP and apply our application-level filters.

    This is important because the MCP server currently performs
    keyword search, while app.py handles natural-language
    requirements such as price limits.
    """

    category = extract_category(query)
    max_price = extract_budget(query)

    # Use a clean MCP query.
    # MCP does not need to understand "under 2000".
    if category == "Printer":
        mcp_query = "printer"

    elif category == "Barcode":
        mcp_query = "barcode scanner"

    elif category == "Cash Drawer":
        mcp_query = "cash drawer"

    elif category == "POS":
        mcp_query = "POS"

    else:
        mcp_query = query

    products = call_search(mcp_query)

    # Apply strict category and budget filtering
    products = filter_products(
        products,
        category=category,
        max_price=max_price,
        stock_only=False
    )

    return products, category, max_price


# ============================================================
# PRODUCT EXPLANATION
# ============================================================

def product_reason(product, query=""):
    """Generate a simple explanation for Why this product."""

    name = str(product.get("name", "BUVVAS Product"))
    price = get_product_price(product)
    available = is_available(product)
    category = product.get("category", "")

    reasons = []

    if price > 0:
        reasons.append(f"priced at {format_price(price)}")

    if available:
        reasons.append("currently in stock")
    else:
        reasons.append("currently unavailable")

    if category:
        reasons.append(f"category: {category}")

    if "printer" in name.lower():
        reasons.append("suitable for printing requirements")

    elif "scanner" in name.lower():
        reasons.append("suitable for barcode scanning")

    elif "cash drawer" in name.lower():
        reasons.append("suitable for retail cash management")

    elif "pos" in name.lower():
        reasons.append("suitable for POS operations")

    return (
        "This product matches your request because it is "
        + ", ".join(reasons)
        + "."
    )


# ============================================================
# FIND CHEAPER ALTERNATIVES
# ============================================================

def find_cheaper_products(product):
    """
    Search the same category and return products cheaper
    than the selected product.

    Uses the existing search_products MCP tool, so no new
    MCP server tool is required.
    """

    original_price = get_product_price(product)

    if original_price <= 0:
        return []

    name = str(product.get("name", "")).lower()
    category = str(product.get("category", "")).lower()

    if "printer" in name or "printer" in category:
        search_query = "printer"
        detected_category = "Printer"

    elif "scanner" in name or "barcode" in name or "scanner" in category:
        search_query = "barcode scanner"
        detected_category = "Barcode"

    elif "cash drawer" in name or "cash drawer" in category:
        search_query = "cash drawer"
        detected_category = "Cash Drawer"

    elif "pos" in name or "pos" in category:
        search_query = "POS"
        detected_category = "POS"

    else:
        return []

    candidates = call_search(search_query)

    cheaper = []

    original_id = str(product.get("id", ""))

    for candidate in candidates:

        candidate_id = str(candidate.get("id", ""))

        if candidate_id == original_id:
            continue

        if not strict_category_match(candidate, detected_category):
            continue

        candidate_price = get_product_price(candidate)

        if candidate_price <= 0:
            continue

        if candidate_price < original_price:
            cheaper.append(candidate)

    cheaper.sort(
        key=lambda p: get_product_price(p)
    )

    return cheaper


# ============================================================
# PRODUCT CARD
# ============================================================

def render_product(product, index, message_key):
    """Render one product card."""

    name = clean_text(
        product.get("name", "BUVVAS Product")
    )

    price = get_product_price(product)
    available = is_available(product)

    category = clean_text(
        product.get("category", "")
    )

    image = product.get("image", "")
    url = product.get("url", "")

    if image:
        image_html = f"""
        <img src="{html.escape(image)}"
             alt="{name}">
        """
    else:
        image_html = """
        <div style="
            color:#777;
            font-size:18px;
            text-align:center;
        ">
            📦<br>
            No Image
        </div>
        """

    stock_html = (
        '<div class="stock-in">● In Stock</div>'
        if available
        else
        '<div class="stock-out">● Out of Stock</div>'
    )

    st.html(f"""
    <div class="product-card">

        <div class="product-image-box">
            {image_html}
        </div>

        <div class="product-name">
            {name}
        </div>

        <div class="product-price">
            {format_price(price)}
        </div>

        {stock_html}

        <div class="product-category">
            Category: {category if category else "BUVVAS Product"}
        </div>

    </div>
    """)

    if url:
        st.link_button(
            "🛒 View Product",
            url,
            use_container_width=True
        )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💡 Why this product?",
            key=f"why_{message_key}_{index}",
            use_container_width=True
        ):

            st.info(
                product_reason(
                    product,
                    st.session_state.get("current_query", "")
                )
            )

    with col2:

        if st.button(
            "💸 Find Cheaper",
            key=f"cheaper_{message_key}_{index}",
            use_container_width=True
        ):

            with st.spinner("Finding cheaper alternatives..."):
                cheaper = find_cheaper_products(product)

            st.session_state.cheaper_results = cheaper
            st.session_state.cheaper_for = product.get(
                "name",
                "selected product"
            )

            st.rerun()


def render_cheaper_section():
    """Render cheaper alternatives independently of main filters."""

    cheaper_results = st.session_state.get(
        "cheaper_results", []
    )

    cheaper_for = st.session_state.get(
        "cheaper_for", "selected product"
    )

    if not cheaper_results:
        return

    st.markdown("---")

    st.markdown(
        f"""
        <div class="cheaper-section">
            <div class="compare-title">💸 Cheaper alternatives</div>
            <div class="cheaper-subtitle">
                Lower-priced BUVVAS products found for:
                <strong>{clean_text(cheaper_for)}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    cols_per_row = 2

    for start in range(0, len(cheaper_results), cols_per_row):

        row_products = cheaper_results[start:start + cols_per_row]
        cols = st.columns(len(row_products))

        for col_index, cheaper_product in enumerate(row_products):

            with cols[col_index]:
                render_product(
                    cheaper_product,
                    start + col_index,
                    "cheaper"
                )


# ============================================================
# COMPARISON
# ============================================================

def render_comparison(products):
    """Display selected products comparison."""

    if not products:
        return

    st.markdown(
        '<div class="compare-box">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="compare-title">⚖️ Product Comparison</div>',
        unsafe_allow_html=True
    )

    for product in products:

        name = product.get(
            "name",
            "BUVVAS Product"
        )

        price = get_product_price(product)

        available = (
            "In Stock"
            if is_available(product)
            else "Out of Stock"
        )

        category = product.get(
            "category",
            "—"
        )

        st.markdown(
            f"""
            <div class="info-box">
                <strong>{clean_text(name)}</strong><br><br>
                💰 Price: <strong>{format_price(price)}</strong><br>
                📦 Stock: {clean_text(available)}<br>
                🏷️ Category: {clean_text(category)}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# NAVBAR
# ============================================================

st.html("""
<div class="navbar">

    <div class="nav-left">
        <span class="logo-icon">🛒</span>
        <span class="logo">BUVVAS</span>
    </div>

    <div class="nav-right">
        <span>Home</span>
        <span>Products</span>
        <span>Categories</span>
        <span>Support</span>
    </div>

</div>
""")


# ============================================================
# HERO
# ============================================================

st.html("""
<div class="hero">

    <div class="badge">
        ✨ AI POWERED BY MCP
    </div>

    <h1>Your AI Shopping Assistant</h1>

    <p>
        Find products smarter. Shop faster.
    </p>

</div>
""")


# ============================================================
# CATEGORY BUTTONS
# ============================================================

st.markdown(
    '<div class="category-title">Browse by category</div>',
    unsafe_allow_html=True
)

cat1, cat2, cat3, cat4, cat5 = st.columns(5)

categories = [
    ("All", "All"),
    ("📷 Barcode", "Barcode"),
    ("🖨️ Printer", "Printer"),
    ("💰 Cash Drawer", "Cash Drawer"),
    ("🖥️ POS", "POS"),
]

category_columns = [cat1, cat2, cat3, cat4, cat5]


def perform_category_search(category):

    category_queries = {
        "All": "products",
        "Printer": "printer",
        "Barcode": "barcode scanner",
        "Cash Drawer": "cash drawer",
        "POS": "POS"
    }

    query = category_queries.get(
        category,
        category
    )

    products = call_search(query)

    products = filter_products(
        products,
        category=category,
        max_price=None,
        stock_only=False
    )

    display_names = {
        "All": "products",
        "Printer": "printers",
        "Barcode": "barcode scanners",
        "Cash Drawer": "cash drawers",
        "POS": "POS systems"
    }

    display_name = display_names.get(
        category,
        "products"
    )

    # IMPORTANT:
    # Clear old messages so previous category products
    # don't remain on screen.
    st.session_state.messages = [
        {
            "role": "user",
            "content": f"Show me {display_name}"
        },
        {
            "role": "assistant",
            "content": (
                f"I found {len(products)} "
                f"{display_name} for you."
            ),
            "products": products,
            "category": category,
            "max_price": None
        }
    ]

    st.session_state.last_products = products
    st.session_state.selected_category = category
    st.session_state.current_query = f"Show me {display_name}"

    st.session_state.cheaper_results = []
    st.session_state.cheaper_for = ""

    st.rerun()


for col, (label, category) in zip(
    category_columns,
    categories
):

    with col:

        if st.button(
            label,
            key=f"category_{category}",
            use_container_width=True
        ):

            perform_category_search(category)


# ============================================================
# SEARCH AREA
# ============================================================

st.markdown("")

user_query = st.text_input(
    "",
    placeholder=(
        "Ask me anything... "
        "e.g. I need a printer under 2000"
    ),
    key="search_input"
)


# ============================================================
# SEARCH BUTTON
# ============================================================

search_col1, search_col2, search_col3 = st.columns(
    [1, 2, 1]
)

with search_col2:

    search_clicked = st.button(
        "🔍 Search Products",
        type="primary",
        use_container_width=True
    )


# ============================================================
# PROCESS SEARCH
# ============================================================

if search_clicked and user_query.strip():

    query = user_query.strip()

    st.session_state.current_query = query

    with st.spinner("🤖 MCP is searching BUVVAS products..."):

        products, category, max_price = get_search_products(
            query
        )

    # Clear category-specific old messages.
    st.session_state.messages = []

    # Build response text
    if max_price is not None:

        if products:

            answer = (
                f"I found {len(products)} BUVVAS "
                f"products under "
                f"{format_price(max_price)} "
                f"that match your request."
            )

        else:

            answer = (
                f"I couldn't find any matching "
                f"products under "
                f"{format_price(max_price)}."
            )

    else:

        if products:

            answer = (
                f"I found {len(products)} BUVVAS "
                f"products that match your request."
            )

        else:

            answer = (
                "I couldn't find products matching "
                "your request."
            )

    # Save messages
    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "products": products,
            "category": category,
            "max_price": max_price
        }
    )

    st.session_state.last_products = products
    st.session_state.selected_category = category

    st.session_state.cheaper_results = []
    st.session_state.cheaper_for = ""

    st.rerun()


# ============================================================
# FILTER / SORT CONTROLS
# ============================================================

if st.session_state.last_products:

    st.markdown("---")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:

        stock_only = st.checkbox(
            "📦 Show only in-stock products",
            value=False
        )

    with filter_col2:

        sort_option = st.selectbox(
            "Sort products",
            [
                "Recommended",
                "Price: Low to High",
                "Price: High to Low",
                "Name: A-Z"
            ]
        )

    with filter_col3:

        selected_budget = st.number_input(
            "Maximum price filter (₹)",
            min_value=0,
            value=0,
            step=500
        )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message_index, message in enumerate(
    st.session_state.messages
):

    role = message.get("role")

    if role == "user":

        st.html(f"""
        <div class="chat-user">
            <span class="chat-user-icon">👤</span>
            {clean_text(message.get("content", ""))}
        </div>
        """)

    elif role == "assistant":

        st.html(f"""
        <div class="chat-answer">
            {clean_text(message.get("content", ""))}
        </div>
        """)

        products = message.get(
            "products",
            []
        )

        # IMPORTANT:
        # Use the category stored in THIS message.
        # Do not use the current global category.
        message_category = message.get(
            "category",
            "All"
        )

        message_max_price = message.get(
            "max_price",
            None
        )

        # The search/category functions already applied the
        # message category and natural-language budget.
        # Do not apply those filters a second time here.
        display_products = list(products)

        # User-selected filters
        if st.session_state.get(
            "last_products"
        ):

            if "stock_only" in locals() and stock_only:

                display_products = [
                    p for p in display_products
                    if is_available(p)
                ]

            if (
                "selected_budget" in locals()
                and selected_budget > 0
            ):

                display_products = [
                    p for p in display_products
                    if (
                        get_product_price(p) > 0
                        and
                        get_product_price(p)
                        <= selected_budget
                    )
                ]

            if "sort_option" in locals():

                display_products = sort_products(
                    display_products,
                    sort_option
                )

        if display_products:

            # Number of columns
            cols_per_row = 2

            for start in range(
                0,
                len(display_products),
                cols_per_row
            ):

                row_products = display_products[
                    start:start + cols_per_row
                ]

                cols = st.columns(
                    len(row_products)
                )

                for col_index, product in enumerate(
                    row_products
                ):

                    with cols[col_index]:

                        render_product(
                            product,
                            start + col_index,
                            f"{message_index}"
                        )

        else:

            if products:

                st.html("""
                <div class="empty-box">
                    No products match the current filters.
                </div>
                """)


# ============================================================
# CHEAPER ALTERNATIVES SECTION
# ============================================================

# Render cheaper alternatives outside the normal message/filter loop.
render_cheaper_section()


# ============================================================
# COMPARISON SECTION
# ============================================================

if st.session_state.comparison_products:

    render_comparison(
        st.session_state.comparison_products
    )


# ============================================================
# FOOTER
# ============================================================

st.html("""
<div class="footer">
    BUVVAS AI Shopping Assistant • Powered by MCP
</div>
""")