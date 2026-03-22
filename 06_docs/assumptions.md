# Project Assumptions

This document defines the operational assumptions used to generate the synthetic dataset for the project **“Promotion Impact on Inventory & Fulfillment.”**

Because the dataset is simulated rather than sourced from real company systems, clearly defined assumptions are required to ensure the generated data reflects **plausible retail supply chain behavior**.

The assumptions below define the simulation environment, demand dynamics, promotion mechanics, and inventory management logic used during dataset generation.

---

## Simulation Environment

Simulation Period: **365 days**

The dataset represents one full year of retail activity.
A yearly simulation enables analysis of:

* multiple promotional cycles
* seasonal demand variation
* inventory replenishment patterns
* fulfillment workload fluctuations

All operational events (orders, promotions, inventory changes, and shipments) occur within this simulated timeline.

---

## Product Catalog

Total Products: **120**

Products are distributed across several retail categories to simulate a realistic assortment mix.

Example product categories:

* Electronics
* Home & Kitchen
* Apparel
* Beauty & Personal Care
* Sports & Outdoors
* Accessories

Each product is assigned:

* a base price
* a baseline demand profile
* a product category
* participation in promotional campaigns during the simulation period.

Product categories influence baseline demand levels and promotion frequency.

---

## Warehouse Network

Number of Warehouses: **3**

Warehouses simulate regional fulfillment centers responsible for storing inventory and processing shipments.

Example regional structure:

Warehouse 1 — North Region
Warehouse 2 — West Region
Warehouse 3 — South Region

Inventory is tracked at the **product–warehouse level**, allowing analysis of regional inventory imbalances and stockout risk.

Each warehouse is also assigned a **maximum daily fulfillment capacity**, which represents operational processing limits.

---

## Demand Behavior

Each product is assigned a baseline demand level ranging from **5 to 30 units per day**.

Demand variability is introduced using randomized distributions to simulate differences in product popularity.

Demand patterns include:

* product-level demand variation
* random daily fluctuations
* promotion-driven demand spikes

Demand during promotional campaigns increases significantly depending on discount depth, typically ranging between **2× and 4× baseline demand**.

---

## Promotion Behavior

Promotions represent marketing campaigns designed to stimulate demand.

Promotion duration:

**3 to 14 days**
Discount range:

**5% to 40%**
Promotion frequency per product:

**2 to 4 promotions per year**
Estimated total promotions simulated:

**500–800 campaigns**
Promotion intensity directly influences the magnitude of demand uplift during active promotion periods.
Promotions are distributed across the simulation timeline to represent typical retail campaign scheduling.

---

## Inventory Management Logic

Initial inventory levels are assigned for each **product–warehouse combination**.
Inventory levels decrease as orders are generated.
Replenishment is governed by a simple reorder policy:
Reorder Point = **25% of average inventory level**
When inventory falls below the reorder threshold, a replenishment order is triggered.

Supplier Lead Time:

**5 days**
Inventory replenishment occurs after the lead time period has elapsed.
If inventory reaches zero before replenishment arrives, **stockout conditions occur**.

---

## Order Generation

Orders are generated daily based on simulated demand.

Each order record includes:

* order_id
* order_date
* product_id
* warehouse_id
* quantity
* promotion_id (if a promotion is active)

Orders reflect demand behavior influenced by both baseline demand patterns and promotional activity.

---

## Fulfillment Logic

Orders are fulfilled by warehouses based on inventory availability and warehouse processing capacity.

If daily order volume exceeds a warehouse’s fulfillment capacity:

* shipment processing is delayed
* backlog accumulates
* fulfillment delay metrics can be measured

Shipment records include timestamps that allow calculation of fulfillment performance metrics.

---

## Expected Dataset Scale

The simulation is expected to generate datasets approximately within the following ranges:

Products: **~120 rows**
Warehouses: **3 rows**
Promotions: **500–800 rows**
Orders: **80,000 – 120,000 rows**
Inventory records: **40,000 – 60,000 rows**
Shipments: **similar scale to orders**

These volumes provide sufficient data density for meaningful SQL analysis and business intelligence reporting.

---

## Data Generation Objective

The synthetic dataset is designed to simulate realistic retail operational dynamics in order to analyze the relationship between **promotional demand spikes and supply chain performance**.

The dataset structure supports analysis of:

* demand lift during promotions
* demand volatility patterns
* inventory depletion behavior
* stockout probability
* warehouse fulfillment delays

---

## Limitations

Because the dataset is simulated:

* demand patterns are modeled rather than observed
* customer-level behavior is not explicitly represented
* supplier variability is simplified
* external factors (market trends, competitor actions) are not modeled

Despite these limitations, the dataset structure is sufficient to support meaningful analysis of **promotion-driven operational risk within retail supply chains.**
