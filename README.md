# Olist E-Commerce Analytics | 2016 - 2018
End-to-end analytics engineering project built using Snowflake, dbt, and Tableau to analyze e-commerce performance, delivery efficiency, and customer behavior.

---

## Project Overview

This project transforms raw e-commerce data into a clean analytical model and delivers business insights through interactive dashboards.

### Key Objectives:
- Analyze **revenue trends and growth**
- Evaluate **delivery performance and delays**
- Understand **customer and seller behavior**
- Identify **geographic revenue distribution across Brazil**

---

## Architecture

Raw Data → Snowflake → dbt Models → Tableau Dashboard

- **Snowflake**: Data warehouse  
- **dbt**: Data transformation and modeling  
- **Tableau**: Data visualization 

---

## Data Modelling (dbt)

The project follows a layered modeling approach:

### 🔹 Staging Layer (`stg_*`)
- Cleans and standardizes raw data

### 🔹 Intermediate Layer (`int_*`)
- Joins and enriches datasets  
- Examples:
  - `int_orders_enriched`
  - `int_products_enriched`
  - `int_payments_agg`

---

### 🔹 Fact Table

#### `fct_orders`
**Grain:** One row per order

**Key Columns:**
- `order_id`
- `customer_id`
- `purchased_at`
- `delivered_customer_at`

**Derived Metrics:**
- `delivery_time_days`
- `approval_delay_days`
- `is_delivered`
- `is_late_delivery`
- `payment_diff`
- `is_payment_mismatch`

---

### 🔹 Mart Layer (`mart_*`)
Business-ready aggregated tables:

- `mart_customer_analytics`
- `mart_product_performance`
- `mart_seller_performance`
- `mart_category_performance`
- `mart_order_funnel`

---

## 📊 Dashboard Overview

### 🔹 Executive KPIs
- **Total Revenue:** R$ 16.01M  
- **Total Orders:** 99.44K  
- **Average Order Value:** R$ 159.33  
- **Total Customers:** 96.48K  
- **Average Review Score:** 4.16  

---

### 🔹 Key Visualizations

- 📈 Revenue Trend (Monthly + Cumulative)
- 🏙️ Top Cities by Revenue
- 🧾 Revenue by Category
- 🗺️ Revenue by State (Brazil Map)
- 📦 Order Status Distribution
- ⭐ Review Score Distribution
- 🚚 Delivery Time Distribution
- 🏪 Top Seller Clusters

![Dashboard](assets/OlistDashboard.png)

---

## 🔍 Key Insights

- São Paulo generates **~4x more revenue** than Rio de Janeiro, indicating strong geographic concentration.
- Most deliveries occur within **5–15 days**, with a median around **~9 days**.
- A small percentage of orders show **extreme delivery delays**, forming a long-tail distribution.
- Late deliveries are a **key driver of lower review scores**.
- Ibatinga represents a **high-volume, low-price seller cluster**, while premium sellers operate at significantly higher price points.

---

## 📈 Key Metrics

- Total Revenue  
- Total Orders  
- Average Order Value (AOV)  
- Median Delivery Time  
- Late Delivery %  
- Payment Mismatch Rate  

---

## 🗺️ dbt DAG

![dbt DAG](assets/dbt-dag.png)

- Raw sources → staging → intermediate → fact → marts  
- Central fact table: `fct_orders`  
- Downstream marts power Tableau dashboards  

---

## ⚙️ Tech Stack

- **Snowflake** – Data Warehouse  
- **dbt** – Data Transformation  
- **Tableau** – Visualization  
- **SQL** – Data Modeling  

---
