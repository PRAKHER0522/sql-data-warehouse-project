-- Databricks notebook source
create schema IF NOT EXISTS bronze;

-- COMMAND ----------

create schema IF NOT EXISTS silver;

-- COMMAND ----------

create schema IF NOT EXISTS gold;

-- COMMAND ----------

CREATE TABLE if not EXISTS bronze.crm_cust_info (
    cst_id              INT,
    cst_key             VARCHAR(50),
    cst_firstname       VARCHAR(50),
    cst_lastname        VARCHAR(50),
    cst_marital_status  VARCHAR(50),
    cst_gndr            VARCHAR(50),
    cst_create_date     DATE
);
