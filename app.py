# ============================================================
# SUPERSTORE EXECUTIVE BUSINESS PERFORMANCE DASHBOARD
# STREAMLIT APPLICATION
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import db_utils


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Superstore Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. PROFESSIONAL COLOR SYSTEM
# ============================================================

NAVY = "#1F3864"

BLUE = "#4472C4"
LIGHT_BLUE = "#5B9BD5"

GREEN = "#70AD47"
RED = "#C00000"

ORANGE = "#ED7D31"
TEAL = "#2F75B2"

GRID = "#E6EAF0"


# ============================================================
# 3. CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */
    .stApp {
        background-color: #F7F9FC;
    }

    /* Dashboard title */
    .dashboard-title {
        font-size: 30px;
        font-weight: 700;
        color: #1F3864;
        text-align: center;
        margin-bottom: 5px;
    }

    .dashboard-subtitle {
        font-size: 14px;
        color: #64748B;
        text-align: center;
        margin-bottom: 25px;
    }

    /* KPI cards */
    .kpi-card {
        background-color: white;
        border-radius: 10px;
        padding: 18px 20px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        min-height: 120px;
    }

    .kpi-title {
        color: #64748B;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .kpi-value {
        color: #1F3864;
        font-size: 28px;
        font-weight: 700;
        margin-top: 8px;
    }

    /* Section headings */
    .section-title {
        color: #1F3864;
        font-size: 19px;
        font-weight: 650;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 4. DATA LOADING
# ============================================================

@st.cache_data(ttl=300)
def load_data():

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    kpi_query = """
    SELECT
        SUM(i.sales) AS "Total Revenue",
        SUM(i.profit) AS "Total Profit",
        ROUND(
            SUM(i.profit) /
            NULLIF(SUM(i.sales), 0) * 100,
            2
        ) AS "Profit Margin %",
        COUNT(DISTINCT i.order_id) AS "Total Orders"
    FROM superstore.order_items i;
    """

    kpi_df = db_utils.run_pg_query(kpi_query)


    # --------------------------------------------------------
    # MONTHLY PERFORMANCE
    # --------------------------------------------------------

    monthly_query = """
    SELECT
        TO_CHAR(o.order_date, 'YYYY-MM') AS month,
        SUM(i.sales) AS revenue,
        SUM(i.profit) AS profit
    FROM superstore.orders o
    JOIN superstore.order_items i
        ON o.order_id = i.order_id
    GROUP BY
        TO_CHAR(o.order_date, 'YYYY-MM')
    ORDER BY
        month;
    """

    monthly_df = db_utils.run_pg_query(monthly_query)


    # --------------------------------------------------------
    # CATEGORY PERFORMANCE
    # --------------------------------------------------------

    category_query = """
    SELECT
        p.category,
        SUM(i.sales) AS revenue,
        SUM(i.profit) AS profit,
        ROUND(
            SUM(i.profit) /
            NULLIF(SUM(i.sales), 0) * 100,
            2
        ) AS profit_margin
    FROM superstore.order_items i
    JOIN superstore.products p
        ON i.product_key = p.product_key
    GROUP BY
        p.category
    ORDER BY
        profit DESC;
    """

    category_df = db_utils.run_pg_query(category_query)


    # --------------------------------------------------------
    # FURNITURE
    # --------------------------------------------------------

    furniture_query = """
    SELECT
        p.sub_category,
        SUM(i.sales) AS revenue,
        SUM(i.profit) AS profit,
        ROUND(
            SUM(i.profit) /
            NULLIF(SUM(i.sales), 0) * 100,
            2
        ) AS profit_margin
    FROM superstore.order_items i
    JOIN superstore.products p
        ON i.product_key = p.product_key
    WHERE
        p.category = 'Furniture'
    GROUP BY
        p.sub_category
    ORDER BY
        profit DESC;
    """

    furniture_df = db_utils.run_pg_query(furniture_query)


    # --------------------------------------------------------
    # TOP REVENUE CUSTOMERS
    # --------------------------------------------------------

    top_revenue_query = """
    SELECT
        c.customer_name,
        SUM(i.sales) AS revenue,
        SUM(i.profit) AS profit
    FROM superstore.orders o
    JOIN superstore.customers c
        ON o.customer_id = c.customer_id
    JOIN superstore.order_items i
        ON o.order_id = i.order_id
    GROUP BY
        c.customer_name
    ORDER BY
        revenue DESC
    LIMIT 10;
    """

    top_revenue_customers_df = db_utils.run_pg_query(
        top_revenue_query
    )


    # --------------------------------------------------------
    # TOP PROFIT CUSTOMERS
    # --------------------------------------------------------

    top_profit_query = """
    SELECT
        c.customer_name,
        SUM(i.sales) AS revenue,
        SUM(i.profit) AS profit
    FROM superstore.orders o
    JOIN superstore.customers c
        ON o.customer_id = c.customer_id
    JOIN superstore.order_items i
        ON o.order_id = i.order_id
    GROUP BY
        c.customer_name
    ORDER BY
        profit DESC
    LIMIT 10;
    """

    top_profit_customers_df = db_utils.run_pg_query(
        top_profit_query
    )


    # --------------------------------------------------------
    # LOSS-MAKING CUSTOMERS
    # --------------------------------------------------------

    customer_loss_query = """
    SELECT
        c.customer_name,
        SUM(i.sales) AS revenue,
        SUM(i.profit) AS profit
    FROM superstore.orders o
    JOIN superstore.customers c
        ON o.customer_id = c.customer_id
    JOIN superstore.order_items i
        ON o.order_id = i.order_id
    GROUP BY
        c.customer_name
    HAVING
        SUM(i.profit) < 0
    ORDER BY
        profit ASC
    LIMIT 10;
    """

    customer_loss_df = db_utils.run_pg_query(
        customer_loss_query
    )


    # --------------------------------------------------------
    # ORDERS BY CATEGORY
    # --------------------------------------------------------

    orders_category_query = """
    SELECT
        p.category AS "Category",
        COUNT(DISTINCT i.order_id) AS "Total Orders"
    FROM superstore.order_items i
    JOIN superstore.products p
        ON i.product_key = p.product_key
    GROUP BY
        p.category
    ORDER BY
        "Total Orders" DESC;
    """

    orders_category_df = db_utils.run_pg_query(
        orders_category_query
    )


    # --------------------------------------------------------
    # ORDERS BY REGION
    # --------------------------------------------------------

    orders_region_query = """
    SELECT
        o.region AS "Region",
        COUNT(DISTINCT o.order_id) AS "Total Orders"
    FROM superstore.orders o
    GROUP BY
        o.region
    ORDER BY
        "Total Orders" DESC;
    """

    orders_region_df = db_utils.run_pg_query(
        orders_region_query
    )


    # --------------------------------------------------------
    # ORDERS BY STATE
    # --------------------------------------------------------

    orders_state_query = """
    SELECT
        o.state AS "State",
        COUNT(DISTINCT o.order_id) AS "Total Orders"
    FROM superstore.orders o
    GROUP BY
        o.state
    ORDER BY
        "Total Orders" DESC;
    """

    orders_state_df = db_utils.run_pg_query(
        orders_state_query
    )


    # --------------------------------------------------------
    # ORDERS BY CUSTOMER
    # --------------------------------------------------------

    orders_customer_query = """
    SELECT
        c.customer_name AS "Customer Name",
        COUNT(DISTINCT o.order_id) AS "Total Orders"
    FROM superstore.orders o
    JOIN superstore.customers c
        ON o.customer_id = c.customer_id
    GROUP BY
        c.customer_name
    ORDER BY
        "Total Orders" DESC
    LIMIT 10;
    """

    orders_customer_df = db_utils.run_pg_query(
        orders_customer_query
    )


    # --------------------------------------------------------
    # STATE PERFORMANCE
    # --------------------------------------------------------

    state_query = """
    SELECT
        o.state,
        SUM(i.sales) AS revenue,
        SUM(i.profit) AS profit,
        ROUND(
            SUM(i.profit) /
            NULLIF(SUM(i.sales), 0) * 100,
            2
        ) AS profit_margin
    FROM superstore.orders o
    JOIN superstore.order_items i
        ON o.order_id = i.order_id
    GROUP BY
        o.state
    ORDER BY
        profit DESC;
    """

    state_df = db_utils.run_pg_query(state_query)


    return (
        kpi_df,
        monthly_df,
        category_df,
        furniture_df,
        top_revenue_customers_df,
        top_profit_customers_df,
        customer_loss_df,
        orders_category_df,
        orders_region_df,
        orders_state_df,
        orders_customer_df,
        state_df
    )


# ============================================================
# 5. LOAD ALL DATA
# ============================================================

(
    kpi_df,
    monthly_df,
    category_df,
    furniture_df,
    top_revenue_customers_df,
    top_profit_customers_df,
    customer_loss_df,
    orders_category_df,
    orders_region_df,
    orders_state_df,
    orders_customer_df,
    state_df
) = load_data()


# ============================================================
# 6. SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 📊 Superstore Analytics"
    )

    st.markdown("---")

    page = st.radio(
        "Dashboard",
        [
            "Executive Overview",
            "Customer Analysis",
            "Geographic Analysis"
        ]
    )

    st.markdown("---")

    if st.button("🔄 Refresh Data"):

        st.cache_data.clear()

        st.rerun()


# ============================================================
# 7. DASHBOARD HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">'
    'SUPERSTORE EXECUTIVE BUSINESS PERFORMANCE DASHBOARD'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Executive overview of revenue, profitability, orders, customers, '
    'and geographic performance'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 8. KPI CARDS
# ============================================================

total_revenue = kpi_df.loc[0, "Total Revenue"]
total_profit = kpi_df.loc[0, "Total Profit"]
profit_margin = kpi_df.loc[0, "Profit Margin %"]
total_orders = kpi_df.loc[0, "Total Orders"]


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Revenue</div>
            <div class="kpi-value">${total_revenue:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Profit</div>
            <div class="kpi-value">${total_profit:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Profit Margin</div>
            <div class="kpi-value">{profit_margin:.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Orders</div>
            <div class="kpi-value">{total_orders:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 9. EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    st.markdown(
        '<div class="section-title">Business Performance</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # MONTHLY REVENUE VS PROFIT
    # --------------------------------------------------------

    with col1:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=monthly_df["month"],
                y=monthly_df["revenue"],
                mode="lines+markers",
                name="Revenue",
                line={
                    "color": BLUE,
                    "width": 2.5
                }
            )
        )

        fig.add_trace(
            go.Scatter(
                x=monthly_df["month"],
                y=monthly_df["profit"],
                mode="lines+markers",
                name="Profit",
                line={
                    "color": GREEN,
                    "width": 2.5
                }
            )
        )

        fig.update_layout(
            title="Monthly Revenue vs Profit",
            template="plotly_white",
            height=450,
            hovermode="x unified",
            legend=dict(
                orientation="h",
                y=1.08
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # PROFIT BY CATEGORY
    # --------------------------------------------------------

    with col2:

        category_colors = [
            GREEN if value >= 0 else RED
            for value in category_df["profit"]
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=category_df["category"],
                y=category_df["profit"],
                text=category_df["profit"],
                texttemplate="$%{text:,.0f}",
                textposition="outside",
                marker_color=category_colors
            )
        )

        fig.update_layout(
            title="Profit by Category",
            template="plotly_white",
            height=450,
            yaxis_title="Profit ($)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # ORDERS BY CATEGORY
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=orders_category_df["Category"],
                y=orders_category_df["Total Orders"],
                text=orders_category_df["Total Orders"],
                texttemplate="%{text:,}",
                textposition="outside",
                marker_color=BLUE
            )
        )

        fig.update_layout(
            title="Orders by Category",
            template="plotly_white",
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # FURNITURE
    # --------------------------------------------------------

    with col2:

        furniture_colors = [
            RED if value < 0 else GREEN
            for value in furniture_df["profit"]
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=furniture_df["sub_category"],
                y=furniture_df["profit"],
                text=furniture_df["profit"],
                texttemplate="$%{text:,.0f}",
                textposition="outside",
                marker_color=furniture_colors
            )
        )

        fig.update_layout(
            title="Furniture Profit by Sub-Category",
            template="plotly_white",
            height=420,
            yaxis_title="Profit ($)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# 10. CUSTOMER ANALYSIS
# ============================================================

elif page == "Customer Analysis":

    st.markdown(
        '<div class="section-title">Customer Performance</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # TOP REVENUE CUSTOMERS
    # --------------------------------------------------------

    with col1:

        df = top_revenue_customers_df.sort_values(
            "revenue",
            ascending=True
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df["revenue"],
                y=df["customer_name"],
                orientation="h",
                text=df["revenue"],
                texttemplate="$%{text:,.0f}",
                textposition="outside",
                marker_color=LIGHT_BLUE
            )
        )

        fig.update_layout(
            title="Top 10 Customers by Revenue",
            template="plotly_white",
            height=500,
            xaxis_title="Revenue ($)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # TOP PROFIT CUSTOMERS
    # --------------------------------------------------------

    with col2:

        df = top_profit_customers_df.sort_values(
            "profit",
            ascending=True
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df["profit"],
                y=df["customer_name"],
                orientation="h",
                text=df["profit"],
                texttemplate="$%{text:,.0f}",
                textposition="outside",
                marker_color=GREEN
            )
        )

        fig.update_layout(
            title="Top 10 Customers by Profit",
            template="plotly_white",
            height=500,
            xaxis_title="Profit ($)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # LOSS-MAKING CUSTOMERS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Customers Requiring Attention</div>',
        unsafe_allow_html=True
    )

    df = customer_loss_df.sort_values(
        "profit",
        ascending=True
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["profit"],
            y=df["customer_name"],
            orientation="h",
            text=df["profit"],
            texttemplate="$%{text:,.0f}",
            textposition="outside",
            marker_color=RED
        )
    )

    fig.update_layout(
        title="Top 10 Loss-Making Customers",
        template="plotly_white",
        height=550,
        xaxis_title="Profit ($)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # ORDERS BY CUSTOMER
    # --------------------------------------------------------

    df = orders_customer_df.sort_values(
        "Total Orders",
        ascending=True
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["Total Orders"],
            y=df["Customer Name"],
            orientation="h",
            text=df["Total Orders"],
            texttemplate="%{text:,}",
            textposition="outside",
            marker_color=ORANGE
        )
    )

    fig.update_layout(
        title="Top 10 Customers by Orders",
        template="plotly_white",
        height=550,
        xaxis_title="Total Orders"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# 11. GEOGRAPHIC ANALYSIS
# ============================================================

elif page == "Geographic Analysis":

    st.markdown(
        '<div class="section-title">Geographic Performance</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # ORDERS BY REGION
    # --------------------------------------------------------

    with col1:

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=orders_region_df["Region"],
                y=orders_region_df["Total Orders"],
                text=orders_region_df["Total Orders"],
                texttemplate="%{text:,}",
                textposition="outside",
                marker_color=ORANGE
            )
        )

        fig.update_layout(
            title="Orders by Region",
            template="plotly_white",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # TOP STATES BY ORDERS
    # --------------------------------------------------------

    with col2:

        df = orders_state_df.sort_values(
            "Total Orders",
            ascending=True
        ).tail(10)

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df["Total Orders"],
                y=df["State"],
                orientation="h",
                text=df["Total Orders"],
                texttemplate="%{text:,}",
                textposition="outside",
                marker_color=TEAL
            )
        )

        fig.update_layout(
            title="Top 10 States by Orders",
            template="plotly_white",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # STATE PROFITABILITY
    # --------------------------------------------------------

    sorted_states = state_df.sort_values(
        "profit",
        ascending=True
    )

    bottom_5 = sorted_states.head(5)

    top_5 = sorted_states.tail(5)

    state_plot = pd.concat(
        [bottom_5, top_5]
    ).drop_duplicates()


    state_plot = state_plot.sort_values(
        "profit",
        ascending=True
    )


    state_colors = [
        RED if value < 0 else GREEN
        for value in state_plot["profit"]
    ]


    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=state_plot["profit"],
            y=state_plot["state"],
            orientation="h",
            text=state_plot["profit"],
            texttemplate="$%{text:,.0f}",
            textposition="outside",
            marker_color=state_colors
        )
    )

    fig.update_layout(
        title="State Profitability — Top 5 & Bottom 5",
        template="plotly_white",
        height=650,
        xaxis_title="Profit ($)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# 12. FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Superstore Business Analytics Dashboard | "
    "Powered by PostgreSQL, Python, Pandas, Plotly and Streamlit"
)