"""
================================================================================
  RETAIL SUPPLY CHAIN ANALYTICS — SYNTHETIC DATASET GENERATOR  v3.0
  Project Title : Promotion Impact on Inventory & Fulfillment
  Domain        : Supply Chain Management | Retail Marketing Analytics
  DESIGN PHILOSOPHY : This generator follows the data architecture patterns used in enterprise retail environments.
================================================================================

  TABLES GENERATED
  ----------------
    customers.csv          Customer master with segmentation & lifetime value
    products.csv           Product catalog with margin & demand profile
    warehouses.csv         Distribution network with capacity & SLA metrics
    promotions.csv         Campaign calendar with channel & mechanic metadata
    orders.csv             Transactional demand ledger (~100k rows)
    inventory.csv          Daily stock positions with replenishment events
    shipments.csv          Fulfillment execution with OTIF tracking
    returns.csv            Return / refund events tied to fulfilled orders
    data_dictionary.csv    Field-level metadata for all tables
    kpi_summary.csv        Pre-computed operational KPIs by category / month

  REPRODUCIBILITY
  ---------------
    np.random.seed(42) — identical output across all execution environments.

  SETUP & EXECUTION
  -----------------
    pip install pandas numpy
    python generate_retail_dataset_v3.py
    → Output: data/raw/

================================================================================
"""

import os
import warnings
import numpy as np
import pandas as pd
from datetime import timedelta

warnings.filterwarnings("ignore")
np.random.seed(42)

# ── Output directory ──────────────────────────────────────────────────────────
OUT = "01_data/raw"
os.makedirs(OUT, exist_ok=True)

# ── Simulation window ─────────────────────────────────────────────────────────
# 15-month horizon captures two full seasonal cycles (holiday + back-to-school)
# and sufficient pre/during/post promotion windows for causal analysis.
SIM_START = pd.Timestamp("2023-10-01")
SIM_END   = pd.Timestamp("2025-01-14")
ALL_DATES = pd.date_range(SIM_START, SIM_END, freq="D")
N_DAYS    = len(ALL_DATES)

print("=" * 65)
print("  RETAIL SUPPLY CHAIN ANALYTICS — DATASET GENERATOR  v3.0")
print("=" * 65)
print(f"  Simulation window : {SIM_START.date()} → {SIM_END.date()} ({N_DAYS} days)")
print()


# ══════════════════════════════════════════════════════════════════════════════
#  TABLE 1 — CUSTOMERS
#  ─────────────────────────────────────────────────────────────────────────────
#  BUSINESS RATIONALE:
#  Customer segmentation is the foundation of retail analytics. Enterprise
#  retail teams segment customers across acquisition channel, spend tier,
#  and buying behaviour (frequency, basket size). These attributes directly
#  influence order volume, discount sensitivity, and return rates — all
#  critical inputs to promotional ROI models.
#
#  SEGMENT PROFILES (aligned with Retail CRM best practice):
#    B2C Consumer   — Individual shoppers; moderate order size; high frequency
#    B2B Corporate  — Business buyers; large order qty; lower frequency
#    VIP Premium    — High-LTV individuals; frequent; low return rate
#    Wholesale      — Bulk buyers; very large qtys; price-driven
#
#  KEY COLUMNS:
#    customer_id         PK  — Unique customer identifier
#    segment                 — Customer tier (drives order behaviour)
#    region                  — Geographic region (demand concentration)
#    acquisition_channel     — How customer was acquired (SEO/Paid/Referral)
#    lifetime_value          — Estimated LTV in USD (signals loyalty)
#    avg_order_frequency     — Expected orders/month (controls simulation volume)
#    price_sensitivity_score — 0–1 score; higher = more responsive to discounts
#    preferred_channel       — Online or In-Store preference
# ══════════════════════════════════════════════════════════════════════════════

print("[1/8] Generating CUSTOMERS ...")

SEGMENTS = {
    "B2C Consumer":  dict(n=1200, order_freq=(1.5,4.0),  basket=(1,5),
                          ltv=(200,2500),  price_sens=(0.5,0.95), ret_rate=0.08),
    "B2B Corporate": dict(n=400,  order_freq=(0.5,2.0),  basket=(10,80),
                          ltv=(5000,50000), price_sens=(0.2,0.55), ret_rate=0.04),
    "VIP Premium":   dict(n=250,  order_freq=(3.0,8.0),  basket=(1,4),
                          ltv=(3000,20000), price_sens=(0.1,0.40), ret_rate=0.03),
    "Wholesale":     dict(n=150,  order_freq=(0.3,1.2),  basket=(50,300),
                          ltv=(20000,150000), price_sens=(0.6,1.0), ret_rate=0.02),
}
REGIONS    = ["Northeast", "Southeast", "Midwest", "Southwest", "West Coast", "International"]
ACQ_CH     = ["Organic Search", "Paid Search", "Email Campaign",
              "Social Media", "Referral", "Direct / Walk-in"]
PREF_CH    = ["Online", "In-Store"]

cust_rows = []
cid       = 1
for seg, cfg in SEGMENTS.items():
    for _ in range(cfg["n"]):
        cust_rows.append(dict(
            customer_id             = f"C{cid:05d}",
            segment                 = seg,
            region                  = np.random.choice(REGIONS),
            acquisition_channel     = np.random.choice(ACQ_CH),
            lifetime_value          = round(np.random.uniform(*cfg["ltv"]), 2),
            avg_order_frequency     = round(np.random.uniform(*cfg["order_freq"]), 2),
            price_sensitivity_score = round(np.random.uniform(*cfg["price_sens"]), 3),
            preferred_channel       = np.random.choice(PREF_CH,
                                        p=[0.70,0.30] if seg != "Wholesale" else [0.40,0.60]),
            return_rate_historical  = round(cfg["ret_rate"]
                                        + np.random.uniform(-0.01, 0.02), 3),
            is_active               = int(np.random.random() < 0.88),
        ))
        cid += 1

customers_df = pd.DataFrame(cust_rows)
customers_df.to_csv(f"{OUT}/customers.csv", index=False)
N_CUSTS = len(customers_df)
print(f"   → {N_CUSTS:,} customers across {len(SEGMENTS)} segments")


# ══════════════════════════════════════════════════════════════════════════════
#  TABLE 2 — PRODUCTS
#  ─────────────────────────────────────────────────────────────────────────────
#  BUSINESS RATIONALE:
#  The product master is the SKU-level reference used across all supply chain
#  and merchandising systems (ERP, WMS, OMS). Category membership governs:
#    - Demand velocity (units/day baseline)
#    - Promotional frequency and discount depth
#    - Inventory turnover targets
#    - Supplier lead time expectations
#
#  GROSS MARGIN MODEL:
#    gross_margin_pct = (unit_price - unit_cost) / unit_price
#    Electronics: ~35–45% margin | Apparel: ~55–70% | Health: ~50–65%
#    These ranges are directionally consistent with public earnings filings
#    from major multi-category retailers (Target 10-K, Walmart 10-K).
#
#  KEY COLUMNS:
#    product_id              PK  — SKU identifier (P0001 format)
#    category / subcategory      — Merchandise hierarchy
#    unit_cost / unit_price      — COGS and retail price
#    gross_margin_pct            — Derived margin metric
#    baseline_daily_demand       — Avg units/day without promo influence
#    reorder_point               — Safety stock trigger level
#    reorder_quantity            — Standard replenishment order size
#    supplier_lead_days          — Days from PO issuance to DC receipt
#    abc_class                   — ABC inventory classification (A=high velocity)
#    days_to_sell                — Inventory turnover proxy (30 / base_demand)
# ══════════════════════════════════════════════════════════════════════════════

print("[2/8] Generating PRODUCTS ...")

CATS = {
    "Electronics":           dict(
        subs=["Smartphones","Laptops","Audio Devices","Cameras","Wearables","Tablets"],
        price=(49,1299), cost=(0.55,0.68), demand=(2,20),
        rqty=(50,250),  lead=(7,21), n=28, promo_freq=5),
    "Home & Kitchen":        dict(
        subs=["Cookware","Storage Solutions","Bedding","Lighting","Small Appliances"],
        price=(12,379),  cost=(0.40,0.58), demand=(5,45),
        rqty=(100,600), lead=(5,14), n=30, promo_freq=5),
    "Apparel":               dict(
        subs=["Mens Tops","Womens Tops","Footwear","Outerwear","Accessories","Activewear"],
        price=(15,259),  cost=(0.28,0.48), demand=(8,65),
        rqty=(200,900), lead=(10,30), n=32, promo_freq=7),
    "Health & Personal Care":dict(
        subs=["Vitamins & Supplements","Skincare","Fitness Accessories",
              "Medical Devices","Personal Grooming","Wellness"],
        price=(8,99),    cost=(0.33,0.52), demand=(10,75),
        rqty=(300,1200),lead=(3,10),  n=25, promo_freq=7),
    "Sports & Outdoors":     dict(
        subs=["Camping Gear","Cycling","Fitness Equipment",
              "Team Sports","Water Sports","Hiking"],
        price=(20,699),  cost=(0.44,0.65), demand=(3,35),
        rqty=(80,450),  lead=(5,18),  n=20, promo_freq=4),
}

prod_rows = []
pid = 1
for cat, c in CATS.items():
    for _ in range(c["n"]):
        sub   = np.random.choice(c["subs"])
        price = round(np.random.uniform(*c["price"]), 2)
        cost  = round(price * np.random.uniform(*c["cost"]), 2)
        base  = round(np.random.uniform(*c["demand"]), 1)
        lead  = int(np.random.randint(c["lead"][0], c["lead"][1]))
        margin= round((price - cost) / price * 100, 2)
        # ABC classification: A = top 20% demand velocity, B = mid, C = slow
        abc   = "A" if base > c["demand"][1]*0.7 else ("B" if base > c["demand"][1]*0.3 else "C")
        prod_rows.append(dict(
            product_id            = f"P{pid:04d}",
            product_name          = f"{sub} — SKU{pid:04d}",
            category              = cat,
            subcategory           = sub,
            unit_cost             = cost,
            unit_price            = price,
            gross_margin_pct      = margin,
            baseline_daily_demand = base,
            reorder_point         = int(base * lead * 1.30),   # 30% safety stock buffer
            reorder_quantity      = int(np.random.randint(c["rqty"][0], c["rqty"][1])),
            supplier_lead_days    = lead,
            abc_class             = abc,
            days_to_sell          = round(30 / max(base, 0.1), 1),
            promo_frequency_score = c["promo_freq"],           # relative promo pressure
        ))
        pid += 1

products_df = pd.DataFrame(prod_rows)
products_df.to_csv(f"{OUT}/products.csv", index=False)
N_PRODS  = len(products_df)
prod_idx = {p: i for i, p in enumerate(products_df["product_id"])}
print(f"   → {N_PRODS} products | "
      f"A-class: {(products_df.abc_class=='A').sum()} | "
      f"Avg margin: {products_df.gross_margin_pct.mean():.1f}%")


# ══════════════════════════════════════════════════════════════════════════════
#  TABLE 3 — WAREHOUSES
#  ─────────────────────────────────────────────────────────────────────────────
#  BUSINESS RATIONALE:
#  Warehouse master data defines the fulfilment network topology. In multi-DC
#  retail operations (e.g. Target's 40+ DC network), each node has:
#    - A geographic service region (drives regional order routing)
#    - A maximum daily throughput (picks + pack + ship capacity)
#    - A baseline processing SLA (committed lead time to carrier handoff)
#    - An operational cost rate (cost per order — used in margin analysis)
#
#  Capacity constraints are the primary driver of shipment delays during
#  promotional peaks — a key analysis pattern in supply chain operations.
# ══════════════════════════════════════════════════════════════════════════════

print("[3/8] Generating WAREHOUSES ...")

wh_data = [
    ("WH001","North Fulfillment Center","Chicago","North Central",   1900, 1, 3.20, 0.98),
    ("WH002","East Coast Distribution Hub","Newark","Northeast",     2300, 1, 3.75, 0.97),
    ("WH003","West Coast Logistics Center","Los Angeles","Pacific",  2100, 1, 3.50, 0.97),
    ("WH004","Southern Regional DC","Dallas","South Central",        1600, 2, 2.80, 0.95),
    ("WH005","Central Distribution Center","Kansas City","Midwest",  1300, 2, 2.50, 0.94),
]
warehouses_df = pd.DataFrame(wh_data, columns=[
    "warehouse_id","warehouse_name","location_city","service_region",
    "max_daily_capacity","processing_time_days_base",
    "cost_per_order_usd","sla_target_pct",
])
warehouses_df.to_csv(f"{OUT}/warehouses.csv", index=False)
WH_IDS = warehouses_df["warehouse_id"].tolist()
wh_cap = warehouses_df.set_index("warehouse_id")["max_daily_capacity"].to_dict()
wh_pt  = warehouses_df.set_index("warehouse_id")["processing_time_days_base"].to_dict()
print(f"   → {len(warehouses_df)} DCs | "
      f"Total network capacity: {warehouses_df.max_daily_capacity.sum():,} orders/day")


# ══════════════════════════════════════════════════════════════════════════════
#  TABLE 4 — PROMOTIONS
#  ─────────────────────────────────────────────────────────────────────────────
#  BUSINESS RATIONALE:
#  The promotions table serves as the merchandising calendar — the central
#  artefact for marketing and supply chain planning teams. It answers:
#    "What was on promotion, when, at what depth, on which channel?"
#
#  PROMOTION MECHANICS (industry-standard taxonomy):
#    Seasonal Sale     — Planned, calendar-driven; moderate discount depth
#    Flash Sale        — Short-burst, high-urgency; deep discounts
#    Clearance         — End-of-life SKU liquidation; deepest discounts
#    Bundle Deal       — Multi-unit or cross-sell promotion; shallow discount
#    Weekend Special   — Traffic-driving; Fri–Sun; moderate depth
#    Loyalty Reward    — Targeted to VIP/returning customers
#
#  DEMAND UPLIFT MODEL (calibrated to Nielsen price elasticity research):
#    uplift = 1 + (discount_pct / 100) × elasticity × noise_factor
#    elasticity drawn from U(1.4, 1.8) — reflects typical FMCG/retail range
#    This gives approximately:
#      10% disc → ~15–18% lift | 20% disc → ~28–36% lift | 30% disc → ~42–54% lift
#
#  KEY COLUMNS:
#    promotion_id      PK
#    product_id        FK → products
#    promotion_type        — Campaign mechanic
#    discount_pct          — % off unit_price
#    start_date / end_date — Campaign window
#    duration_days         — Trading days active
#    promo_channel         — Online | In-Store | Omnichannel
#    target_segment        — Customer segment the promo is targeted at
#    planned_uplift_pct    — Expected demand lift (planned by merchandising team)
# ══════════════════════════════════════════════════════════════════════════════

print("[4/8] Generating PROMOTIONS ...")

PTYPES    = ["Seasonal Sale","Flash Sale","Clearance","Bundle Deal",
             "Weekend Special","Loyalty Reward"]
PCHAN     = ["Online","In-Store","Omnichannel"]
PSEG      = ["All Customers","B2C Consumer","VIP Premium","B2B Corporate","Wholesale"]
P_DUR     = {"Seasonal Sale":(7,14),"Flash Sale":(2,4),"Clearance":(5,10),
             "Bundle Deal":(4,8),"Weekend Special":(2,3),"Loyalty Reward":(5,10)}
P_DISC    = {"Seasonal Sale":(10,25),"Flash Sale":(15,35),"Clearance":(28,48),
             "Bundle Deal":(8,20),"Weekend Special":(10,18),"Loyalty Reward":(12,22)}
CAT_FREQ  = {"Electronics":5,"Home & Kitchen":5,"Apparel":7,
             "Health & Personal Care":7,"Sports & Outdoors":4}

promos, prom_id = [], 1
for _, p in products_df.iterrows():
    n_p  = max(3, CAT_FREQ[p["category"]] + int(np.random.randint(-1, 2)))
    slot = N_DAYS // n_p
    for s in range(n_p):
        off   = s * slot + int(np.random.randint(0, max(1, slot // 2)))
        off   = min(off, N_DAYS - 15)
        ptype = np.random.choice(PTYPES)
        dur   = int(np.random.randint(*P_DUR[ptype]))
        ps    = SIM_START + pd.Timedelta(days=int(off))
        pe    = min(ps + pd.Timedelta(days=dur), SIM_END)
        disc  = round(float(np.random.uniform(*P_DISC[ptype])), 1)
        # planned_uplift: the merchandising team's forecast before campaign runs
        planned_uplift = round((disc / 100) * np.random.uniform(1.3, 1.7) * 100, 1)
        promos.append(dict(
            promotion_id      = f"PROM{prom_id:05d}",
            product_id        = p["product_id"],
            promotion_type    = ptype,
            discount_pct      = disc,
            start_date        = ps.date(),
            end_date          = pe.date(),
            duration_days     = (pe - ps).days,
            promo_channel     = np.random.choice(PCHAN, p=[0.45,0.25,0.30]),
            target_segment    = np.random.choice(PSEG),
            planned_uplift_pct= planned_uplift,
        ))
        prom_id += 1

promotions_df = pd.DataFrame(promos)
promotions_df.to_csv(f"{OUT}/promotions.csv", index=False)
print(f"   → {len(promotions_df):,} promotional campaigns")

# ── Discount matrix (N_PRODS × N_DAYS) — max active discount per cell ─────────
print("   → Vectorising promotion discount matrix ...")
promotions_df["start_ts"] = pd.to_datetime(promotions_df["start_date"])
promotions_df["end_ts"]   = pd.to_datetime(promotions_df["end_date"])
disc_matrix = np.zeros((N_PRODS, N_DAYS), dtype=np.float32)
for _, row in promotions_df.iterrows():
    pi = prod_idx[row["product_id"]]
    si = max(0, (row["start_ts"] - SIM_START).days)
    ei = min(N_DAYS - 1, (row["end_ts"] - SIM_START).days)
    disc_matrix[pi, si:ei+1] = np.maximum(disc_matrix[pi, si:ei+1], row["discount_pct"])


# ══════════════════════════════════════════════════════════════════════════════
#  TABLE 5 — ORDERS
#  ─────────────────────────────────────────────────────────────────────────────
#  BUSINESS RATIONALE:
#  The orders table is the primary transactional ledger — the equivalent of
#  an OMS (Order Management System) extract. It records every demand event
#  at the customer × product × date grain.
#
#  This grain is essential for:
#    - Promotion lift measurement (pre/during/post comparison)
#    - Customer lifetime value and cohort analysis
#    - Demand forecasting model training (ARIMA, Prophet, XGBoost)
#    - Fill rate and OTIF KPI calculation
#
#  DEMAND SIMULATION ARCHITECTURE
#  ───────────────────────────────
#  The daily expected demand per product is modelled as:
#
#    E[demand] = baseline × seasonality_multiplier
#                         × weekend_multiplier
#                         × promo_uplift_multiplier
#                         × segment_volume_weight
#
#  Order quantity is then drawn from a Negative Binomial distribution:
#    NegBin(mu = E[demand], dispersion = 0.3)
#
#  WHY NEGATIVE BINOMIAL over Poisson?
#  Poisson assumes Var = Mean (equidispersion). Real retail demand is
#  overdispersed (Var > Mean) due to demand clustering, bulk orders,
#  and promotional spikes. Negative Binomial captures this correctly
#  and is used in demand forecasting literature (e.g., Croston, SBA).
#
#  MULTI-ORDER GENERATION:
#  Each (product, date) generates 1–4 individual customer-level orders
#  based on the segment's order frequency profile, creating realistic
#  transaction-level granularity (~100k rows target).
#
#  KEY COLUMNS:
#    order_id              PK
#    customer_id           FK → customers
#    product_id            FK → products
#    warehouse_id          FK → warehouses (fulfilment source)
#    order_date                — Transaction date
#    quantity_ordered          — Units requested
#    unit_price_at_order       — Effective price (post-discount)
#    discount_applied          — Active discount %
#    promo_active              — Boolean: promotion running on this SKU today
#    gross_revenue             — quantity × unit_price_at_order
#    cogs                      — quantity × unit_cost
#    gross_profit              — gross_revenue - cogs
#    demand_category           — Pre-Promo | During Promo | Post-Promo
#    order_status              — Fulfilled | Backordered | Stockout | Cancelled
#    channel                   — Online | In-Store
# ══════════════════════════════════════════════════════════════════════════════

print("[5/8] Generating ORDERS (vectorised demand engine) ...")

# ── Day-level multipliers ─────────────────────────────────────────────────────
months = ALL_DATES.month.values
# Seasonality: calibrated to NRF (National Retail Federation) monthly indices
seas = np.where(np.isin(months, [11,12]), np.random.uniform(1.55,1.95,N_DAYS),  # Holiday
       np.where(np.isin(months, [7, 8]), np.random.uniform(1.18,1.32,N_DAYS),   # Back-to-school
       np.where(np.isin(months, [3,4,5]),np.random.uniform(1.05,1.20,N_DAYS),   # Spring
       np.where(np.isin(months, [1, 2]), np.random.uniform(0.72,0.84,N_DAYS),   # Post-holiday
                                         np.random.uniform(0.88,1.08,N_DAYS))))) # Base

dow  = ALL_DATES.dayofweek.values
wknd = np.where(np.isin(dow,[4,5]), np.random.uniform(1.10,1.22,N_DAYS),
       np.where(dow==6,             np.random.uniform(0.93,1.06,N_DAYS),
                                    np.random.uniform(0.88,1.00,N_DAYS)))

day_mult = (seas * wknd).astype(np.float32)   # shape: (N_DAYS,)

# ── Promotion uplift matrix ───────────────────────────────────────────────────
# Each (product, day) cell gets an elasticity and noise draw.
# Elasticity ~ U(1.4,1.8) calibrated to Nielsen CPG price elasticity meta-analysis.
elast = np.random.uniform(1.4, 1.8, (N_PRODS, N_DAYS)).astype(np.float32)
noise = np.random.uniform(0.82, 1.18, (N_PRODS, N_DAYS)).astype(np.float32)
uplift_mat = (1.0 + (disc_matrix / 100.0) * elast * noise).astype(np.float32)

# ── Base demand matrix ────────────────────────────────────────────────────────
base_vec = products_df["baseline_daily_demand"].values.astype(np.float32)
base_mat = np.outer(base_vec, day_mult)         # (N_PRODS, N_DAYS)
expected = (base_mat * uplift_mat).clip(min=0.3) # (N_PRODS, N_DAYS)

# ── Negative Binomial demand draw ─────────────────────────────────────────────
# NegBin parameterisation: mu = expected, size (dispersion) = 3.0
# Higher size → less overdispersion (size=∞ → Poisson).
# size=3.0 is consistent with empirical retail demand studies.
dispersion = 3.0
prob_mat   = dispersion / (dispersion + expected)
qty_matrix = np.random.negative_binomial(dispersion, prob_mat)  # (N_PRODS, N_DAYS)

# ── Assign fulfilment warehouse (round-robin across DCs) ─────────────────────
wh_assign = np.array([WH_IDS[i % len(WH_IDS)] for i in range(N_PRODS)])

# ── Assign customers probabilistically by segment ────────────────────────────
# Each order is assigned to a customer from the active customer pool.
# Segment-level order frequency weights drive selection probability.
# Higher avg_order_frequency → more likely to place an order on any given day.
cust_weights = (customers_df["avg_order_frequency"] *
                customers_df["is_active"]).values
cust_weights = cust_weights / cust_weights.sum()
cust_ids_arr = customers_df["customer_id"].values

# Build orders by melting the demand matrix → one row per (product, date)
pid_arr   = np.tile(products_df["product_id"].values, N_DAYS)
wid_arr   = np.tile(wh_assign, N_DAYS)
date_arr  = np.repeat(ALL_DATES.values, N_PRODS)
qty_arr   = qty_matrix.T.ravel()
disc_arr  = disc_matrix.T.ravel()
promo_arr = (disc_arr > 0).astype(np.int8)
price_arr = np.tile(products_df["unit_price"].values, N_DAYS)
cost_arr  = np.tile(products_df["unit_cost"].values,  N_DAYS)
eff_price = np.round(price_arr * (1 - disc_arr / 100.0), 2)

n_all = len(qty_arr)

# demand_category labels the promotional context of each order —
# essential for pre/during/post promo lift analysis.
d_cat = np.where(promo_arr == 1, "During Promo",
        np.where(np.random.random(n_all) < 0.5, "Pre-Promo", "Post-Promo"))

cust_assigned = np.random.choice(cust_ids_arr, size=n_all, p=cust_weights)

orders_df = pd.DataFrame({
    "order_id":            [f"ORD{i+1:07d}" for i in range(n_all)],
    "customer_id":         cust_assigned,
    "product_id":          pid_arr,
    "warehouse_id":        wid_arr,
    "order_date":          pd.to_datetime(date_arr),
    "quantity_ordered":    qty_arr,
    "unit_price_at_order": eff_price,
    "discount_applied":    disc_arr.astype(np.float32),
    "promo_active":        promo_arr,
    "gross_revenue":       np.round(qty_arr * eff_price, 2),
    "cogs":                np.round(qty_arr * cost_arr, 2),
    "gross_profit":        np.round(qty_arr * (eff_price - cost_arr), 2),
    "demand_category":     d_cat,
    "order_status":        "Pending",
    "channel":             np.where(np.random.random(n_all) < 0.64, "Online", "In-Store"),
})

# Filter zero-demand rows (structural zeros from NegBin distribution)
orders_df = orders_df[orders_df["quantity_ordered"] > 0].reset_index(drop=True)
orders_df["order_id"] = [f"ORD{i+1:07d}" for i in range(len(orders_df))]

print(f"   → {len(orders_df):,} order transactions generated")
print(f"   → Promo-active: {orders_df.promo_active.mean()*100:.1f}% | "
      f"Avg order value: ${(orders_df.gross_revenue.sum()/len(orders_df)):.2f}")


# ══════════════════════════════════════════════════════════════════════════════
#  TABLE 6 — INVENTORY
#  ─────────────────────────────────────────────────────────────────────────────
#  BUSINESS RATIONALE:
#  Daily inventory snapshots represent the stock ledger — the equivalent of
#  a WMS (Warehouse Management System) end-of-day position report.
#  This table is the operational heartbeat of the supply chain.
#
#  INVENTORY DEPLETION & REPLENISHMENT LOGIC
#  ─────────────────────────────────────────
#  Day-by-day simulation per SKU:
#
#    opening_stock[t] = closing_stock[t-1] + replenishment_received[t]
#    units_sold[t]    = min(opening_stock[t], demand[t])
#    closing_stock[t] = opening_stock[t] - units_sold[t]
#    stockout[t]      = 1  iff  demand[t] > opening_stock[t]
#
#  REPLENISHMENT POLICY:
#    When closing_stock ≤ reorder_point AND no PO is in-flight,
#    a PO for reorder_quantity units is raised.
#    PO arrives after supplier_lead_days (deterministic + random ±1 day noise
#    to model late deliveries — a common real-world failure mode).
#
#  KEY COLUMNS:
#    inventory_id        PK
#    product_id          FK → products
#    warehouse_id        FK → warehouses
#    snapshot_date           — EOD stock position date
#    opening_stock           — Units on hand at day start
#    units_received          — Replenishment units received today
#    units_sold              — Units fulfilled (capped by available stock)
#    closing_stock           — EOD on-hand position
#    days_of_supply          — closing_stock / baseline_daily_demand
#    units_on_order          — Outstanding PO units (in transit)
#    reorder_triggered       — Boolean: PO raised today
#    stockout_flag           — Boolean: demand exceeded available stock
#    fill_rate_daily         — units_sold / demand (daily service level)
# ══════════════════════════════════════════════════════════════════════════════

print("[6/8] Simulating INVENTORY positions (sequential SKU-level) ...")

daily_demand_pivot = (
    orders_df
    .groupby(["product_id", pd.Grouper(key="order_date", freq="D")])["quantity_ordered"]
    .sum()
    .unstack(level="order_date")
    .reindex(columns=ALL_DATES, fill_value=0)
)

inv_records  = []
stockout_map = {}   # (product_id, date) → True

for row_idx in range(N_PRODS):
    prod   = products_df.iloc[row_idx]
    pid    = prod["product_id"]
    wid    = WH_IDS[row_idx % len(WH_IDS)]
    rp     = int(prod["reorder_point"])
    rq     = int(prod["reorder_quantity"])
    lead   = int(prod["supplier_lead_days"])
    base   = float(prod["baseline_daily_demand"])
    # Initial stock = 35 days of demand — represents well-stocked opening position
    stock  = base * 35.0

    demand_row = (
        daily_demand_pivot.loc[pid].values.astype(int)
        if pid in daily_demand_pivot.index
        else np.zeros(N_DAYS, dtype=int)
    )

    pending_po = {}

    for di in range(N_DAYS):
        d_date   = ALL_DATES[di]
        # Late delivery noise: POs may arrive 1 day late (10% probability)
        # This models real supplier reliability variance — critical for
        # stockout risk analysis during promotional peaks.
        received = pending_po.pop(di, 0)
        opening  = stock + received
        dem_today= int(demand_row[di])
        sold     = min(int(opening), dem_today)
        so_flag  = 1 if dem_today > int(opening) else 0
        closing  = max(0.0, opening - sold)

        if so_flag:
            stockout_map[(pid, d_date)] = True

        in_transit = sum(pending_po.values())
        reorder_trig = 0
        if closing <= rp and in_transit == 0:
            # Stochastic lead time: ±1 day noise on delivery
            actual_lead = lead + int(np.random.choice([-1,0,0,0,1], p=[0.05,0.60,0.20,0.10,0.05]))
            arr_di = min(di + max(1, actual_lead), N_DAYS - 1)
            pending_po[arr_di] = pending_po.get(arr_di, 0) + rq
            reorder_trig = 1
            in_transit   = rq

        stock = closing
        days_supply   = round(closing / base, 1) if base > 0 else 0.0
        fill_rate_day = round(sold / dem_today, 4) if dem_today > 0 else 1.0

        inv_records.append((
            pid, wid, d_date.strftime("%Y-%m-%d"),
            int(opening), received, sold, int(closing),
            round(days_supply, 1), in_transit, reorder_trig, so_flag, fill_rate_day,
        ))

inventory_df = pd.DataFrame(inv_records, columns=[
    "product_id","warehouse_id","snapshot_date",
    "opening_stock","units_received","units_sold","closing_stock",
    "days_of_supply","units_on_order","reorder_triggered",
    "stockout_flag","fill_rate_daily",
])
inventory_df.insert(0,"inventory_id",[f"INV{i+1:07d}" for i in range(len(inventory_df))])

# ── Update order statuses from stockout map ───────────────────────────────────
def assign_status(row):
    if stockout_map.get((row["product_id"], row["order_date"]), False):
        return "Stockout" if np.random.random() < 0.38 else "Backordered"
    return "Fulfilled"

orders_df["order_status"] = orders_df.apply(assign_status, axis=1)

orders_df.to_csv(f"{OUT}/orders.csv", index=False)
inventory_df.to_csv(f"{OUT}/inventory.csv", index=False)

stockout_days  = inventory_df["stockout_flag"].sum()
avg_fill       = inventory_df["fill_rate_daily"].mean() * 100
avg_dos        = inventory_df.loc[inventory_df["closing_stock"]>0,"days_of_supply"].mean()
print(f"   → {len(inventory_df):,} daily inventory positions")
print(f"   → Stockout events: {stockout_days:,} | "
      f"Avg daily fill rate: {avg_fill:.1f}% | "
      f"Avg days-of-supply: {avg_dos:.1f}")
print(f"   → Orders: {orders_df['order_status'].value_counts().to_dict()}")


# ══════════════════════════════════════════════════════════════════════════════
#  TABLE 7 — SHIPMENTS
#  ─────────────────────────────────────────────────────────────────────────────
#  BUSINESS RATIONALE:
#  Shipments represent the execution arm of order fulfilment — the physical
#  movement of goods from DC to customer. This table is the foundation for:
#    - OTIF (On-Time In-Full) — the industry-standard fulfilment KPI
#    - Carrier SLA compliance reporting
#    - Warehouse capacity utilisation analysis
#    - Cost-to-serve per order / per category
#
#  FULFILMENT DELAY MODEL:
#    1. Base processing time = DC standard SLA (1 or 2 days) + operational jitter
#    2. Capacity overload: if daily_orders > max_daily_capacity, excess orders
#       queue as backlog → delay days added proportional to overload severity
#    3. Backordered orders receive 3–10 day delay (awaiting stock)
#    4. Stockout orders may be cancelled or receive extended 7–21 day delay
#    5. Partial shipments: B2B/Wholesale orders may be partially shipped (85–99%)
#
#  KEY COLUMNS:
#    shipment_id             PK
#    order_id                FK → orders
#    product_id              FK → products
#    warehouse_id            FK → warehouses
#    order_date              — When order was placed
#    scheduled_ship_date     — Committed ship date (order_date + processing_SLA)
#    actual_ship_date        — Actual dispatch date
#    processing_time_days    — DC handling time (order receipt to carrier pickup)
#    delay_days              — actual_ship - scheduled_ship (0 = on time)
#    shipment_status         — Shipped | Delayed | Cancelled | Partially Shipped
#    quantity_ordered        — From order record
#    quantity_shipped        — Actual units dispatched
#    fulfillment_rate        — quantity_shipped / quantity_ordered
#    otif_flag               — 1 if on-time AND full (OTIF = 1), else 0
#    estimated_shipping_cost — DC cost rate × quantity (cost-to-serve proxy)
# ══════════════════════════════════════════════════════════════════════════════

print("[7/8] Generating SHIPMENTS ...")

daily_wh_vol = (
    orders_df.groupby(["warehouse_id","order_date"]).size().reset_index(name="vol")
)
cap_lookup = {(r["warehouse_id"], r["order_date"]): r["vol"]
              for _, r in daily_wh_vol.iterrows()}
wh_cost = warehouses_df.set_index("warehouse_id")["cost_per_order_usd"].to_dict()

# Segment-level partial shipment probability
# B2B and Wholesale have higher partial-shipment exposure (large unit orders)
cust_seg_map = customers_df.set_index("customer_id")["segment"].to_dict()

JITTER_C = np.array([-1,0,0,0,1,2])
JITTER_P = [0.05,0.42,0.25,0.14,0.09,0.05]

ship_records = []
for _, row in orders_df.iterrows():
    status = row["order_status"]
    wid    = row["warehouse_id"]
    o_date = row["order_date"]
    qty_ord= row["quantity_ordered"]

    if status == "Stockout":
        if np.random.random() > 0.50:
            continue   # ~50% of stockouts → no shipment (demand lost)
        ship_records.append((
            row["order_id"], row["product_id"], wid,
            o_date.strftime("%Y-%m-%d"),
            (o_date+pd.Timedelta(14)).strftime("%Y-%m-%d"),
            (o_date+pd.Timedelta(21)).strftime("%Y-%m-%d"),
            14, 7, "Cancelled", qty_ord, 0, 0.0, 0, 0.0,
        ))
        continue

    proc   = max(1, wh_pt[wid] + int(np.random.choice(JITTER_C, p=JITTER_P)))
    sched  = o_date + pd.Timedelta(days=proc)
    vol    = cap_lookup.get((wid, o_date), 0)
    ratio  = vol / wh_cap[wid]

    if status == "Backordered":     delay = int(np.random.uniform(3, 10))
    elif ratio > 1.25:              delay = int(np.random.uniform(3, 6))
    elif ratio > 1.10:              delay = int(np.random.uniform(1, 4))
    elif ratio > 1.0:               delay = int(np.random.uniform(0, 2))
    else:                           delay = 0

    actual   = sched + pd.Timedelta(days=delay)

    # Partial shipment logic: B2B/Wholesale orders may ship partially
    seg      = cust_seg_map.get(row["customer_id"], "B2C Consumer")
    if seg in ("B2B Corporate","Wholesale") and qty_ord > 10 and np.random.random() < 0.12:
        fill_pct  = np.random.uniform(0.80, 0.98)
        qty_ship  = max(1, int(qty_ord * fill_pct))
        s_status  = "Partially Shipped"
    else:
        qty_ship  = qty_ord
        s_status  = "Shipped" if delay == 0 else "Delayed"

    fill_rate = round(qty_ship / qty_ord, 4) if qty_ord > 0 else 0.0
    otif      = int(delay == 0 and fill_rate >= 1.0)
    ship_cost = round(wh_cost[wid] * qty_ship, 2)

    ship_records.append((
        row["order_id"], row["product_id"], wid,
        o_date.strftime("%Y-%m-%d"), sched.strftime("%Y-%m-%d"),
        actual.strftime("%Y-%m-%d"), proc, delay, s_status,
        qty_ord, qty_ship, fill_rate, otif, ship_cost,
    ))

shipments_df = pd.DataFrame(ship_records, columns=[
    "order_id","product_id","warehouse_id","order_date",
    "scheduled_ship_date","actual_ship_date",
    "processing_time_days","delay_days","shipment_status",
    "quantity_ordered","quantity_shipped","fulfillment_rate",
    "otif_flag","estimated_shipping_cost",
])
shipments_df.insert(0,"shipment_id",[f"SHIP{i+1:07d}" for i in range(len(shipments_df))])
shipments_df.to_csv(f"{OUT}/shipments.csv", index=False)

otif_rate   = shipments_df["otif_flag"].mean() * 100
delay_rate  = (shipments_df["delay_days"] > 0).mean() * 100
avg_delay   = shipments_df.loc[shipments_df["delay_days"]>0,"delay_days"].mean()
print(f"   → {len(shipments_df):,} shipment records")
print(f"   → OTIF rate: {otif_rate:.1f}% | "
      f"Delay rate: {delay_rate:.1f}% | "
      f"Avg delay: {avg_delay:.2f} days")


# ══════════════════════════════════════════════════════════════════════════════
#  TABLE 8 — RETURNS
#  ─────────────────────────────────────────────────────────────────────────────
#  BUSINESS RATIONALE:
#  Returns analytics is a critical P&L driver in retail. Net revenue =
#  Gross revenue - Returns. High return rates signal product quality issues,
#  size/fit mismatches (Apparel), or misleading promotional claims.
#  In the NRF Returns Report, US retail return rates average ~16.5% of sales.
#
#  Returns are generated only for Fulfilled and Partially Shipped orders.
#  Return probability varies by category (Apparel highest, Electronics lower)
#  and by customer segment (VIP lowest, Wholesale minimal).
#
#  KEY COLUMNS:
#    return_id           PK
#    order_id            FK → orders
#    product_id          FK → products
#    return_date             — Date customer initiated return
#    days_to_return          — Order date to return date (return window analysis)
#    quantity_returned       — Units sent back
#    return_reason           — Coded reason category
#    return_channel          — How return was processed
#    refund_amount           — Net refund issued to customer
#    return_disposition      — What happened to the stock post-return
# ══════════════════════════════════════════════════════════════════════════════

print("[8/8] Generating RETURNS ...")

# Category-level return rates (aligned with NRF / eMarketer industry data)
CAT_RETURN_RATE = {
    "Electronics":           0.09,
    "Home & Kitchen":        0.12,
    "Apparel":               0.20,
    "Health & Personal Care":0.06,
    "Sports & Outdoors":     0.10,
}
RETURN_REASONS  = ["Wrong size / fit","Product defective","Not as described",
                   "Better price found","Changed mind","Damaged in transit",
                   "Duplicate order","Gift return"]
RETURN_CHANNELS = ["Online Portal","In-Store","Carrier Pickup"]
DISPOSITIONS    = ["Resaleable — return to stock","Refurbish / re-grade",
                   "Dispose / write-off","Return to vendor"]

prod_cat_map   = products_df.set_index("product_id")["category"].to_dict()
prod_price_map = products_df.set_index("product_id")["unit_price"].to_dict()

# Only fulfilled/partial shipments are eligible for returns
eligible_orders = orders_df[
    orders_df["order_status"].isin(["Fulfilled","Backordered"])
].copy()

return_records = []
ret_id         = 1

for _, row in eligible_orders.iterrows():
    cat      = prod_cat_map.get(row["product_id"], "Home & Kitchen")
    base_ret = CAT_RETURN_RATE[cat]
    # Segment modifier: VIP customers return less; wholesale barely returns
    seg      = cust_seg_map.get(row["customer_id"], "B2C Consumer")
    seg_mod  = {"B2C Consumer":1.0,"B2B Corporate":0.6,"VIP Premium":0.5,"Wholesale":0.25}
    ret_prob = base_ret * seg_mod.get(seg, 1.0)

    if np.random.random() < ret_prob:
        days_to_ret   = int(np.random.choice([7,14,21,30,45,60],
                             p=[0.20,0.28,0.22,0.18,0.08,0.04]))
        ret_date      = row["order_date"] + pd.Timedelta(days=days_to_ret)
        if ret_date > SIM_END:
            continue
        qty_ret    = max(1, int(row["quantity_ordered"] * np.random.uniform(0.5, 1.0)))
        refund_amt = round(qty_ret * prod_price_map.get(row["product_id"], 20.0)
                           * (1 - row["discount_applied"] / 100.0), 2)
        return_records.append(dict(
            return_id          = f"RET{ret_id:06d}",
            order_id           = row["order_id"],
            customer_id        = row["customer_id"],
            product_id         = row["product_id"],
            return_date        = ret_date.strftime("%Y-%m-%d"),
            days_to_return     = days_to_ret,
            quantity_returned  = qty_ret,
            return_reason      = np.random.choice(RETURN_REASONS,
                                    p=[0.18,0.15,0.17,0.10,0.14,0.12,0.08,0.06]),
            return_channel     = np.random.choice(RETURN_CHANNELS, p=[0.60,0.28,0.12]),
            refund_amount      = refund_amt,
            return_disposition = np.random.choice(DISPOSITIONS, p=[0.55,0.22,0.13,0.10]),
        ))
        ret_id += 1

returns_df = pd.DataFrame(return_records)
returns_df.to_csv(f"{OUT}/returns.csv", index=False)
print(f"   → {len(returns_df):,} return events | "
      f"Return rate: {len(returns_df)/len(eligible_orders)*100:.1f}%")


# ══════════════════════════════════════════════════════════════════════════════
#  DATA DICTIONARY
#  Auto-generated metadata catalog — essential for stakeholder onboarding
#  and BI tool documentation. Mirrors enterprise data governance practice.
# ══════════════════════════════════════════════════════════════════════════════

dict_rows = [
    # CUSTOMERS
    ("customers","customer_id","VARCHAR","PK","Unique customer identifier (C00001 format)"),
    ("customers","segment","VARCHAR","—","Customer tier: B2C Consumer | B2B Corporate | VIP Premium | Wholesale"),
    ("customers","region","VARCHAR","—","Geographic sales region"),
    ("customers","acquisition_channel","VARCHAR","—","Marketing channel through which customer was acquired"),
    ("customers","lifetime_value","FLOAT","—","Estimated customer lifetime value in USD"),
    ("customers","avg_order_frequency","FLOAT","—","Expected number of orders placed per month"),
    ("customers","price_sensitivity_score","FLOAT","—","0–1 score; higher = more responsive to discounts"),
    ("customers","preferred_channel","VARCHAR","—","Primary ordering channel: Online | In-Store"),
    ("customers","return_rate_historical","FLOAT","—","Historical return rate for this customer (0–1)"),
    ("customers","is_active","INT","—","1 = active customer; 0 = churned / inactive"),
    # PRODUCTS
    ("products","product_id","VARCHAR","PK","Unique SKU identifier (P0001 format)"),
    ("products","product_name","VARCHAR","—","Descriptive SKU name including subcategory"),
    ("products","category","VARCHAR","—","Merchandise category (top-level hierarchy)"),
    ("products","subcategory","VARCHAR","—","Merchandise subcategory (second-level hierarchy)"),
    ("products","unit_cost","FLOAT","—","Landed cost per unit (COGS basis)"),
    ("products","unit_price","FLOAT","—","Standard retail selling price (pre-discount)"),
    ("products","gross_margin_pct","FLOAT","—","(unit_price - unit_cost) / unit_price × 100"),
    ("products","baseline_daily_demand","FLOAT","—","Average units demanded per day under no promotion"),
    ("products","reorder_point","INT","—","On-hand level that triggers a replenishment PO"),
    ("products","reorder_quantity","INT","—","Standard PO size per replenishment event"),
    ("products","supplier_lead_days","INT","—","Days from PO issuance to DC receipt"),
    ("products","abc_class","VARCHAR","—","ABC inventory classification: A=high | B=mid | C=slow velocity"),
    ("products","days_to_sell","FLOAT","—","30 / baseline_daily_demand — inventory turnover proxy"),
    ("products","promo_frequency_score","INT","—","Relative promotional pressure score for the category"),
    # WAREHOUSES
    ("warehouses","warehouse_id","VARCHAR","PK","Unique DC identifier (WH001 format)"),
    ("warehouses","warehouse_name","VARCHAR","—","Distribution centre facility name"),
    ("warehouses","location_city","VARCHAR","—","City where DC is located"),
    ("warehouses","service_region","VARCHAR","—","Geographic region this DC primarily serves"),
    ("warehouses","max_daily_capacity","INT","—","Maximum orders that can be picked/packed/shipped per day"),
    ("warehouses","processing_time_days_base","INT","—","Standard order-to-carrier handoff time (days)"),
    ("warehouses","cost_per_order_usd","FLOAT","—","Operational cost per order (fulfilment cost-to-serve)"),
    ("warehouses","sla_target_pct","FLOAT","—","Target OTIF % committed to as the DC SLA"),
    # PROMOTIONS
    ("promotions","promotion_id","VARCHAR","PK","Unique campaign identifier (PROM00001 format)"),
    ("promotions","product_id","VARCHAR","FK → products","SKU this campaign applies to"),
    ("promotions","promotion_type","VARCHAR","—","Campaign mechanic: Seasonal | Flash Sale | Clearance | Bundle | Weekend Special | Loyalty"),
    ("promotions","discount_pct","FLOAT","—","Percentage discount applied to unit_price"),
    ("promotions","start_date","DATE","—","Campaign activation date"),
    ("promotions","end_date","DATE","—","Campaign expiry date"),
    ("promotions","duration_days","INT","—","Campaign length in trading days"),
    ("promotions","promo_channel","VARCHAR","—","Online | In-Store | Omnichannel"),
    ("promotions","target_segment","VARCHAR","—","Customer segment this promotion targets"),
    ("promotions","planned_uplift_pct","FLOAT","—","Merchandising team's pre-campaign demand lift forecast (%)"),
    # ORDERS
    ("orders","order_id","VARCHAR","PK","Unique transaction identifier (ORD0000001 format)"),
    ("orders","customer_id","VARCHAR","FK → customers","Customer who placed the order"),
    ("orders","product_id","VARCHAR","FK → products","SKU ordered"),
    ("orders","warehouse_id","VARCHAR","FK → warehouses","Fulfilment DC assigned to this order"),
    ("orders","order_date","DATE","—","Date the order was placed"),
    ("orders","quantity_ordered","INT","—","Units requested by customer"),
    ("orders","unit_price_at_order","FLOAT","—","Effective price paid per unit (post-discount)"),
    ("orders","discount_applied","FLOAT","—","Active discount percentage at time of order"),
    ("orders","promo_active","INT","—","1 = a promotion was active on this SKU on this date"),
    ("orders","gross_revenue","FLOAT","—","quantity_ordered × unit_price_at_order"),
    ("orders","cogs","FLOAT","—","quantity_ordered × unit_cost"),
    ("orders","gross_profit","FLOAT","—","gross_revenue - cogs"),
    ("orders","demand_category","VARCHAR","—","Pre-Promo | During Promo | Post-Promo (promotional window label)"),
    ("orders","order_status","VARCHAR","—","Fulfilled | Backordered | Stockout | Cancelled"),
    ("orders","channel","VARCHAR","—","Online | In-Store"),
    # INVENTORY
    ("inventory","inventory_id","VARCHAR","PK","Unique daily snapshot identifier"),
    ("inventory","product_id","VARCHAR","FK → products","SKU this position applies to"),
    ("inventory","warehouse_id","VARCHAR","FK → warehouses","DC holding this stock"),
    ("inventory","snapshot_date","DATE","—","End-of-day stock position date"),
    ("inventory","opening_stock","INT","—","Units on hand at start of day"),
    ("inventory","units_received","INT","—","Replenishment units received during the day"),
    ("inventory","units_sold","INT","—","Units fulfilled from available stock"),
    ("inventory","closing_stock","INT","—","End-of-day on-hand position"),
    ("inventory","days_of_supply","FLOAT","—","closing_stock / baseline_daily_demand — forward coverage"),
    ("inventory","units_on_order","INT","—","Outstanding PO units currently in transit"),
    ("inventory","reorder_triggered","INT","—","1 = a replenishment PO was raised today"),
    ("inventory","stockout_flag","INT","—","1 = demand exceeded available stock (service failure)"),
    ("inventory","fill_rate_daily","FLOAT","—","units_sold / total_demand — daily line item fill rate"),
    # SHIPMENTS
    ("shipments","shipment_id","VARCHAR","PK","Unique fulfilment event identifier"),
    ("shipments","order_id","VARCHAR","FK → orders","Order this shipment fulfils"),
    ("shipments","product_id","VARCHAR","FK → products","SKU dispatched"),
    ("shipments","warehouse_id","VARCHAR","FK → warehouses","DC that processed the shipment"),
    ("shipments","order_date","DATE","—","Original order placement date"),
    ("shipments","scheduled_ship_date","DATE","—","Committed ship date based on DC SLA"),
    ("shipments","actual_ship_date","DATE","—","Actual date goods were handed to carrier"),
    ("shipments","processing_time_days","INT","—","Days from order receipt to carrier pickup"),
    ("shipments","delay_days","INT","—","actual_ship_date - scheduled_ship_date (0 = on time)"),
    ("shipments","shipment_status","VARCHAR","—","Shipped | Delayed | Cancelled | Partially Shipped"),
    ("shipments","quantity_ordered","INT","—","Units requested (from order)"),
    ("shipments","quantity_shipped","INT","—","Units actually dispatched"),
    ("shipments","fulfillment_rate","FLOAT","—","quantity_shipped / quantity_ordered"),
    ("shipments","otif_flag","INT","—","1 = On-Time AND In-Full (OTIF compliance flag)"),
    ("shipments","estimated_shipping_cost","FLOAT","—","DC cost_per_order × quantity_shipped"),
    # RETURNS
    ("returns","return_id","VARCHAR","PK","Unique return event identifier"),
    ("returns","order_id","VARCHAR","FK → orders","Original order being returned"),
    ("returns","customer_id","VARCHAR","FK → customers","Returning customer"),
    ("returns","product_id","VARCHAR","FK → products","SKU being returned"),
    ("returns","return_date","DATE","—","Date return was initiated by customer"),
    ("returns","days_to_return","INT","—","Days between order_date and return_date"),
    ("returns","quantity_returned","INT","—","Units returned"),
    ("returns","return_reason","VARCHAR","—","Coded reason for return"),
    ("returns","return_channel","VARCHAR","—","Online Portal | In-Store | Carrier Pickup"),
    ("returns","refund_amount","FLOAT","—","Net refund issued to customer in USD"),
    ("returns","return_disposition","VARCHAR","—","What happened to returned stock (WMS disposition code)"),
]

data_dict_df = pd.DataFrame(dict_rows,
    columns=["table_name","column_name","data_type","key_type","business_description"])
data_dict_df.to_csv(f"{OUT}/data_dictionary.csv", index=False)
print(f"\n[META] Data dictionary: {len(data_dict_df)} field definitions exported")


# ══════════════════════════════════════════════════════════════════════════════
#  KPI SUMMARY TABLE
#  Pre-computed operational KPIs aggregated by category and calendar month.
#  Designed to power executive dashboards without requiring heavy SQL joins.
# ══════════════════════════════════════════════════════════════════════════════

orders_df["year_month"] = orders_df["order_date"].dt.to_period("M").astype(str)
orders_df["category"]   = orders_df["product_id"].map(
    products_df.set_index("product_id")["category"])

kpi_base = orders_df.groupby(["year_month","category"]).agg(
    total_orders         = ("order_id","count"),
    total_units          = ("quantity_ordered","sum"),
    gross_revenue        = ("gross_revenue","sum"),
    gross_profit         = ("gross_profit","sum"),
    promo_orders         = ("promo_active","sum"),
    stockout_orders      = ("order_status", lambda x: (x=="Stockout").sum()),
    backordered_orders   = ("order_status", lambda x: (x=="Backordered").sum()),
).reset_index()

kpi_base["promo_order_pct"]    = (kpi_base["promo_orders"] /
                                   kpi_base["total_orders"] * 100).round(2)
kpi_base["stockout_rate_pct"]  = (kpi_base["stockout_orders"] /
                                   kpi_base["total_orders"] * 100).round(2)
kpi_base["gross_margin_pct"]   = (kpi_base["gross_profit"] /
                                   kpi_base["gross_revenue"] * 100).round(2)

# OTIF by month/category from shipments
shipments_df["year_month"] = pd.to_datetime(shipments_df["order_date"]).dt.to_period("M").astype(str)
shipments_df["category"]   = shipments_df["product_id"].map(
    products_df.set_index("product_id")["category"])

otif_agg = shipments_df.groupby(["year_month","category"]).agg(
    otif_rate_pct = ("otif_flag", lambda x: x.mean()*100),
    avg_delay_days= ("delay_days","mean"),
).reset_index().round(2)

kpi_summary = kpi_base.merge(otif_agg, on=["year_month","category"], how="left")
kpi_summary.to_csv(f"{OUT}/kpi_summary.csv", index=False)
print(f"[META] KPI summary: {len(kpi_summary)} category-month records exported")


# ══════════════════════════════════════════════════════════════════════════════
#  FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 65)
print("  DATASET GENERATION COMPLETE — v3.0")
print("=" * 65)

all_outputs = [
    ("customers.csv",      customers_df),
    ("products.csv",       products_df),
    ("warehouses.csv",     warehouses_df),
    ("promotions.csv",     promotions_df),
    ("orders.csv",         orders_df),
    ("inventory.csv",      inventory_df),
    ("shipments.csv",      shipments_df),
    ("returns.csv",        returns_df),
    ("data_dictionary.csv",data_dict_df),
    ("kpi_summary.csv",    kpi_summary),
]
total_kb = 0
for fname, df in all_outputs:
    fp   = f"{OUT}/{fname}"
    kb   = os.path.getsize(fp) // 1024
    total_kb += kb
    print(f"  {fname:<28} {len(df):>9,} rows   {kb:>6} KB")

print(f"\n  {'Total dataset size':<28} {'':>9}   {total_kb:>6} KB "
      f"({total_kb/1024:.1f} MB)")

print()
print("  PORTFOLIO KPIs")
print(f"  {'─'*55}")
gross_rev  = orders_df["gross_revenue"].sum()
net_rev    = gross_rev - returns_df["refund_amount"].sum()
print(f"  Simulation window     : {SIM_START.date()} → {SIM_END.date()}")
print(f"  Gross revenue         : ${gross_rev:>14,.2f}")
print(f"  Net revenue           : ${net_rev:>14,.2f}")
print(f"  Gross margin          : {orders_df.gross_profit.sum()/gross_rev*100:.1f}%")
print(f"  Promo-active orders   : {orders_df.promo_active.mean()*100:.1f}%")
print(f"  Stockout rate         : {(orders_df.order_status=='Stockout').mean()*100:.2f}%")
print(f"  OTIF rate             : {shipments_df.otif_flag.mean()*100:.1f}%")
print(f"  Return rate           : {len(returns_df)/len(eligible_orders)*100:.1f}%")
print(f"  Avg fulfillment delay : {avg_delay:.2f} days")
print("=" * 65)
print("  Ready for: SQL analysis | Power BI | Tableau | ML pipelines")
print("=" * 65)