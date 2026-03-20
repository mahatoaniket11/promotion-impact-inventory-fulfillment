# Promotion Impact on Inventory & Fulfillment

## Project Overview

This project analyzes how marketing promotions influence demand volatility,
inventory levels, and fulfillment performance in a retail supply chain.

Promotions often generate sudden demand spikes which can lead to stockouts,
inventory imbalances, and operational delays. This analysis investigates how
promotional campaigns affect these supply chain dynamics.

---

## Business Problem

Marketing promotions drive revenue but can disrupt supply chain operations.

Key operational risks include:

- Demand spikes exceeding available inventory
- Increased stockout probability
- Fulfillment delays due to rapid demand fluctuations

The goal of this project is to quantify these impacts and identify operational insights.

---

## Objectives

1. Analyze demand spikes caused by promotions
2. Identify inventory stockout risks
3. Measure fulfillment performance degradation
4. Generate insights for promotion planning and inventory management

---

## Analytical Framework

The project evaluates the causal relationship between promotions and supply chain performance.

---

## Key Business Metrics

- Promotion Lift %
- Demand Volatility
- Inventory Turnover
- Stockout Rate
- Fulfillment SLA Compliance

---

## Data Model

The project uses several key datasets.

### Orders

- order_id
- product_id
- order_date
- quantity
- promotion_id

### Inventory

- product_id
- warehouse_id
- inventory_level
- reorder_point

### Promotions

- promotion_id
- product_id
- discount_percent
- promotion_start
- promotion_end

---

## Analytical Workflow

Data Generation
↓
SQL Data Cleaning
↓
Demand Spike Analysis
↓
Inventory Risk Modeling
↓
Fulfillment Performance Analysis
↓
Power BI Dashboard
↓
Business Insights

---

## Tech Stack

Python  
SQL  
Power BI  
Pandas  

---

## Repository Structure

- 00_project_charter
- 01_data
- 02_sql
- 03_excel_model
- 04_analysis_notebooks
- 05_dashboard
- 06_docs
- 07_presentation
- src
- Readme_file

---

## Expected Insights

The analysis aims to uncover:

- how promotions influence demand variability
- the relationship between promotions and stockout risk
- operational impacts on fulfillment performance

These insights can help organizations better align marketing campaigns
with supply chain planning.

---

## Future Improvements

- Demand forecasting models
- Inventory optimization simulation
- Real-time promotion monitoring dashboards
