import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from utils.cortex import (
    ask_analyst,
    extract_text,
    extract_sql
)

from utils.snowflake_client import run_query


st.set_page_config(
    page_title="Olist Analytics Assistant",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>

.main .block-container {
    max-width: 1200px;
    margin: 0 auto;
    padding-bottom: 6rem;
}

h1 {
    text-align: center;
}

div[data-testid="stCaptionContainer"] {
    text-align: center;
}

div[data-testid="stSegmentedControl"] {
    width: fit-content !important;
}

</style>
""", unsafe_allow_html=True)

center_col = st.columns([1, 3, 1])[1]

with center_col:

    st.title("Olist Marketplace Analytics Assistant")

    st.caption(
        "Powered by Snowflake Cortex Analyst, dbt, and Snowflake"
    )

    # Native horizontal centering alignment to prevent shifting/reloading visual bugs
    with st.container(horizontal_alignment="center"):
        page = st.segmented_control(
            "",
            ["💬 Chat", "📊 Dashboard"],
            default="💬 Chat",
            key="page_selector"
        )

# Cached query helper
@st.cache_data(ttl=3600, show_spinner=False)
def cached_query(sql):
    return run_query(sql)


PALETTE = ["#0B3D91", "#1B5FAE", "#2E7BC4", "#4B9FD4", "#7BC0E4", "#AEDCF0"]


def style_chart(fig, show_legend=False):
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="sans-serif", size=13, color="#333333"),
        showlegend=show_legend,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=340,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EDEDED", zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


# CHAT TAB
if page == "💬 Chat":

    st.sidebar.header("Quick Questions")

    sample_questions = [
        "Top 10 product categories by revenue",
        "Which seller states generate the most revenue?",
        "Which customer segment spends the most?",
        "What categories have the lowest review scores?",
        "Show the order funnel",
    ]

    # Initialize chat history early
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Use a dynamic key based on message count so it resets cleanly when cleared
    pill_key = f"quick_questions_{len(st.session_state.messages)}"
    selected_question = st.sidebar.pills(
        "",
        sample_questions,
        selection_mode="single",
        key=pill_key
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "Clear Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        if "last_processed_pill" in st.session_state:
            del st.session_state["last_processed_pill"]
        st.rerun()

    # 1. RENDER PAST HISTORY WITH ISOLATED WIDGET KEYS
    # Enumeration guarantees that historical charts get distinct, valid IDs
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sql" in message and message["sql"]:
                with st.expander("Generated SQL", expanded=False):
                    st.code(message["sql"], language="sql")
            if "df" in message and message["df"] is not None:
                st.subheader("Results")
                st.dataframe(message["df"], use_container_width=True)
                
                # Re-render auto-charts safely with a unique element key
                numeric_cols = message["df"].select_dtypes(include="number").columns
                if len(message["df"].columns) == 2 and len(numeric_cols) == 1 and len(message["df"]) > 0:
                    fig = px.bar(
                        message["df"], 
                        x=message["df"].columns[0], 
                        y=numeric_cols[0], 
                        title=message.get("query_text", "")
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"hist_chart_{idx}")

    # 2. SEPARATE CHAT INPUT FROM SIDEBAR PROCESSING
    typed_question = st.chat_input("Ask a business question...")

    active_question = None
    
    # Priority 1: User typed an explicit question
    if typed_question:
        active_question = typed_question
        # Stashing the currently highlighted pill into memory prevents it from auto-firing next rerun
        st.session_state.last_processed_pill = selected_question
            
    # Priority 2: User clicked a sidebar pill that hasn't been evaluated yet
    elif selected_question:
        if "last_processed_pill" not in st.session_state or st.session_state.last_processed_pill != selected_question:
            active_question = selected_question
            st.session_state.last_processed_pill = selected_question

    # 3. RUN BACKEND PIPELINE
    if active_question:
        st.session_state.messages.append({"role": "user", "content": active_question})
        with st.chat_message("user"):
            st.markdown(active_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_analyst(active_question)

            if response.status_code != 200:
                st.error(f"API Error: {response.status_code}")
                try:
                    st.json(response.json())
                except ValueError:
                    st.code(response.text or "No response body")
            else:
                response_json = response.json()
                answer = extract_text(response_json)
                sql = extract_sql(response_json)

                st.markdown(answer)

                df_results = None
                if sql:
                    with st.expander("Generated SQL"):
                        st.code(sql, language="sql")

                    try:
                        df_results = run_query(sql)
                        st.subheader("Results")
                        st.dataframe(df_results, use_container_width=True)

                        # Auto chart fresh execution turn
                        numeric_cols = df_results.select_dtypes(include="number").columns
                        if len(df_results.columns) == 2 and len(numeric_cols) == 1 and len(df_results) > 0:
                            fig = px.bar(df_results, x=df_results.columns[0], y=numeric_cols[0], title=active_question)
                            st.plotly_chart(fig, use_container_width=True, key=f"fresh_chart_{len(st.session_state.messages)}")

                    except Exception as e:
                        st.error(f"SQL Execution Error:\n{e}")

                # Save metadata bundle back to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sql": sql,
                    "df": df_results,
                    "query_text": active_question
                })
                
                st.rerun()


# DASHBOARD TAB
elif page == "📊 Dashboard":

    st.caption(
        "Static overview built directly from the dbt marts (no Cortex Analyst call)."
    )

    # KPI strip
    try:
        df_orders = cached_query(
            """
            SELECT SUM(TOTAL_PAYMENT) AS TOTAL_PAYMENT
            FROM FCT_ORDERS
            """
        )

        df_all_orders = cached_query(
            """
            SELECT TOTAL_ORDERS
            FROM MART_ORDER_FUNNEL
            WHERE STAGE = 'created'
            """
        )

        df_reviews = cached_query(
            """
            SELECT AVG(REVIEW_SCORE) AS AVG_REVIEW_SCORE
            FROM MART_ORDER_EXPERIENCE
            WHERE REVIEW_SCORE IS NOT NULL
            """
        )

        df_items = cached_query(
            """
            SELECT SUM(TOTAL_ITEMS) AS TOTAL_ITEMS
            FROM MART_CATEGORY_PERFORMANCE
            """
        )

        df_customers = cached_query(
            """
            SELECT
                COUNT(*) AS TOTAL_CUSTOMERS,
                AVG(AVG_ORDER_VALUE) AS AVG_ORDER_VALUE
            FROM MART_CUSTOMER_ANALYTICS
            """
        )

        with st.container(border=True):

            kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(
                [1.3, 1, 1, 1.2, 1, 1]
            )

            kpi1.metric("Total Payment", f"R$ {df_orders['TOTAL_PAYMENT'][0]/1e6:.2f}M")
            kpi2.metric("Total Orders", f"{df_all_orders['TOTAL_ORDERS'][0]/1e3:.2f}K")
            kpi3.metric("Total Items", f"{df_items['TOTAL_ITEMS'][0]/1e3:.2f}K")
            kpi4.metric("Avg Order Value", f"R$ {df_customers['AVG_ORDER_VALUE'][0]:.2f}")
            kpi5.metric("Total Customers", f"{df_customers['TOTAL_CUSTOMERS'][0]/1e3:.2f}K")
            kpi6.metric("Avg Review Score", f"{df_reviews['AVG_REVIEW_SCORE'][0]:.2f}")

    except Exception as e:
        st.error(f"Could not load KPI strip: {e}")

    st.write("")

    # Row 0: Top 10 cities by revenue

    with st.container(border=True):

        st.subheader("Top 10 Cities by Revenue")

        try:
            df_cities = cached_query(
                """
                SELECT CUSTOMER_CITY, SUM(TOTAL_SPENDS) AS TOTAL_REVENUE
                FROM MART_CUSTOMER_ANALYTICS
                GROUP BY CUSTOMER_CITY
                ORDER BY TOTAL_REVENUE DESC
                LIMIT 10
                """
            )

            fig_cities = px.bar(
                df_cities,
                x="TOTAL_REVENUE",
                y="CUSTOMER_CITY",
                orientation="h",
                color_discrete_sequence=[PALETTE[0]]
            )

            fig_cities.update_layout(
                yaxis={"categoryorder": "total ascending"}
            )

            st.plotly_chart(style_chart(fig_cities), use_container_width=True)

        except Exception as e:
            st.error(f"Could not load top cities: {e}")

    st.write("")

    # Row 0.5: Revenue over time

    with st.container(border=True):

        st.subheader("Revenue Over Time")

        try:
            df_timeseries = cached_query(
                """
                SELECT ORDER_MONTH, SUM(TOTAL_PAYMENT) AS TOTAL_REVENUE
                FROM MART_ORDER_EXPERIENCE
                GROUP BY ORDER_MONTH
                ORDER BY ORDER_MONTH
                """
            )

            fig_timeseries = px.area(
                df_timeseries,
                x="ORDER_MONTH",
                y="TOTAL_REVENUE",
                color_discrete_sequence=[PALETTE[1]]
            )

            fig_timeseries.update_traces(line_color=PALETTE[0])

            st.plotly_chart(style_chart(fig_timeseries), use_container_width=True)

        except Exception as e:
            st.error(f"Could not load revenue over time: {e}")

    st.write("")

    # Row 1: Revenue by category | Order funnel
    
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:

        with st.container(border=True):

            st.subheader("Top 10 Categories by Revenue")

            try:
                df_category = cached_query(
                    """
                    SELECT PRODUCT_CATEGORY, TOTAL_REVENUE
                    FROM MART_CATEGORY_PERFORMANCE
                    ORDER BY TOTAL_REVENUE DESC
                    LIMIT 10
                    """
                )

                fig_category = px.bar(
                    df_category,
                    x="TOTAL_REVENUE",
                    y="PRODUCT_CATEGORY",
                    orientation="h",
                    color_discrete_sequence=[PALETTE[0]]
                )

                fig_category.update_layout(
                    yaxis={"categoryorder": "total ascending"}
                )

                st.plotly_chart(style_chart(fig_category), use_container_width=True)

            except Exception as e:
                st.error(f"Could not load category revenue: {e}")

    with row1_col2:

        with st.container(border=True):

            st.subheader("Order Funnel")

            try:
                df_funnel = cached_query(
                    """
                    SELECT STAGE, TOTAL_ORDERS
                    FROM MART_ORDER_FUNNEL
                    ORDER BY TOTAL_ORDERS DESC
                    """
                )

                fig_funnel = px.funnel(
                    df_funnel,
                    x="TOTAL_ORDERS",
                    y="STAGE",
                    color_discrete_sequence=[PALETTE[2]]
                )

                st.plotly_chart(style_chart(fig_funnel), use_container_width=True)

            except Exception as e:
                st.error(f"Could not load order funnel: {e}")

    st.write("")

    # Row 2: Top sellers

    with st.container(border=True):

        st.subheader("Top 10 Seller Cities by Revenue")

        try:
            df_sellers = cached_query(
                """
                SELECT CITY, SUM(SELLER_REVENUE) AS TOTAL_REVENUE
                FROM MART_SELLER_PERFORMANCE
                GROUP BY CITY
                ORDER BY TOTAL_REVENUE DESC
                LIMIT 10
                """
            )

            fig_sellers = px.bar(
                df_sellers,
                x="TOTAL_REVENUE",
                y="CITY",
                orientation="h",
                color_discrete_sequence=[PALETTE[0]]
            )

            fig_sellers.update_layout(
                yaxis={"categoryorder": "total ascending"}
            )

            st.plotly_chart(style_chart(fig_sellers), use_container_width=True)

        except Exception as e:
            st.error(f"Could not load top sellers: {e}")

    st.write("")

    # Row 2.5: Review score distribution | Delivery time distribution

    row25_col1, row25_col2 = st.columns(2)

    with row25_col1:

        with st.container(border=True):

            st.subheader("Review Score Distribution")

            try:
                df_reviews_dist = cached_query(
                    """
                    SELECT REVIEW_SCORE
                    FROM MART_ORDER_EXPERIENCE
                    WHERE REVIEW_SCORE IS NOT NULL
                    """
                )

                fig_reviews = px.histogram(
                    df_reviews_dist,
                    x="REVIEW_SCORE",
                    nbins=10,
                    color_discrete_sequence=[PALETTE[1]]
                )

                st.plotly_chart(style_chart(fig_reviews), use_container_width=True)

            except Exception as e:
                st.error(f"Could not load review score distribution: {e}")

    with row25_col2:

        with st.container(border=True):

            st.subheader("Delivery Time Distribution")

            try:
                df_delivery = cached_query(
                    """
                    SELECT DELIVERY_TIME_DAYS
                    FROM MART_ORDER_EXPERIENCE
                    WHERE DELIVERY_TIME_DAYS IS NOT NULL
                    AND DELIVERY_TIME_DAYS <= 40
                    """
                )

                df_delivery["DELIVERY_BIN"] = (
                    np.floor(df_delivery["DELIVERY_TIME_DAYS"] / 2) * 2
                )

                fig = go.Figure()

                fig.add_histogram(
                    x=df_delivery["DELIVERY_BIN"],
                    xbins=dict(
                        start=0,
                        end=40,
                        size=2
                    ),
                    marker_color=PALETTE[1]
                )

                fig.update_layout(
                    xaxis_title="Delivery Time (Days)",
                    yaxis_title="Order Count",
                    bargap=0.05
                )

                st.plotly_chart(
                    style_chart(fig),
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"Could not load delivery time distribution: {e}")

    st.write("")

    # Row 3: Revenue by seller state

    with st.container(border=True):

        st.subheader("Revenue by Seller State")

        try:
            df_state = cached_query(
                """
                SELECT STATE, SUM(SELLER_REVENUE) AS TOTAL_REVENUE
                FROM MART_SELLER_PERFORMANCE
                GROUP BY STATE
                ORDER BY TOTAL_REVENUE DESC
                """
            )

            fig_state = px.bar(
                df_state,
                x="STATE",
                y="TOTAL_REVENUE",
                color_discrete_sequence=[PALETTE[0]]
            )

            st.plotly_chart(style_chart(fig_state), use_container_width=True)

        except Exception as e:
            st.error(f"Could not load seller state revenue: {e}")