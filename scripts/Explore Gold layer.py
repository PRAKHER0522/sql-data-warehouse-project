# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC ===============================================================================
# MAGIC DDL Script: Create Gold Views
# MAGIC ===============================================================================
# MAGIC Script Purpose:
# MAGIC     This script creates views for the Gold layer in the data warehouse. 
# MAGIC     The Gold layer represents the final dimension and fact tables (Star Schema)
# MAGIC
# MAGIC     Each view performs transformations and combines data from the Silver layer 
# MAGIC     to produce a clean, enriched, and business-ready dataset.
# MAGIC
# MAGIC Usage:
# MAGIC     - These views can be queried directly for analytics and reporting.
# MAGIC ===============================================================================
# MAGIC */

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC -- =============================================================================
# MAGIC -- Create Dimension: gold.dim_customers
# MAGIC -- =============================================================================

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC
# MAGIC CREATE or replace VIEW gold.dim_customers AS
# MAGIC SELECT
# MAGIC     ROW_NUMBER() OVER (ORDER BY cst_id) AS customer_key, -- Surrogate key
# MAGIC     ci.cst_id                          AS customer_id,
# MAGIC     ci.cst_key                         AS customer_number,
# MAGIC     ci.cst_firstname                   AS first_name,
# MAGIC     ci.cst_lastname                    AS last_name,
# MAGIC     la.cntry                           AS country,
# MAGIC     ci.cst_marital_status              AS marital_status,
# MAGIC     CASE 
# MAGIC         WHEN ci.cst_gndr != 'n/a' THEN ci.cst_gndr -- CRM is the primary source for gender
# MAGIC         ELSE COALESCE(ca.gen, 'n/a')  			   -- Fallback to ERP data
# MAGIC     END                                AS gender,
# MAGIC     ca.bdate                           AS birthdate,
# MAGIC     ci.cst_create_date                 AS create_date
# MAGIC FROM silver.crm_cust_info ci
# MAGIC LEFT JOIN silver.erp_cust_az12 ca
# MAGIC     ON ci.cst_key = ca.cid
# MAGIC LEFT JOIN silver.erp_loc_a101 la
# MAGIC     ON ci.cst_key = la.cid;

# COMMAND ----------

# MAGIC %md
# MAGIC -- =============================================================================
# MAGIC -- Create Dimension: gold.dim_products
# MAGIC -- =============================================================================

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC CREATe or replace VIEW gold.dim_products AS
# MAGIC SELECT
# MAGIC     ROW_NUMBER() OVER (ORDER BY pn.prd_start_dt, pn.prd_key) AS product_key, -- Surrogate key
# MAGIC     pn.prd_id       AS product_id,
# MAGIC     pn.prd_key      AS product_number,
# MAGIC     pn.prd_nm       AS product_name,
# MAGIC     pn.cat_id       AS category_id,
# MAGIC     pc.cat          AS category,
# MAGIC     pc.subcat       AS subcategory,
# MAGIC     pc.maintenance  AS maintenance,
# MAGIC     pn.prd_cost     AS cost,
# MAGIC     pn.prd_line     AS product_line,
# MAGIC     pn.prd_start_dt AS start_date
# MAGIC FROM silver.crm_prd_info pn
# MAGIC LEFT JOIN silver.erp_px_cat_g1v2 pc
# MAGIC     ON pn.cat_id = pc.id
# MAGIC WHERE pn.prd_end_dt IS NULL; -- Filter out all historical data

# COMMAND ----------

# MAGIC %md
# MAGIC -- =============================================================================
# MAGIC -- Create Fact Table: gold.fact_sales
# MAGIC -- =============================================================================

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC CREATE or replace VIEW gold.fact_sales AS
# MAGIC SELECT
# MAGIC     sd.sls_ord_num  AS order_number,
# MAGIC     pr.product_key  AS product_key,
# MAGIC     cu.customer_key AS customer_key,
# MAGIC     sd.sls_order_dt AS order_date,
# MAGIC     sd.sls_ship_dt  AS shipping_date,
# MAGIC     sd.sls_due_dt   AS due_date,
# MAGIC     sd.sls_sales    AS sales_amount,
# MAGIC     sd.sls_quantity AS quantity,
# MAGIC     sd.sls_price    AS price
# MAGIC FROM silver.crm_sales_details sd
# MAGIC LEFT JOIN gold.dim_products pr
# MAGIC     ON sd.sls_prd_key = pr.product_number
# MAGIC LEFT JOIN gold.dim_customers cu
# MAGIC     ON sd.sls_cust_id = cu.customer_id;
# MAGIC
# MAGIC
