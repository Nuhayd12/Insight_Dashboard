import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
import numpy as np

st.set_page_config(layout="wide", page_title="Online Order Cancellation Analysis ")

# --- 1. Define the Master SQL Query (using corrected column names) ---
SQL_QUERY = """
SELECT
    -- ORDER DETAILS (O)
    O.ORDER_DT,
    O.STORE_NUM,
    O.ITEM_ID,
    O.PLCD_QTY,
    O.PLCD_AMT,
    
    -- CANCELLATION DETAILS (C)
    COALESCE(C.CNCL_QTY, 0) AS Cancelled_Quantity,
    COALESCE(C.CNCL_AMT, 0) AS Cancelled_dollar_amount,
    C.CANCEL_DT,
    COALESCE(C.CNCL_RSN_DESC, 'No Cancel') AS Cancel_reason,
    COALESCE(C.CNCL_RSN_SUB_DESC, 'N/A') AS Cancel_subreason,
    
    -- STORE DETAILS (S)
    S.Region AS Store_Region,
    S.State AS Store_State,
    S.City AS Store_City,

    -- PRODUCT DETAILS (P)
    P.PRODUCT_NAME,
    P.Department AS Product_Department,
    P.Category AS Product_Category,
    P.Brand AS Product_Brand,
    P.UNIT_COST,
    
    -- CALENDAR DETAILS (CAL)
    CAL."Week_#" AS Week_Number, 
    CAL.DayofWeek
    
FROM Orders AS O
LEFT JOIN Cancels AS C
    ON O.STORE_NUM = C.STORE_NUM
    AND O.ITEM_ID = C.ITEM_ID
    AND O.ORDER_DT = C.ORDER_DT
    
JOIN Store AS S
    ON O.STORE_NUM = S.STORE_NUM
    
JOIN Product AS P
    ON O.ITEM_ID = P.ITEM_ID
    
JOIN Calendar AS CAL
    ON O.ORDER_DT = CAL.Date;
"""

# --- 2. Data Loading Function with Caching and Type Fixes ---
@st.cache_data
def load_data():
    """
    Connects to SQLite, executes the query, returns the DataFrame, 
    and converts necessary columns to numeric types.
    """
    DB_FILE = 'retail_analysis.db'
    
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(SQL_QUERY, conn)
        conn.close()
        
        # --- Column Renaming and Type Conversion Fix ---
        df.rename(columns={'PLCD_QTY': 'Ordered_Quantity', 'PLCD_AMT': 'Ordered_dollar_amount'}, inplace=True)
        df.rename(columns={'CNCL_QTY': 'Cancelled_Quantity', 'CNCL_AMT': 'Cancelled_dollar_amount', 
                           'WEEK_NUM': 'Week_Number', 'CNCL_RSN_DESC': 'Cancel_reason', 
                           'CNCL_RSN_SUB_DESC': 'Cancel_subreason', 'REGION': 'Store_Region',
                           'STATE': 'Store_State', 'CITY': 'Store_City', 'DEPARTMENT': 'Product_Department',
                           'CATEGORY': 'Product_Category', 'BRAND': 'Product_Brand'}, inplace=True)


        # Convert quantity and dollar columns to numeric, coercing errors to NaN
        for col in ['Ordered_Quantity', 'Cancelled_Quantity', 'Ordered_dollar_amount', 'Cancelled_dollar_amount', 'UNIT_COST']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Drop rows where critical numeric values failed to convert
        df.dropna(subset=['Ordered_Quantity', 'Cancelled_Quantity'], inplace=True)
        
        # Ensure date columns are correct
        df['Order_DT'] = pd.to_datetime(df['ORDER_DT']) 
        df['CANCEL_DT'] = pd.to_datetime(df['CANCEL_DT'])
        
        # Calculate Key Metric: Cancellation Rate (handle ordered quantity of zero)
        df['Cancellation_Quantity_Rate_Item'] = df['Cancelled_Quantity'] / df.apply(
            lambda row: row['Ordered_Quantity'] if row['Ordered_Quantity'] != 0 else 1, axis=1
        )
        
        # Extract Month for Time Series
        df['Order_Month'] = df['Order_DT'].dt.to_period('M').astype(str)

        # Calculate CANCELLATION LAG TIME
        df['Cancellation_Lag_Days'] = (df['CANCEL_DT'] - df['Order_DT']).dt.days
        df['Cancellation_Lag_Days'] = df['Cancellation_Lag_Days'].apply(lambda x: x if x >= 0 else 0)
        
        return df
    except sqlite3.Error as e:
        st.error(f"Database Error: Could not load data from 'retail_analysis.db'. Please check the SQL query and the database file. Details: {e}")
        return pd.DataFrame() 

# Load the initial data
df_main = load_data()


# --- STREAMLIT APPLICATION START ---
st.title("🔥 AI Analyst: Comprehensive Order Cancellation Dashboard")
st.markdown("### Focus: Holistic View and Actionable Pain Points")

if df_main.empty:
    st.stop() 

# --- Sidebar Filters ---
st.sidebar.header("Filter Data")

# Date Range Filter
min_date = df_main['Order_DT'].min().date()
max_date = df_main['Order_DT'].max().date()

date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# Filter by Region
regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=df_main['Store_Region'].unique(),
    default=df_main['Store_Region'].unique()
)

# Filter by Department
departments = st.sidebar.multiselect(
    "Select Department(s)",
    options=df_main['Product_Department'].unique(),
    default=df_main['Product_Department'].unique()
)

# Filter by Cancel Reason
cancel_reasons = st.sidebar.multiselect(
    "Select Cancellation Reason(s)",
    options=df_main['Cancel_reason'].unique(),
    default=df_main['Cancel_reason'].unique()
)


# --- Apply Filters ---
df_filtered = df_main[
    (df_main['Store_Region'].isin(regions)) &
    (df_main['Product_Department'].isin(departments)) &
    (df_main['Cancel_reason'].isin(cancel_reasons)) &
    (df_main['Order_DT'].dt.date >= date_range[0]) &
    (df_main['Order_DT'].dt.date <= date_range[1])
].copy() 

# --- 3. Display Key Metrics (Visual 1) ---
st.subheader("1. High-Level Performance Indicators (KPIs)")
total_orders = df_filtered['Ordered_Quantity'].sum()
total_cancelled = df_filtered['Cancelled_Quantity'].sum()
total_sales_dollars = df_filtered['Ordered_dollar_amount'].sum()
total_cancelled_dollars = df_filtered['Cancelled_dollar_amount'].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Ordered Qty", f"{total_orders:,.0f}")
col2.metric("Total Cancelled Qty", f"{total_cancelled:,.0f}")

if total_orders > 0:
    overall_rate = total_cancelled / total_orders
    col3.metric("Overall Qty Cancel Rate", f"{overall_rate:.2%}")
else:
    col3.metric("Overall Qty Cancel Rate", "N/A")

if total_sales_dollars > 0:
    overall_dollar_rate = total_cancelled_dollars / total_sales_dollars
    col4.metric("Total \$ Cancelled", f"${total_cancelled_dollars:,.0f}", delta=f"Rate: {overall_dollar_rate:.2%}", delta_color="inverse")
else:
    col4.metric("Total \$ Cancelled", "N/A")


#4. TIME-BASED ANALYSIS (Visuals 2, 3, 12)
st.markdown("---")
st.subheader("2. Time-Based Analysis: When and How Fast Are Failures Occurring?")
col_line, col_bar = st.columns(2)

with col_line:
    # --- VISUAL 2: Monthly Trend (Line Chart) ---
    st.markdown("##### 2. Cancellation Rate Trend Over Time")
    df_trend = df_filtered.groupby('Order_Month').agg(
        Ordered_Quantity=('Ordered_Quantity', 'sum'),
        Cancelled_Quantity=('Cancelled_Quantity', 'sum')
    ).reset_index()
    df_trend['Cancellation_Rate'] = df_trend['Cancelled_Quantity'] / df_trend['Ordered_Quantity'].replace(0, 1)

    chart_trend = alt.Chart(df_trend).mark_line(point=True).encode(
        x=alt.X('Order_Month', sort='ascending', title="Month"),
        y=alt.Y('Cancellation_Rate', title="Cancellation Rate", axis=alt.Axis(format='.2%')),
        tooltip=['Order_Month', alt.Tooltip('Cancellation_Rate', format='.2%'), alt.Tooltip('Cancelled_Quantity', format=',.0f')]
    ).properties(title="Monthly Cancellation Rate").interactive()
    st.altair_chart(chart_trend, use_container_width=True)

with col_bar:
    # --- VISUAL 3: Day of Week (Bar Chart) ---
    st.markdown("##### 3. Cancellation Rate by Day of Week")
    df_dow = df_filtered.groupby('DayofWeek').agg(
        Ordered_Quantity=('Ordered_Quantity', 'sum'),
        Cancelled_Quantity=('Cancelled_Quantity', 'sum')
    ).reset_index()
    df_dow['Cancellation_Rate'] = df_dow['Cancelled_Quantity'] / df_dow['Ordered_Quantity'].replace(0, 1)

    dow_order = ['1', '2', '3', '4', '5', '6', '7'] 
    
    chart_dow = alt.Chart(df_dow).mark_bar().encode(
        x=alt.X('DayofWeek', sort=dow_order, title="Day of Week (1=Sun)"),
        y=alt.Y('Cancellation_Rate', title="Cancellation Rate", axis=alt.Axis(format='.2%')),
        color=alt.Color('Cancellation_Rate', scale=alt.Scale(range='heatmap'), legend=None),
        tooltip=['DayofWeek', alt.Tooltip('Cancellation_Rate', format='.2%')]
    ).properties(title="Risk by Fulfillment Day").interactive()
    st.altair_chart(chart_dow, use_container_width=True)



# 5. ROOT CAUSE ANALYSIS (Visuals 4, 5) 
st.markdown("---")
st.subheader("3. Root Cause Analysis: What is the primary cause and its impact?")
col_stack, col_donut = st.columns(2)

with col_stack:
    # --- VISUAL 4 (Original): Stacked Bar Chart by Reason & Department ---
    st.markdown("##### 4. Cancelled Quantity Breakdown by Cause and Department")
    df_reasons = df_filtered.groupby(['Cancel_reason', 'Product_Department'])['Cancelled_Quantity'].sum().reset_index()

    chart_reasons = alt.Chart(df_reasons).mark_bar().encode(
        x=alt.X('Cancel_reason', title="Primary Cancel Reason"),
        y=alt.Y('Cancelled_Quantity', title="Total Cancelled Quantity"),
        color=alt.Color('Product_Department', title="Department"),
        tooltip=['Cancel_reason', 'Product_Department', alt.Tooltip('Cancelled_Quantity', format=',.0f')],
    ).properties(title="Cancelled Quantity Breakdown").interactive()
    st.altair_chart(chart_reasons, use_container_width=True)

with col_donut:
    # --- VISUAL 5: Donut Chart of Top 5 Reasons ---
    st.markdown("##### 5. Percentage Split of Top 5 Cancel Reasons")
    df_donut = df_filtered[df_filtered['Cancel_reason'] != 'No Cancel'].groupby('Cancel_reason')['Cancelled_Quantity'].sum().sort_values(ascending=False).head(5).reset_index()

    base = alt.Chart(df_donut).encode(
        theta=alt.Theta("Cancelled_Quantity", stack=True)
    ).properties(title="Top 5 Reasons (Quantity)").interactive()

    pie = base.mark_arc(outerRadius=120, innerRadius=80).encode(
        color=alt.Color("Cancel_reason", title="Cancel Reason"),
        order=alt.Order("Cancelled_Quantity", sort="descending"),
        tooltip=["Cancel_reason", alt.Tooltip("Cancelled_Quantity", format=",.0f"), alt.Tooltip("Cancelled_Quantity", aggregate="sum", title="Percentage", format=".1%")]
    )

    text = base.mark_text(radius=140).encode(
        text=alt.Text("Cancelled_Quantity", aggregate="sum", format=".1%"),
        order=alt.Order("Cancelled_Quantity", sort="descending"),
        color=alt.value("black")
    )

    chart_donut = pie #+ text
    st.altair_chart(chart_donut, use_container_width=True)

# --- 6. FINANCIAL & GEOGRAPHIC ANALYSIS (Visuals 6, 8) ---
st.markdown("---")
st.subheader("4. Financial & Geographic Pain Points: Prioritizing Losses")
col_financial, col_region = st.columns(2)

with col_financial:
    # --- VISUAL 6: NEW: Financial Loss Leader by Category ---
    st.markdown("##### 6. **NEW**: Top 10 Categories by Cancelled DOLLAR Amount")
    df_loss = df_filtered.groupby('Product_Category')['Cancelled_dollar_amount'].sum().sort_values(ascending=False).head(10).reset_index()

    chart_loss = alt.Chart(df_loss).mark_bar().encode(
        y=alt.Y('Product_Category', title="Product Category", sort='-x'),
        x=alt.X('Cancelled_dollar_amount', title="Total Cancelled Dollar Amount", axis=alt.Axis(format='$,.0f')),
        # FIX: Changed range='viridis' to range='heatmap'
        color=alt.Color('Cancelled_dollar_amount', scale=alt.Scale(range='heatmap'), legend=None), 
        tooltip=['Product_Category', alt.Tooltip('Cancelled_dollar_amount', format='$,.0f')]
    ).properties(title="Financial Loss by Category").interactive()
    st.altair_chart(chart_loss, use_container_width=True)

with col_region:
    # --- VISUAL 7 (Original): Bar Chart by Region Rate ---
    st.markdown("##### 7. Cancellation Rate by Region (Qty-based)")
    df_geo = df_filtered.groupby('Store_Region').agg(
        Ordered_Quantity=('Ordered_Quantity', 'sum'),
        Cancelled_Quantity=('Cancelled_Quantity', 'sum')
    ).reset_index()

    df_geo['Cancellation_Rate'] = df_geo['Cancelled_Quantity'] / df_geo['Ordered_Quantity'].replace(0, float('inf')) 
    df_geo_sorted = df_geo[df_geo['Ordered_Quantity'] > 0].sort_values('Cancellation_Rate', ascending=False)
    
    chart_geo = alt.Chart(df_geo_sorted).mark_bar().encode(
        y=alt.Y('Store_Region', title="Store Region", sort='-x'),
        x=alt.X('Cancellation_Rate', title="Cancellation Rate", axis=alt.Axis(format='.1%')),
        color=alt.Color('Cancellation_Rate', scale=alt.Scale(range='heatmap'), legend=None),
        tooltip=['Store_Region', alt.Tooltip('Cancellation_Rate', format='.2%'), alt.Tooltip('Cancelled_Quantity', format=',.0f')]
    ).properties(title="Regional Cancellation Rate").interactive()
    st.altair_chart(chart_geo, use_container_width=True)



# --- 8. INVENTORY AND PRODUCT IMPACT (Visuals 9, 10, 11, 12) ---
st.markdown("---")
st.subheader("5. Inventory and Product Impact: Item Failures & Risk")
col_brand, col_hist = st.columns(2)

with col_brand:
    # --- VISUAL 8 (Original): Top 10 Brands by Cancelled Quantity ---
    st.markdown("##### 8. Top 10 Brands Driving Cancel Volume")
    df_brand = df_filtered.groupby('Product_Brand').agg(
        Cancelled_Quantity=('Cancelled_Quantity', 'sum'),
        Ordered_Quantity=('Ordered_Quantity', 'sum')
    ).reset_index()

    df_brand_top10 = df_brand.sort_values('Cancelled_Quantity', ascending=False).head(10)

    chart_brand = alt.Chart(df_brand_top10).mark_bar().encode(
        x=alt.X('Cancelled_Quantity', title="Total Cancelled Quantity", axis=alt.Axis(format=',.0f')),
        y=alt.Y('Product_Brand', title="Product Brand", sort='-x'),
        tooltip=['Product_Brand', alt.Tooltip('Cancelled_Quantity', format=',.0f')]
    ).properties(title="Top 10 Brands by Cancel Volume").interactive()
    st.altair_chart(chart_brand, use_container_width=True)

with col_hist:
    # --- VISUAL 9: Cost Distribution Histogram ---
    st.markdown("##### 9. Cancellation Frequency by Unit Cost ($)")
    df_cost = df_filtered[df_filtered['Cancelled_Quantity'] > 0]
    
    chart_hist = alt.Chart(df_cost).mark_bar().encode(
        x=alt.X("UNIT_COST", bin=alt.Bin(maxbins=20), title="Unit Cost Bins"),
        y=alt.Y("count()", title="Count of Cancelled Orders"),
        color=alt.value("#63B8FF"),
        tooltip=["UNIT_COST", "count()"]
    ).properties(title="Where the Cancelled Orders Fall on Cost").interactive()
    st.altair_chart(chart_hist, use_container_width=True)


col_state, col_risk = st.columns(2)

with col_state:
    # --- VISUAL 10: State-Level Table (Simulated Heatmap/Drilldown) ---
    st.markdown("##### 10. State-Level Rate Drilldown (Top 10 States)")
    df_state = df_filtered.groupby('Store_State').agg(
        Ordered_Quantity=('Ordered_Quantity', 'sum'),
        Cancelled_Quantity=('Cancelled_Quantity', 'sum')
    ).reset_index()
    df_state['Cancellation_Rate'] = df_state['Cancelled_Quantity'] / df_state['Ordered_Quantity'].replace(0, float('inf'))
    df_state_top10 = df_state[df_state['Ordered_Quantity'] > 500].sort_values('Cancellation_Rate', ascending=False).head(10)
    
    st.dataframe(
        df_state_top10[['Store_State', 'Cancellation_Rate', 'Cancelled_Quantity']].rename(
            columns={'Store_State': 'State', 'Cancellation_Rate': 'Rate', 'Cancelled_Quantity': 'Qty'}
        ), 
        hide_index=True,
        column_config={
            "Rate": st.column_config.ProgressColumn(
                "Rate", format="%.2f%%", min_value=0, max_value=df_state_top10['Cancellation_Rate'].max()
            ),
            "Qty": st.column_config.NumberColumn("Qty", format="%d")
        },
        use_container_width=True
    )

with col_risk:
    # --- VISUAL 11 (Out-of-the-Box): Risk vs. Impact (Bubble Chart) ---
    st.markdown("##### 11. Inventory Risk Matrix: Category Rate vs. Financial Impact (Bubble Chart)")

    df_risk = df_filtered[df_filtered['Cancel_reason'] != 'No Cancel'].copy()

    df_risk_agg = df_risk.groupby('Product_Category').agg(
        Total_Ordered=('Ordered_Quantity', 'sum'),
        Total_Cancelled=('Cancelled_Quantity', 'sum'),
        Avg_Unit_Cost=('UNIT_COST', 'mean'), 
    ).reset_index()

    df_risk_agg['Cancellation_Rate'] = df_risk_agg['Total_Cancelled'] / df_risk_agg['Total_Ordered'].replace(0, float('inf'))
    df_risk_agg = df_risk_agg[df_risk_agg['Total_Ordered'] > 100] 

    if not df_risk_agg.empty:
        chart_risk = alt.Chart(df_risk_agg).mark_circle().encode(
            x=alt.X('Cancellation_Rate', title="Category Cancellation Rate (Qty)", axis=alt.Axis(format='.1%')),
            y=alt.Y('Avg_Unit_Cost', title="Average Unit Cost ($)", axis=alt.Axis(format='$.2f')),
            size=alt.Size('Total_Cancelled', title="Cancelled Volume (Qty)", scale=alt.Scale(range=[50, 1000])),
            color=alt.Color('Product_Category', title="Category"),
            tooltip=['Product_Category', alt.Tooltip('Cancellation_Rate', format='.2%'), alt.Tooltip('Avg_Unit_Cost', format='$.2f'), alt.Tooltip('Total_Cancelled', format=',.0f')]
        ).properties(
            title="Category Risk Matrix"
        ).interactive()
        
        st.altair_chart(chart_risk, use_container_width=True)
