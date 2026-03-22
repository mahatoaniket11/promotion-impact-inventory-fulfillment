# Project Charter

## Promotion Impact on Inventory & Fulfillment

---

## Project Overview

Promotional campaigns are widely used in retail to stimulate short-term demand and increase revenue. However, these campaigns can also introduce operational pressure across supply chain systems by generating sudden demand spikes that exceed available inventory or warehouse processing capacity.

When demand increases faster than operational systems can respond, organizations may experience stockouts, shipment delays, and reduced service levels.

This project analyzes how promotional campaigns influence demand patterns, inventory risk, and fulfillment performance within a simulated retail supply chain environment. The objective is to quantify the operational effects of promotion-driven demand spikes and identify insights that support better coordination between marketing campaigns and supply chain planning.

---

## Business Context

Retail organizations often operate with separate planning cycles for marketing activities and supply chain operations.

Marketing teams focus on increasing customer engagement and driving demand through promotional campaigns. At the same time, supply chain teams must ensure adequate inventory levels and fulfillment capacity to meet customer demand.

When these planning processes are not aligned, promotional campaigns can produce demand surges that disrupt operational stability.

Analyzing the relationship between promotions and operational metrics such as demand variability, stockouts, and fulfillment delays helps organizations better align promotional planning with inventory and operational capacity.

---

## Project Objectives

The project aims to evaluate how promotional activity affects operational performance within a retail supply chain environment.

Key objectives include:

* Quantify demand lift generated during promotional campaigns
* Measure changes in demand volatility during promotion periods
* Evaluate the relationship between promotions and stockout risk
* Assess fulfillment performance during high-demand promotional windows
* Generate operational insights supporting promotion-aware inventory planning

---

## Key Business Questions

The analysis focuses on answering the following operational questions:

* How significantly do promotions increase product demand relative to baseline levels?
* Do promotional campaigns increase demand volatility?
* Are products under promotion more likely to experience stockouts?
* How does warehouse fulfillment performance change during promotion periods?
* What operational practices could reduce supply chain disruption during promotional campaigns?

---

## Analytical Scope

The project analyzes promotion-driven operational dynamics within a simulated retail environment.

The analysis includes:

* demand patterns before, during, and after promotional campaigns
* inventory depletion behavior across warehouses
* identification of stockout events
* evaluation of warehouse fulfillment performance during demand spikes

The project focuses on **operational impact**, rather than optimizing marketing campaign design.

---

## Stakeholders

Insights from this analysis are relevant to several business functions.

**Marketing Teams**
Use demand insights to plan promotional campaigns that balance revenue generation with operational feasibility.

**Supply Chain Planning**
Use demand volatility and stockout analysis to improve inventory planning and safety stock strategies.

**Warehouse Operations**
Understand operational capacity risks during promotion-driven demand surges.

**Business Leadership**
Evaluate trade-offs between promotional revenue growth and operational stability.

---

## Success Metrics

Project success is evaluated using the following analytical metrics:

**Demand Lift**
Increase in product demand during promotion periods relative to baseline demand.

**Demand Volatility**
Variation in daily demand levels across promotional and non-promotional periods.

**Stockout Rate**
Frequency of stockout events occurring during promotional campaigns.

**Fulfillment Delay Rate**
Percentage of orders experiencing shipment delays due to operational capacity constraints.

**Inventory Turnover**
Rate at which inventory is depleted during periods of increased demand.

---

## Analytical Deliverables

The project produces the following analytical outputs:

* synthetic retail dataset representing promotions, demand, and inventory activity
* SQL-based data transformation and analytical queries
* exploratory analysis notebooks evaluating demand and inventory patterns
* operational metrics measuring promotion impact
* an interactive Power BI dashboard summarizing key insights
* documented analytical methodology and assumptions

These deliverables demonstrate an end-to-end analytics workflow commonly used within retail analytics teams.

---

## Project Constraints

The project uses a synthetically generated dataset designed to replicate realistic retail operations.

As a result:

* demand behavior is modeled rather than observed from real transactions
* customer-level purchasing behavior is not explicitly simulated
* supplier variability and disruptions are simplified

Despite these constraints, the dataset structure enables meaningful analysis of promotion-driven operational dynamics.

---

## Project Success Criteria

The project is considered successful if it:

* demonstrates measurable relationships between promotional campaigns and operational metrics
* identifies patterns in stockout risk and fulfillment performance during promotion periods
* produces actionable insights supporting promotion-aware inventory planning
* presents results through clear analytical outputs and business intelligence dashboards

---

## Relationship to Supporting Documentation

This charter provides the strategic framing for the project.

Additional project documentation includes:

Project Assumptions
→ `assumptions.md`

Analytical Methodology
→ `methodology.md`

Data Dictionary
→ `data_dictionary.md`

SQL Analysis
→ `02_sql/`

Power BI Dashboard
→ `04_dashboard/`

---

## Expected Outcome

The project demonstrates how promotional demand spikes affect inventory availability and fulfillment performance within a retail supply chain.

The analysis provides a structured example of how data analytics can support cross-functional decision-making between marketing teams and supply chain operations.
