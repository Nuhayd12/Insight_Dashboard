# Insight_Dashboard

Building a Streamlit Dashboard by following these steps below:

1.	Load Data: Load the provided tables into a Database Management System (DBMS) of your choosing (e.g., PostgreSQL, SQLite, Snowflake, etc.).
2.	Develop Dashboard: Utilize AI tools to create an interactive dashboard using Streamlit to visualize the data and using this dashboard, explore the data. (You are expected to use an AI assistant (e.g., Gemini, ChatGPT, Copilot) to help generate the Python code for your Streamlit dashboard).
3.	Document Prompts: Keep a clear, organized log of the prompts you use to interact with the AI during your development process.

# To maintain logs we create a log file

prompts.log - adds all the prompts asked by the user during the AI interaction process.

# Run the streamlit using this command:

-- streamlit run main.py

# Loading data done using sqlite3

Excel Data Set - "AI-Analyst-Data-Set.xlsx"

# Dashboard Summary: Online Order Cancellation Analysis

## Overview
This Streamlit dashboard provides a comprehensive analysis of order cancellations across 11 interactive visualizations. The dashboard helps identify **when**, **why**, **where**, and **what** is driving cancellations to enable data-driven decision making.

---

## Key Metrics & Formulas

### Primary KPIs
- **Cancellation Rate (Quantity)** = `Cancelled_Quantity ÷ Ordered_Quantity`
- **Cancellation Rate (Dollar)** = `Cancelled_Dollar_Amount ÷ Ordered_Dollar_Amount`
- **Financial Impact** = `Sum of Cancelled_Dollar_Amount`

---

## Visual Breakdown

### 1. High-Level Performance Indicators (KPIs)
**What it shows:** Four key metrics displayed as cards
- Total Ordered Quantity
- Total Cancelled Quantity  
- Overall Quantity Cancellation Rate
- Total Dollar Amount Cancelled

**Why important:** Provides immediate snapshot of business impact and scale of the cancellation problem.

---

### 2. Monthly Cancellation Rate Trend (Line Chart)
**What it shows:** Cancellation rate over time by month
**Formula:** `Monthly_Cancelled_Qty ÷ Monthly_Ordered_Qty`
**Why important:** Identifies seasonal patterns, trends, and whether the problem is getting better or worse over time.

---

### 3. Cancellation Rate by Day of Week (Bar Chart)
**What it shows:** Which days of the week have highest cancellation rates
**Formula:** `Day_Cancelled_Qty ÷ Day_Ordered_Qty`
**Why important:** Reveals operational patterns - maybe weekends have higher cancellation rates due to staffing or supply chain issues.

---

### 4. Cancelled Quantity by Cause and Department (Stacked Bar)
**What it shows:** Breakdown of cancellation reasons across different product departments
**Formula:** `Sum of Cancelled_Quantity` grouped by Cancel_Reason and Department
**Why important:** Identifies which departments have which types of problems (e.g., Grocery has more "Out of Stock" vs. Electronics has more "Customer Request").

---

### 5. Top 5 Cancel Reasons (Donut Chart)
**What it shows:** Percentage breakdown of the most common cancellation reasons
**Formula:** `(Reason_Cancelled_Qty ÷ Total_Cancelled_Qty) × 100`
**Why important:** Focuses attention on the biggest root causes - helps prioritize improvement efforts.

---

### 6. Top 10 Categories by Cancelled Dollar Amount (Horizontal Bar)
**What it shows:** Which product categories are losing the most money due to cancellations
**Formula:** `Sum of Cancelled_Dollar_Amount` by Product_Category
**Why important:** Prioritizes financial impact - focus on categories losing the most revenue first.

---

### 7. Cancellation Rate by Region (Horizontal Bar)
**What it shows:** Geographic performance - which regions have highest cancellation rates
**Formula:** `Region_Cancelled_Qty ÷ Region_Ordered_Qty`
**Why important:** Identifies geographic pain points - maybe certain regions have supply chain or operational issues.

---

### 8. Top 10 Brands by Cancel Volume (Horizontal Bar)
**What it shows:** Which brands are being cancelled most frequently
**Formula:** `Sum of Cancelled_Quantity` by Product_Brand
**Why important:** Identifies problematic suppliers or popular brands that need better inventory management.

---

### 9. Cancellation Frequency by Unit Cost (Histogram)
**What it shows:** Distribution of cancelled orders across different price ranges
**Formula:** Count of cancelled orders binned by `UNIT_COST`
**Why important:** Shows if expensive or cheap items are more likely to be cancelled - impacts inventory strategy.

---

### 10. State-Level Rate Drilldown (Data Table)
**What it shows:** Top 10 states with highest cancellation rates (minimum 500 orders)
**Formula:** `State_Cancelled_Qty ÷ State_Ordered_Qty`
**Why important:** Provides granular geographic insight for targeted interventions.

---

### 11. Inventory Risk Matrix (Bubble Chart)
**What it shows:** Categories plotted by cancellation rate (x-axis) vs. average unit cost (y-axis), with bubble size showing total cancelled volume
**Formulas:**
- X-axis: `Category_Cancelled_Qty ÷ Category_Ordered_Qty`
- Y-axis: `Average(UNIT_COST)` per category
- Bubble size: `Sum of Cancelled_Quantity`

**Why important:** **Most strategic visual** - identifies high-risk categories that are both expensive AND frequently cancelled. Top-right quadrant = highest priority for intervention.

---

## Dashboard Filters
Users can filter all visuals simultaneously by:
- **Date Range:** Focus on specific time periods
- **Region:** Analyze specific geographic areas  
- **Department:** Focus on specific product departments
- **Cancellation Reason:** Include/exclude specific cancel reasons

---

## Key Insights This Dashboard Reveals

1. **Temporal Patterns:** When do cancellations spike?
2. **Root Causes:** What are the main reasons for cancellations?
3. **Geographic Hotspots:** Where are the problem areas?
4. **Product Issues:** Which items/categories/brands are problematic?
5. **Financial Impact:** What's the dollar cost of cancellations?
6. **Strategic Priorities:** Which combinations of factors need immediate attention?

---

## Business Value
This dashboard enables stakeholders to:
- **Prioritize** improvement efforts based on financial impact
- **Identify** operational issues by geography and time
- **Monitor** progress over time with trend analysis  
- **Focus** on specific problem areas using interactive filters
- **Make data-driven decisions** rather than guessing at solutions

---

*Dashboard built using Streamlit, Altair visualizations, and SQLite database with 11 interconnected visuals providing 360° view of order cancellation challenges.*